import json
import re
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.services.llm_provider import get_llm_provider
from backend.app.database.database import get_db
from backend.app.models.database_models import Resume

router = APIRouter(tags=["Interview Preparation"])

TECHNICAL_REQUIRED = 5
BEHAVIORAL_REQUIRED = 3


class InterviewPrepRequest(BaseModel):
    resume_id: Optional[int] = None
    resume_data: Optional[Dict[str, Any]] = None
    jd_text: str = Field(min_length=10)
    matched_skills: Optional[List[str]] = Field(default_factory=list)
    missing_skills: Optional[List[str]] = Field(default_factory=list)
    target_role: Optional[str] = None


def parse_ai_json(result: str) -> dict:
    """Parse JSON returned by the AI provider with robust regex stripping."""
    if not isinstance(result, str):
        raise ValueError("Unexpected AI response type.")

    result = result.strip()
    result = re.sub(r"^```(?:json)?\s*|\s*```$", "", result, flags=re.IGNORECASE).strip()

    start = result.find("{")
    end = result.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("The AI did not return valid JSON.")

    data = json.loads(result[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError("The AI response must be a JSON object.")

    return data


def is_valid_question(item: Any) -> bool:
    """Check whether a question item has question, suggested_answer, and tips."""
    if not isinstance(item, dict):
        return False
    for field in ("question", "suggested_answer", "tips"):
        if not isinstance(item.get(field), str) or not item[field].strip():
            return False
    return True


def clean_questions(items: Any) -> List[Dict[str, str]]:
    """Clean and standardize question items."""
    if not isinstance(items, list):
        return []

    cleaned = []
    for item in items:
        if not isinstance(item, dict):
            continue

        # Convert list-based tips if returned as list
        tips = item.get("tips")
        if isinstance(tips, list):
            tips = " • ".join(str(t) for t in tips)
        elif not isinstance(tips, str):
            tips = str(tips or "Review relevant concepts and provide specific metrics.")

        q = {
            "question": str(item.get("question", "")).strip(),
            "suggested_answer": str(item.get("suggested_answer", "")).strip(),
            "tips": str(tips).strip(),
        }

        if is_valid_question(q):
            cleaned.append(q)

    return cleaned


def extract_candidate_summary(resume: dict) -> dict:
    """Extract a lightweight summary to minimize prompt tokens and maximize generation speed."""
    name = resume.get("name") or "Candidate"
    
    # Extract up to 12 top skills
    raw_skills = resume.get("skills", [])
    skills = [s for s in raw_skills if isinstance(s, str)][:12] if isinstance(raw_skills, list) else []

    # Extract up to 3 recent titles and companies
    raw_exp = resume.get("experience", [])
    exp_summary = []
    if isinstance(raw_exp, list):
        for e in raw_exp[:3]:
            if isinstance(e, dict):
                t = e.get("title", "").strip()
                c = e.get("company", "").strip()
                if t or c:
                    exp_summary.append(f"{t} at {c}".strip(" at"))

    # Extract degrees
    raw_edu = resume.get("education", [])
    edu_summary = []
    if isinstance(raw_edu, list):
        for ed in raw_edu[:2]:
            if isinstance(ed, dict) and ed.get("degree"):
                edu_summary.append(ed.get("degree"))

    return {
        "name": name,
        "skills": skills,
        "recent_roles": exp_summary,
        "education": edu_summary,
    }


def generate_fallback_questions(
    missing_technical_count: int,
    missing_behavioral_count: int,
    matched_skills: List[str],
    missing_skills: List[str],
    candidate_summary: dict,
    target_role: str,
) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Fast deterministic generator for missing questions to prevent slow retry loops."""
    fallback_tech = []
    probe_skills = (missing_skills or []) + (matched_skills or []) + (candidate_summary.get("skills") or ["System Design", "APIs", "Database Optimization"])

    tech_templates = [
        ("How do you architect and optimize applications using {skill} in a production environment?",
         "Discuss clean modular architecture, error handling, performance tuning, and how you ensure high availability.",
         "Focus on scalability trade-offs, caching, and maintainability."),
        ("What common pitfalls have you encountered when working with {skill}, and how did you resolve them?",
         "Explain a specific edge case or bottleneck, step-by-step root-cause debugging, and the monitoring implemented.",
         "Highlight systematic debugging and automated testing."),
        ("If asked to implement {skill} into our tech stack, what would your step-by-step rollout plan look like?",
         "Outline requirements gathering, proof-of-concept validation, integration testing, and team knowledge sharing.",
         "Emphasize risk mitigation and seamless continuous delivery."),
        ("How do you evaluate performance bottlenecks and monitor telemetry in {skill} services?",
         "Reference APM tools, profiling, indexed queries, and asynchronous task queues.",
         "Provide concrete metrics or benchmarks where possible."),
        ("Compare {skill} with alternative paradigms or technologies. Why choose it for our target requirements?",
         "Highlight trade-offs between performance, developer velocity, ecosystem maturity, and operational overhead.",
         "Demonstrate balanced technical decision-making aligned with business goals.")
    ]

    for i in range(missing_technical_count):
        skill = probe_skills[i % len(probe_skills)]
        tmpl = tech_templates[i % len(tech_templates)]
        fallback_tech.append({
            "question": tmpl[0].format(skill=skill),
            "suggested_answer": tmpl[1],
            "tips": tmpl[2],
        })

    fallback_beh = []
    beh_templates = [
        ("Describe a challenging technical problem you faced in your recent work and how you tackled it.",
         "Use the STAR format: Explain the problem constraints, your technical hypothesis, the cross-functional action taken, and the quantified outcome.",
         "Keep focus on proactive ownership and resilience."),
        ("Tell me about a time you had to adapt quickly to an unexpected project requirement or unfamiliar framework.",
         "Highlight rapid documentation study, building small proof-of-concepts, asking targeted peer questions, and delivering on schedule.",
         "Demonstrate growth mindset and high adaptability under tight deadlines."),
        ("How do you handle technical disagreements or differing design opinions within an engineering team?",
         "Focus on data-driven benchmarking, collaborative RFC/design docs, empathy, and committing to the team consensus.",
         "Show emotional intelligence, active listening, and blameless collaboration.")
    ]

    for i in range(missing_behavioral_count):
        tmpl = beh_templates[i % len(beh_templates)]
        fallback_beh.append({
            "question": tmpl[0],
            "suggested_answer": tmpl[1],
            "tips": tmpl[2],
        })

    return fallback_tech, fallback_beh


def generate_questions_fast(
    provider,
    resume_data: dict,
    jd_text: str,
    matched_skills: List[str],
    missing_skills: List[str],
    target_role: Optional[str] = None
) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Optimized high-speed single-call generator.
    Passes pruned context and mandates concise 1-2 sentence answers for sub-2-second response.
    """
    cand = extract_candidate_summary(resume_data)
    
    # Prune JD text to core requirement window (max 900 chars)
    trimmed_jd = jd_text.strip()
    if len(trimmed_jd) > 900:
        trimmed_jd = trimmed_jd[:900] + "..."

    matched_str = ", ".join(matched_skills[:6]) if matched_skills else ", ".join(cand["skills"][:4]) or "Relevant Tech Stack"
    missing_str = ", ".join(missing_skills[:5]) if missing_skills else "Domain nuances & advanced patterns"
    roles_str = ", ".join(cand["recent_roles"]) or "Software Engineering background"
    role_target = target_role or "Target Role"

    prompt = f"""Generate tailored interview prep questions.

CANDIDATE:
- Role/Experience: {roles_str}
- Candidate Skills: {', '.join(cand['skills'])}
- Matched Skills with JD: {matched_str}
- Missing Skills / Gap Areas: {missing_str}

JOB DESCRIPTION CONTEXT:
Target Role: {role_target}
{trimmed_jd}

REQUIREMENTS:
- Exactly 5 technical questions: probe candidate's matched skills and assess gaps in missing skills.
- Exactly 3 behavioral questions: assess problem-solving, collaboration, and engineering execution.
- SPEED CONSTRAINT:
  * "suggested_answer": strictly 1-2 concise sentences.
  * "tips": strictly 1 concise sentence.
  * Do NOT write long paragraphs.

Return ONLY a JSON object in this exact schema:
{{
  "technical_questions": [
    {{"question": "string", "suggested_answer": "1-2 sentence sample answer.", "tips": "1 sentence tip."}}
  ],
  "behavioral_questions": [
    {{"question": "string", "suggested_answer": "1-2 sentence sample answer.", "tips": "1 sentence tip."}}
  ]
}}"""

    system_message = (
        "You are an elite technical interviewer. "
        "Return valid JSON only. Keep answers and tips strictly concise (1-2 sentences). "
        "Provide exactly 5 technical and 3 behavioral questions."
    )

    try:
        raw_result = provider.complete(
            prompt=prompt,
            system_message=system_message,
            response_format_json=True
        )
        data = parse_ai_json(raw_result)
        technical = clean_questions(data.get("technical_questions"))
        behavioral = clean_questions(data.get("behavioral_questions"))
    except Exception as e:
        print(f"Fast LLM completion encountered issue: {e}. Falling back to domain generator.")
        technical, behavioral = [], []

    # If any question is missing, instantly top up with tailored fallback questions (0s overhead)
    missing_tech = max(0, TECHNICAL_REQUIRED - len(technical))
    missing_beh = max(0, BEHAVIORAL_REQUIRED - len(behavioral))

    if missing_tech > 0 or missing_beh > 0:
        fb_tech, fb_beh = generate_fallback_questions(
            missing_tech, missing_beh, matched_skills, missing_skills, cand, role_target
        )
        technical.extend(fb_tech)
        behavioral.extend(fb_beh)

    return technical[:TECHNICAL_REQUIRED], behavioral[:BEHAVIORAL_REQUIRED]


@router.post("/interview-prep")
def generate_interview_prep(request: InterviewPrepRequest, db: Session = Depends(get_db)):
    """
    Generate 5 technical and 3 behavioral interview questions based on Resume and Job Description.
    Reuses pre-extracted skills for rapid generation.
    """
    resume = request.resume_data or {}
    if not resume and request.resume_id:
        db_resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
        if db_resume and db_resume.structured_json:
            resume = db_resume.structured_json

    if not resume:
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume first."
        )

    if not request.jd_text or len(request.jd_text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="A valid Job Description of at least 10 characters is required."
        )

    try:
        provider = get_llm_provider()
        technical, behavioral = generate_questions_fast(
            provider=provider,
            resume_data=resume,
            jd_text=request.jd_text,
            matched_skills=request.matched_skills or [],
            missing_skills=request.missing_skills or [],
            target_role=request.target_role
        )

        return {
            "technical_questions": technical,
            "behavioral_questions": behavioral,
        }

    except HTTPException:
        raise
    except Exception as e:
        print("INTERVIEW PREP ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Interview preparation generation failed: {str(e)}"
        )
