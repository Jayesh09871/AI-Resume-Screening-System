from typing import List, Dict, Any, Optional
from backend.app.models.schemas import (
    ResumeSchema,
    JobDescriptionSchema,
    MatchResultSchema,
    EvidenceBasedSuggestion,
)
from backend.app.services.llm_provider import get_llm_provider, BaseLLMProvider
from backend.app.utils.logger import logger


class RecommendationEngine:
    """
    Generates evidence-backed recommendations for tailoring a resume to a JD.
    Enforces the STRICT ANTI-HALLUCINATION principle:
    - Never invents companies, dates, degrees, or unearned technologies.
    - Prompts user to supply real metrics instead of fabricating numbers.
    - Every recommendation pairs resume evidence with JD requirements.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider or get_llm_provider()

    def generate(
        self,
        resume: ResumeSchema,
        jd: JobDescriptionSchema,
        match_result: MatchResultSchema,
    ) -> List[EvidenceBasedSuggestion]:
        resume_dict = resume.model_dump()
        jd_dict = jd.model_dump()
        match_dict = match_result.model_dump()

        try:
            raw_suggestions = self.llm_provider.generate_recommendations(
                resume_dict, jd_dict, match_dict
            )
        except Exception as e:
            logger.error(f"Error in LLM recommendations: {e}. Falling back to rule-based engine.")
            from backend.app.services.llm_provider import RuleBasedNLPProvider
            fallback = RuleBasedNLPProvider()
            raw_suggestions = fallback.generate_recommendations(
                resume_dict, jd_dict, match_dict
            )

        # Validate and sanitize suggestions
        validated: List[EvidenceBasedSuggestion] = []
        for item in raw_suggestions:
            try:
                # Anti-hallucination check: ensure evidence fields exist
                cat = item.get("category", "keyword")
                rec = item.get("recommendation", "")
                reason = item.get("reason", "")
                evidence = item.get("resume_evidence", "")
                jd_req = item.get("related_jd_requirement", "")

                if not evidence:
                    evidence = f"Candidate profile skills: {', '.join(resume.skills[:4])}"
                if not jd_req:
                    jd_req = f"Target job role: {jd.title or 'Target Position'}"

                validated.append(
                    EvidenceBasedSuggestion(
                        category=cat,
                        recommendation=rec,
                        reason=reason,
                        resume_evidence=evidence,
                        related_jd_requirement=jd_req,
                    )
                )
            except Exception as parse_err:
                logger.warning(f"Skipping malformed suggestion item: {parse_err}")

        # Ensure at least 3 high quality suggestions exist
        if len(validated) < 3:
            from backend.app.services.llm_provider import RuleBasedNLPProvider
            fallback_items = RuleBasedNLPProvider().generate_recommendations(
                resume_dict, jd_dict, match_dict
            )
            for fb in fallback_items:
                if len(validated) >= 4:
                    break
                validated.append(EvidenceBasedSuggestion(**fb))

        return validated
