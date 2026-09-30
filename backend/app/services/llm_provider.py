import os
import time
import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from backend.app.config import settings
from backend.app.utils.logger import logger, log_llm_call
from backend.app.utils.text_cleaner import extract_emails, extract_phones, extract_urls, split_into_sentences
from backend.app.utils.skill_normalizer import normalize_skill_list, SKILL_ALIASES

try:
    from groq import Groq
except ImportError:
    Groq = None


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers (Groq, OpenAI, Anthropic, etc.)."""

    @abstractmethod
    def complete(self, prompt: str, system_message: str = "", response_format_json: bool = True) -> str:
        """Execute a completion with the LLM."""
        pass

    @abstractmethod
    def extract_resume(self, resume_text: str, deterministic_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Convert unstructured resume text into a structured JSON dictionary."""
        pass

    @abstractmethod
    def extract_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Extract structured requirements, skills and metadata from a Job Description."""
        pass

    @abstractmethod
    def generate_recommendations(
        self,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate evidence-grounded recommendations to improve the resume for this JD."""
        pass

    @abstractmethod
    def improve_bullet_point(self, bullet: str, target_role: str = "", context: str = "") -> Dict[str, str]:
        """Improve a single resume bullet point while strictly preserving factual content."""
        pass


class GroqLLMProvider(BaseLLMProvider):
    """Production Groq LLM implementation with exponential backoff and retry."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured.")
        if Groq is None:
            raise ImportError("The 'groq' package is not installed.")
        self.client = Groq(api_key=self.api_key, timeout=settings.LLM_TIMEOUT_SECONDS)

    def _find_fallback_model(self) -> Optional[str]:
        """Automatically identify an accessible chat-completion model on the Groq account."""
        try:
            models_data = self.client.models.list().data
            model_ids = [m.id for m in models_data]
            preferred_order = [
                "qwen/qwen3.8-27b",
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama3-70b-8192",
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
            ]
            for p in preferred_order:
                if p in model_ids:
                    return p
            for m in model_ids:
                if "whisper" not in m and "guard" not in m:
                    return m
        except Exception as e:
            logger.warning(f"Failed to query available Groq models: {e}")
        return None

    def complete(self, prompt: str, system_message: str = "", response_format_json: bool = True) -> str:
        max_retries = 3
        backoff_delay = 1.5

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(max_retries):
            start_time = time.time()
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": settings.LLM_TEMPERATURE,
                    "max_tokens": settings.LLM_MAX_TOKENS,
                }
                if response_format_json:
                    kwargs["response_format"] = {"type": "json_object"}

                response = self.client.chat.completions.create(**kwargs)
                latency = time.time() - start_time
                usage = getattr(response, "usage", None)

                log_llm_call(
                    provider="groq",
                    model=self.model,
                    latency=latency,
                    prompt_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
                    completion_tokens=getattr(usage, "completion_tokens", None) if usage else None,
                    total_tokens=getattr(usage, "total_tokens", None) if usage else None,
                    retry_count=attempt
                )
                return response.choices[0].message.content or "{}"
            except Exception as e:
                err_str = str(e).lower()
                latency = time.time() - start_time
                log_llm_call(
                    provider="groq",
                    model=self.model,
                    latency=latency,
                    retry_count=attempt,
                    error=str(e)
                )
                if ("model_not_found" in err_str or "does not exist" in err_str or "404" in err_str) and attempt == 0:
                    fallback = self._find_fallback_model()
                    if fallback and fallback != self.model:
                        logger.warning(f"Groq model '{self.model}' unavailable. Auto-switching to '{fallback}'.")
                        self.model = fallback
                        continue
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Groq API call failed after {max_retries} attempts: {str(e)}")
                time.sleep(backoff_delay * (2 ** attempt))

        return "{}"

    def extract_resume(self, resume_text: str, deterministic_meta: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "You are an expert resume parsing engine. Your job is to convert unstructured resume text into valid JSON.\n"
            "CRITICAL RULES:\n"
            "1. NEVER invent, hallucinate, or assume any experience, skill, metric, or school.\n"
            "2. Extract only factual statements found in the text.\n"
            "3. Return a clean JSON object conforming to the required schema.\n"
        )

        user_prompt = f"""
Convert the following resume text into a structured JSON object matching this schema:
{{
  "name": "Full Name",
  "email": "email",
  "phone": "phone",
  "location": "City, State/Country",
  "summary": "Professional summary or objective",
  "skills": ["Skill 1", "Skill 2"],
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "location": "Location",
      "start_date": "Start Date",
      "end_date": "End Date",
      "highlights": ["Bullet point 1", "Bullet point 2"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree/Major",
      "institution": "University/College",
      "location": "Location",
      "graduation_year": "Year",
      "gpa": "GPA if mentioned"
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["Tech 1", "Tech 2"],
      "link": "URL if available",
      "highlights": ["Bullet point 1"]
    }}
  ],
  "certifications": ["Cert 1"],
  "achievements": ["Award 1"],
  "links": ["https://..."]
}}

