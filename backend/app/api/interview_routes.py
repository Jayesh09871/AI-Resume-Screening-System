
import json
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.llm_provider import get_llm_provider

router = APIRouter(tags=["Interview Preparation"])

TECHNICAL_REQUIRED = 5
BEHAVIORAL_REQUIRED = 3


class InterviewPrepRequest(BaseModel):
    resume_id: int | None = None
    resume_data: dict | None = None
    jd_text: str = Field(min_length=10)


def parse_ai_json(result):
    """Parse JSON returned by the AI provider."""

    if not isinstance(result, str):
        raise ValueError("Unexpected AI response type.")

    result = result.strip()

    result = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        result,
        flags=re.IGNORECASE
    ).strip()

    start = result.find("{")
    end = result.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("The AI did not return valid JSON.")

    data = json.loads(result[start:end + 1])

    if not isinstance(data, dict):
        raise ValueError("The AI response must be a JSON object.")

    return data


def call_ai(provider, prompt):
    """Call the configured LLM and parse its JSON response."""

    result = provider.complete(
        prompt=prompt,
        system_message=(
            "You are an interview preparation assistant. "
            "Return valid JSON only. Follow the requested counts exactly. "
            "Do not invent candidate experiences or qualifications."
        ),
        response_format_json=True
    )

    return parse_ai_json(result)


def is_valid_question(item):
    """Check whether a generated question has all required fields."""

    if not isinstance(item, dict):
        return False

    for field in ("question", "suggested_answer", "tips"):
        if not isinstance(item.get(field), str) or not item[field].strip():
            return False

    return True


def clean_questions(items):
    """Keep only well-formed question objects."""

    if not isinstance(items, list):
        return []

    cleaned = []

    for item in items:
        if not isinstance(item, dict):
            continue

        # Convert list-based tips into readable text.
        if isinstance(item.get("tips"), list):
            item = item.copy()
            item["tips"] = "\n".join(
                f"• {tip}" for tip in item["tips"]
            )

        if is_valid_question(item):
            cleaned.append(item)

    return cleaned


def generate_questions(provider, resume, jd_text):

    prompt = f"""
Generate interview preparation questions using the candidate's resume
and the target job description.

RESUME:
{json.dumps(resume, ensure_ascii=False)}

JOB DESCRIPTION:
{jd_text}

Generate exactly:
- 5 technical questions
- 3 behavioral questions

Technical questions should cover relevant skills, projects, technologies,
and concepts from the job description.

Behavioral questions should cover teamwork, problem solving, challenges,
and project experience.

Do not invent candidate experiences. When personal details are unavailable,
write suggested answers as adaptable examples rather than claiming the
candidate has done something.

Every question must contain:
- question: string
- suggested_answer: string
- tips: string

Keep answers concise.

Return ONLY valid JSON in this structure:

{{
  "technical_questions": [
    {{
      "question": "Question",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }}
  ],
  "behavioral_questions": [
    {{
      "question": "Question",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }}
  ]
}}

The technical_questions array must contain exactly 5 objects.
The behavioral_questions array must contain exactly 3 objects.
"""

    data = call_ai(provider, prompt)

    technical = clean_questions(data.get("technical_questions"))
    behavioral = clean_questions(data.get("behavioral_questions"))

    print(
        "INITIAL INTERVIEW PREP COUNTS:",
        "Technical =", len(technical),
        "Behavioral =", len(behavioral)
    )

    # Retry by requesting only the missing questions.
    for attempt in range(1, 3):

        missing_technical = max(
            0, TECHNICAL_REQUIRED - len(technical)
        )

        missing_behavioral = max(
            0, BEHAVIORAL_REQUIRED - len(behavioral)
        )

        if missing_technical == 0 and missing_behavioral == 0:
            break

        retry_prompt = f"""
We are completing an interview preparation response.

RESUME:
{json.dumps(resume, ensure_ascii=False)}

JOB DESCRIPTION:
{jd_text}

Generate ONLY the missing questions.

Missing technical questions: {missing_technical}
Missing behavioral questions: {missing_behavioral}

Do not repeat these existing questions:

TECHNICAL:
{json.dumps(technical, ensure_ascii=False)}

BEHAVIORAL:
{json.dumps(behavioral, ensure_ascii=False)}

Each generated question must contain:
- question: string
- suggested_answer: string
- tips: string

Do not invent candidate experiences. Keep answers concise.

Return ONLY valid JSON in this exact structure:

{{
  "technical_questions": [],
  "behavioral_questions": []
}}

The technical_questions array must contain exactly
{missing_technical} new questions.

The behavioral_questions array must contain exactly
{missing_behavioral} new questions.
"""

        print(
            f"INTERVIEW PREP RETRY {attempt}:",
            "Missing technical =", missing_technical,
            "Missing behavioral =", missing_behavioral
        )

        try:
            retry_data = call_ai(provider, retry_prompt)

            new_technical = clean_questions(
                retry_data.get("technical_questions")
            )

            new_behavioral = clean_questions(
                retry_data.get("behavioral_questions")
            )

            technical.extend(new_technical)
            behavioral.extend(new_behavioral)

            # Do not keep extra questions.
            technical = technical[:TECHNICAL_REQUIRED]
            behavioral = behavioral[:BEHAVIORAL_REQUIRED]

        except Exception as retry_error:
            print(
                f"INTERVIEW PREP RETRY {attempt} ERROR:",
                str(retry_error)
            )

    print(
        "FINAL INTERVIEW PREP COUNTS:",
        "Technical =", len(technical),
        "Behavioral =", len(behavioral)
    )

    if len(technical) != TECHNICAL_REQUIRED:
        raise ValueError(
            "Unable to generate exactly 5 valid technical questions. "
            "Please try again."
        )

    if len(behavioral) != BEHAVIORAL_REQUIRED:
        raise ValueError(
            "Unable to generate exactly 3 valid behavioral questions. "
            "Please try again."
        )

    return technical, behavioral


@router.post("/interview-prep")
def generate_interview_prep(request: InterviewPrepRequest):

    if not request.resume_data and not request.resume_id:
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume first."
        )

    resume = request.resume_data or {}

    try:
        provider = get_llm_provider()

        technical, behavioral = generate_questions(
            provider,
            resume,
            request.jd_text
        )

        return {
            "technical_questions": technical,
            "behavioral_questions": behavioral
        }

    except HTTPException:
        raise

    except Exception as e:
        print("INTERVIEW PREP ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Interview preparation generation failed: {str(e)}"
        )
