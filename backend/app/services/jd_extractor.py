from typing import Dict, Any, Optional
from pydantic import ValidationError
from backend.app.models.schemas import JobDescriptionSchema
from backend.app.utils.text_cleaner import normalize_whitespace
from backend.app.utils.skill_normalizer import normalize_skill_list
from backend.app.services.llm_provider import get_llm_provider, BaseLLMProvider
from backend.app.utils.logger import logger


class JobDescriptionExtractor:
    """
    Analyzes and extracts structured requirements from a Job Description (JD).
    Separates required skills from preferred skills, detects technologies,
    responsibilities, experience, and education expectations.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider or get_llm_provider()

    def extract(self, jd_text: str) -> JobDescriptionSchema:
        clean_text = normalize_whitespace(jd_text)
        if len(clean_text) < 10:
            raise ValueError("Job description is too short to analyze.")

        try:
            extracted_dict = self.llm_provider.extract_job_description(clean_text)
        except Exception as e:
            logger.warning(f"Primary LLM JD extraction failed: {e}. Using fallback rule-based analyzer.")
            from backend.app.services.llm_provider import RuleBasedNLPProvider
            fallback = RuleBasedNLPProvider()
            extracted_dict = fallback.extract_job_description(clean_text)

        # Normalize skill lists
        if "required_skills" in extracted_dict and isinstance(extracted_dict["required_skills"], list):
            extracted_dict["required_skills"] = normalize_skill_list(extracted_dict["required_skills"])
        if "preferred_skills" in extracted_dict and isinstance(extracted_dict["preferred_skills"], list):
            extracted_dict["preferred_skills"] = normalize_skill_list(extracted_dict["preferred_skills"])
        if "technologies" in extracted_dict and isinstance(extracted_dict["technologies"], list):
            extracted_dict["technologies"] = normalize_skill_list(extracted_dict["technologies"])

        # Pydantic validation
        try:
            return JobDescriptionSchema(**extracted_dict)
        except ValidationError as val_err:
            logger.warning(f"JD schema validation error: {val_err}. Repairing defaults.")
            repaired = {
                "title": str(extracted_dict.get("title") or "Position"),
                "company": str(extracted_dict.get("company") or ""),
                "required_skills": extracted_dict.get("required_skills") or [],
                "preferred_skills": extracted_dict.get("preferred_skills") or [],
                "technologies": extracted_dict.get("technologies") or [],
                "responsibilities": extracted_dict.get("responsibilities") or [],
                "experience_requirements": extracted_dict.get("experience_requirements") or [],
                "education_requirements": extracted_dict.get("education_requirements") or [],
                "keywords": extracted_dict.get("keywords") or [],
                "domain_terms": extracted_dict.get("domain_terms") or [],
            }
            return JobDescriptionSchema(**repaired)