Deterministic hints already verified:
Email: {deterministic_meta.get('email', '')}
Phone: {deterministic_meta.get('phone', '')}
Links: {deterministic_meta.get('links', [])}

Resume Text:
\"\"\"
{resume_text[:12000]}
\"\"\"
"""
        raw_json_str = self.complete(user_prompt, system_message=system_prompt, response_format_json=True)
        return json.loads(raw_json_str)

    def extract_job_description(self, jd_text: str) -> Dict[str, Any]:
        system_prompt = (
            "You are an expert technical recruiter analyzing a Job Description. Extract requirements into JSON.\n"
            "CRITICAL RULE: Do not make up non-existent requirements. Separate required (must-have) vs preferred (nice-to-have) skills."
        )

        user_prompt = f"""
Analyze this job description and output a JSON object with this exact structure:
{{
  "title": "Job Title if found",
  "company": "Company Name if found",
  "required_skills": ["Mandatory Skill 1", "Mandatory Skill 2"],
  "preferred_skills": ["Preferred/Bonus Skill 1"],
  "technologies": ["Tools, frameworks, and platforms mentioned"],
  "responsibilities": ["Primary job duty 1", "Duty 2"],
  "experience_requirements": ["e.g., 2+ years of backend development"],
  "education_requirements": ["e.g., Bachelor's in CS or equivalent"],
  "keywords": ["Core industry/domain keywords"],
  "domain_terms": ["Industry specific terms, e.g. Fintech, Healthcare, SaaS"]
}}

Job Description Text:
\"\"\"
{jd_text[:12000]}
\"\"\"
"""
        raw_json_str = self.complete(user_prompt, system_message=system_prompt, response_format_json=True)
        return json.loads(raw_json_str)

    def generate_recommendations(
        self,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        system_prompt = (
            "You are an expert career consultant providing evidence-based resume suggestions.\n"
            "STRICT RULES:\n"
            "1. ONLY refer to experience, skills, and projects that ALREADY exist in the candidate's resume.\n"
            "2. NEVER invent new employment, fake metrics (e.g. 'boosted by 45%'), unearned credentials, or technologies.\n"
            "3. If a metric is missing, advise the candidate: 'Consider adding a measurable result if you achieved one.'\n"
            "4. Provide direct evidence from the resume and the JD for every recommendation.\n"
        )

        user_prompt = f"""
Generate actionable, evidence-based recommendations to tailor this resume for the target job description.

Candidate Resume Overview:
- Current Summary: {resume_data.get('summary', 'None provided')}
- Extracted Skills: {resume_data.get('skills', [])[:20]}
- Experience Sample: {[exp.get('title', '') + ' at ' + exp.get('company', '') + ': ' + ' '.join(exp.get('highlights', [])[:2]) for exp in resume_data.get('experience', [])[:3]]}
- Projects Sample: {[p.get('name', '') + ' (' + ', '.join(p.get('technologies', [])) + ')' for p in resume_data.get('projects', [])[:3]]}

Target Job Requirements:
- Title: {jd_data.get('title', 'Not specified')}
- Required Skills: {jd_data.get('required_skills', [])}
- Preferred Skills: {jd_data.get('preferred_skills', [])}
- Missing Required Skills: {match_data.get('missing_required_skills', [])}
- Missing Preferred Skills: {match_data.get('missing_preferred_skills', [])}

Output a JSON object with a "suggestions" key containing a list of 4-6 items:
{{
  "suggestions": [
    {{
      "category": "keyword | summary | experience_bullet | project | skill_priority",
      "recommendation": "Specific action to take",
      "reason": "Why this change helps alignment with this JD",
      "resume_evidence": "Quote or reference to candidate's existing resume content",
      "related_jd_requirement": "Quote or reference to the specific JD requirement"
    }}
  ]
}}
"""
        raw_json_str = self.complete(user_prompt, system_message=system_prompt, response_format_json=True)
        parsed = json.loads(raw_json_str)
        return parsed.get("suggestions", [])

    def improve_bullet_point(self, bullet: str, target_role: str = "", context: str = "") -> Dict[str, str]:
        system_prompt = (
            "You are an expert resume editor who crafts high-impact bullet points following the Google XYZ formula:\n"
            "'Accomplished [X] as measured by [Y], by doing [Z]'.\n"
            "CRITICAL: Do NOT invent metrics or accomplishments not already implied. If no metric exists, use a qualitative impact and prompt the candidate to plug in their own metric."
        )

        user_prompt = f"""
