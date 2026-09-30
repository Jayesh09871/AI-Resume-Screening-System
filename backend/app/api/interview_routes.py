
import json
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.services.llm_provider import get_llm_provider

router = APIRouter(tags=["Interview Preparation"])


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


def generate_questions(provider, resume, jd_text):

    prompt = f"""
Generate interview preparation questions using the candidate's resume
and the target job description.

RESUME:
{json.dumps(resume, ensure_ascii=False)}

JOB DESCRIPTION:
{jd_text}

STRICT OUTPUT REQUIREMENTS:

Generate exactly 5 technical questions and exactly 3 behavioral questions.

Technical questions:
- Focus on skills, projects, technologies and concepts relevant to the JD.
- Personalize questions using the resume wherever possible.

Behavioral questions:
- Focus on teamwork, problem solving, challenges and project experience.
- Do not invent candidate experiences.

Every question must contain:
1. question: a string
2. suggested_answer: a concise, useful sample answer
3. tips: a short string containing 1-2 preparation tips

Keep suggested answers concise to avoid unnecessarily long output.

Return ONLY valid JSON in this exact structure:

{{
  "technical_questions": [
    {{
      "question": "Technical question 1",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }},
    {{
      "question": "Technical question 2",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }},
    {{
      "question": "Technical question 3",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }},
    {{
      "question": "Technical question 4",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }},
    {{
      "question": "Technical question 5",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }}
  ],
  "behavioral_questions": [
    {{
      "question": "Behavioral question 1",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }},
    {{
      "question": "Behavioral question 2",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }},
    {{
      "question": "Behavioral question 3",
      "suggested_answer": "Concise sample answer",
      "tips": "Preparation tip"
    }}
  ]
}}
"""

    result = provider.complete(
        prompt=prompt,
        system_message=(
            "You are an interview preparation assistant. "
            "Return valid JSON only. Generate exactly 5 technical "
            "and 3 behavioral questions. Keep answers concise."
        ),
        response_format_json=True
    )

    data = parse_ai_json(result)

    technical = data.get("technical_questions")
    behavioral = data.get("behavioral_questions")

    if not isinstance(technical, list) or len(technical) != 5:
        raise ValueError(
            "The AI did not generate exactly 5 technical questions."
        )

    if not isinstance(behavioral, list) or len(behavioral) != 3:
        raise ValueError(
            "The AI did not generate exactly 3 behavioral questions."
        )

    for section in (technical, behavioral):
        for item in section:

            if not isinstance(item, dict):
                raise ValueError("Invalid question object generated.")

            for field in ("question", "suggested_answer", "tips"):
                if not item.get(field):
                    raise ValueError(
                        f"Generated question is missing '{field}'."
                    )

            if isinstance(item["tips"], list):
                item["tips"] = "\n".join(
                    f"• {tip}" for tip in item["tips"]
                )

            if not isinstance(item["tips"], str):
                raise ValueError("Question tips must be text.")

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