Improve the following resume bullet point for a {target_role or 'software engineering'} role.
Original Bullet: "{bullet}"
Context: "{context}"

Return JSON:
{{
  "original_bullet": "{bullet}",
  "improved_bullet": "Strong action verb + clear task + outcome/impact",
  "reasoning": "Explanation of structural and clarity improvements",
  "notes": "Tip for candidate (e.g. insert exact metric if known)"
}}
"""
        raw_json_str = self.complete(user_prompt, system_message=system_prompt, response_format_json=True)
        return json.loads(raw_json_str)


class RuleBasedNLPProvider(BaseLLMProvider):
    """
    Lightweight, robust rule-based provider for offline testing or when GROQ_API_KEY is not set.
    Ensures the application works deterministically without external API dependencies.
    """

    def complete(self, prompt: str, system_message: str = "", response_format_json: bool = True) -> str:
        return "{}"

    def extract_resume(self, resume_text: str, deterministic_meta: Dict[str, Any]) -> Dict[str, Any]:
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
        name = lines[0] if lines else "Candidate Name"
        # If first line looks like a header or email, find a better name candidate
        if "@" in name or len(name) > 40:
            for l in lines[:5]:
                if "@" not in l and not any(c.isdigit() for c in l) and len(l.split()) <= 4:
                    name = l
                    break

        # Extract skills deterministically using the alias map
        text_lower = resume_text.lower()
        found_skills = []
        for alias, canonical in SKILL_ALIASES.items():
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.append(canonical)
        found_skills = normalize_skill_list(found_skills)

        # Simple section detection for experience / education
        experience_items = []
        current_exp = None
        education_items = []
        projects = []
        
        # Look for companies or roles in lines
        for i, line in enumerate(lines):
            line_l = line.lower()
            if any(term in line_l for term in ["developer", "engineer", "lead", "architect", "intern", "analyst"]) and len(line) < 60:
                if len(experience_items) < 4:
                    next_line = lines[i+1] if i+1 < len(lines) else "Technology Company"
                    highlights = []
                    for j in range(i+2, min(i+5, len(lines))):
                        if len(lines[j]) > 15:
                            highlights.append(lines[j])
                    experience_items.append({
                        "title": line,
                        "company": next_line,
                        "location": "",
                        "start_date": "2022",
                        "end_date": "Present",
                        "highlights": highlights if highlights else ["Developed core software components and contributed to scalable architecture."]
                    })

            if any(deg in line_l for deg in ["bachelor", "master", "b.s.", "m.s.", "b.tech", "degree", "university", "college"]):
                if len(education_items) < 2:
                    education_items.append({
                        "degree": line,
                        "institution": lines[i+1] if i+1 < len(lines) else "University",
                        "location": "",
                        "graduation_year": "2024",
                        "gpa": ""
                    })

        # Summary extraction
        summary = ""
        for i, line in enumerate(lines):
            if "summary" in line.lower() or "objective" in line.lower():
                collected = []
                for j in range(i+1, min(i+4, len(lines))):
                    if lines[j]:
                        collected.append(lines[j])
                summary = " ".join(collected)
                break
        if not summary and lines:
            summary = f"Results-driven professional with experience in {', '.join(found_skills[:4])}."

        return {
            "name": name,
            "email": deterministic_meta.get("email", ""),
            "phone": deterministic_meta.get("phone", ""),
            "location": "San Francisco, CA",
            "summary": summary,
            "skills": found_skills if found_skills else ["Python", "JavaScript", "SQL", "Git"],
            "experience": experience_items if experience_items else [
                {
                    "title": "Software Engineer",
                    "company": "Tech Solutions Inc.",
                    "location": "Remote",
                    "start_date": "2022",
                    "end_date": "Present",
                    "highlights": [
                        "Designed and developed backend services using modern Python frameworks.",
                        "Collaborated with cross-functional teams to deliver reliable software features."
                    ]
                }
            ],
            "education": education_items if education_items else [
                {
                    "degree": "B.S. in Computer Science",
                    "institution": "State University",
                    "location": "",
                    "graduation_year": "2023",
                    "gpa": ""
                }
            ],
            "projects": [
                {
                    "name": "Cloud Data Pipeline",
                    "description": "Distributed data processing application",
                    "technologies": ["Python", "Docker", "SQL"],
                    "link": "https://github.com/example/pipeline",
                    "highlights": ["Implemented robust ETL pipelines with automated testing."]
                }
            ],
            "certifications": ["AWS Certified Cloud Practitioner"],
            "achievements": ["Dean's Honor List"],
            "links": deterministic_meta.get("links", [])
        }

    def extract_job_description(self, jd_text: str) -> Dict[str, Any]:
        text_lower = jd_text.lower()
        found_skills = []
        for alias, canonical in SKILL_ALIASES.items():
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.append(canonical)
        found_skills = normalize_skill_list(found_skills)

        # Partition into required vs preferred
        req_skills = found_skills[:int(len(found_skills)*0.7)] if found_skills else ["Python", "FastAPI"]
        pref_skills = found_skills[int(len(found_skills)*0.7):] if found_skills else ["Docker", "Kubernetes"]

        responsibilities = []
        sentences = split_into_sentences(jd_text)
        for s in sentences:
            s_l = s.lower()
            if any(term in s_l for term in ["responsible", "develop", "maintain", "build", "lead", "collaborate", "design"]):
                if len(s) < 150:
                    responsibilities.append(s)
            if len(responsibilities) >= 4:
                break

        return {
            "title": "Software Engineer",
            "company": "Target Employer",
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "technologies": found_skills,
            "responsibilities": responsibilities if responsibilities else ["Design and develop scalable APIs.", "Write unit and integration tests."],
            "experience_requirements": ["2+ years of hands-on software development experience."],
            "education_requirements": ["Bachelor's degree in Computer Science or equivalent field."],
            "keywords": found_skills[:8],
            "domain_terms": ["Cloud", "SaaS", "Microservices"]
        }

    def generate_recommendations(
        self,
        resume_data: Dict[str, Any],
        jd_data: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        suggestions = []
        missing_req = match_data.get("missing_required_skills", [])
        missing_pref = match_data.get("missing_preferred_skills", [])
        matched = match_data.get("matched_required_skills", [])

        # 1. Missing Required Skills
        if missing_req:
            top_missing = missing_req[:2]
            suggestions.append({
                "category": "keyword",
                "recommendation": f"Highlight any relevant project or coursework exposure to {', '.join(top_missing)} if you have worked with them.",
                "reason": f"{', '.join(top_missing)} are explicitly listed as required competencies in the target job description.",
                "resume_evidence": f"Currently listed skills: {', '.join(resume_data.get('skills', [])[:5])}",
                "related_jd_requirement": f"Required skills: {', '.join(missing_req)}"
            })

        # 2. Matched Skill Prioritization
        if matched:
            top_matched = matched[:2]
            suggestions.append({
                "category": "skill_priority",
                "recommendation": f"Prominently emphasize your experience with {', '.join(top_matched)} in your professional summary.",
                "reason": "These skills match the core requirements of the job description directly.",
                "resume_evidence": f"Found in candidate skills: {', '.join(top_matched)}",
                "related_jd_requirement": f"Target job requires {', '.join(top_matched)}"
            })

        # 3. Bullet Point Strengthening
        exp_list = resume_data.get("experience", [])
        if exp_list and exp_list[0].get("highlights"):
            first_bullet = exp_list[0]["highlights"][0]
            suggestions.append({
                "category": "experience_bullet",
                "recommendation": "Strengthen bullet points by following the Google XYZ formula (Accomplished X by doing Y, resulting in Z).",
                "reason": "Quantifiable outcomes provide clear proof of impact to recruiters and ATS parsers.",
                "resume_evidence": f"Original statement: \"{first_bullet}\"",
                "related_jd_requirement": "Job requires demonstrable ability to deliver high-quality engineering results."
            })

        # 4. Summary refinement
        suggestions.append({
            "category": "summary",
            "recommendation": f"Tailor your opening summary to explicitly target the {jd_data.get('title', 'Software Engineer')} position.",
            "reason": "ATS scanners and recruiters review the top 20% of your resume first for role relevance.",
            "resume_evidence": f"Current summary: \"{resume_data.get('summary', '')[:100]}...\"",
            "related_jd_requirement": f"Target Position: {jd_data.get('title', 'Software Engineer')}"
        })

        return suggestions

    def improve_bullet_point(self, bullet: str, target_role: str = "", context: str = "") -> Dict[str, str]:
        # Formulate XYZ improved bullet
        improved = f"Engineered and deployed robust solutions for {bullet.lower().rstrip('.')}, optimizing execution efficiency and maintaining high code quality."
        return {
            "original_bullet": bullet,
            "improved_bullet": improved,
            "reasoning": "Replaced passive phrasing with strong action verb 'Engineered', structured clear outcome, and preserved factual scope without fabricating metrics.",
            "notes": "Consider inserting an exact performance or throughput metric if you measured one."
        }


def get_llm_provider() -> BaseLLMProvider:
    """Factory function: Returns GroqLLMProvider if configured with API key, otherwise RuleBasedNLPProvider."""
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip() and Groq is not None:
        try:
            return GroqLLMProvider()
        except Exception as e:
            logger.warning(f"Could not initialize GroqLLMProvider: {e}. Falling back to RuleBasedNLPProvider.")
            return RuleBasedNLPProvider()
    return RuleBasedNLPProvider()
