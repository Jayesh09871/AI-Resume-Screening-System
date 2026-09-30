import json
from typing import Dict, Any, List, Optional
from pydantic import ValidationError
from backend.app.models.schemas import ResumeSchema, ExperienceItem, EducationItem, ProjectItem
from backend.app.utils.text_cleaner import extract_emails, extract_phones, extract_urls, normalize_whitespace
from backend.app.utils.skill_normalizer import normalize_skill_list
from backend.app.services.llm_provider import get_llm_provider, BaseLLMProvider
from backend.app.utils.logger import logger


class ResumeExtractor:
    """
    Hybrid Resume Extraction Pipeline:
    1. Deterministic Regex Parsing (email, phone, URLs)
    2. LLM Extraction for flexible sections
    3. Strict Pydantic Schema Validation
    4. Controlled Repair on validation failure
    5. Skill Normalization
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider or get_llm_provider()

    def parse_deterministic_fields(self, raw_text: str) -> Dict[str, Any]:
        emails = extract_emails(raw_text)
        phones = extract_phones(raw_text)
        urls = extract_urls(raw_text)

        return {
            "email": emails[0] if emails else "",
            "phone": phones[0] if phones else "",
            "links": urls,
        }

    def repair_data(self, data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """Perform controlled repair on invalid or malformed dictionary structures."""
        repaired = dict(data)
        
        # Ensure mandatory strings
        if not isinstance(repaired.get("name"), str) or not repaired["name"].strip():
            # Try to grab candidate name from first non-empty line
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
            repaired["name"] = lines[0] if lines else "Candidate"
        
        # Ensure list fields are indeed lists
        for list_field in ["skills", "certifications", "achievements", "links"]:
            if not isinstance(repaired.get(list_field), list):
                if isinstance(repaired.get(list_field), str):
                    repaired[list_field] = [s.strip() for s in repaired[list_field].split(",") if s.strip()]
                else:
                    repaired[list_field] = []

        # Fix experience items
        if isinstance(repaired.get("experience"), list):
            valid_exp = []
            for item in repaired["experience"]:
                if isinstance(item, dict):
                    valid_exp.append({
                        "title": str(item.get("title") or "Professional Role"),
                        "company": str(item.get("company") or "Company"),
                        "location": str(item.get("location") or ""),
                        "start_date": str(item.get("start_date") or ""),
                        "end_date": str(item.get("end_date") or "Present"),
                        "highlights": item.get("highlights") if isinstance(item.get("highlights"), list) else []
                    })
            repaired["experience"] = valid_exp
        else:
            repaired["experience"] = []

        # Fix education items
        if isinstance(repaired.get("education"), list):
            valid_edu = []
            for item in repaired["education"]:
                if isinstance(item, dict):
                    valid_edu.append({
                        "degree": str(item.get("degree") or "Degree"),
                        "institution": str(item.get("institution") or "University"),
                        "location": str(item.get("location") or ""),
                        "graduation_year": str(item.get("graduation_year") or ""),
                        "gpa": str(item.get("gpa") or "")
                    })
            repaired["education"] = valid_edu
        else:
            repaired["education"] = []

        # Fix project items
        if isinstance(repaired.get("projects"), list):
            valid_proj = []
            for item in repaired["projects"]:
                if isinstance(item, dict):
                    valid_proj.append({
                        "name": str(item.get("name") or "Project"),
                        "description": str(item.get("description") or ""),
                        "technologies": item.get("technologies") if isinstance(item.get("technologies"), list) else [],
                        "link": str(item.get("link") or ""),
                        "highlights": item.get("highlights") if isinstance(item.get("highlights"), list) else []
                    })
            repaired["projects"] = valid_proj
        else:
            repaired["projects"] = []

        return repaired

    def extract(self, raw_text: str) -> ResumeSchema:
        """Execute the full extraction pipeline with validation and fallback."""
        clean_text = normalize_whitespace(raw_text)
        det_meta = self.parse_deterministic_fields(clean_text)

        # 1. LLM Extraction
        try:
            extracted_dict = self.llm_provider.extract_resume(clean_text, det_meta)
        except Exception as e:
            logger.warning(f"Primary LLM resume extraction encountered error: {e}. Attempting fallback parser.")
            from backend.app.services.llm_provider import RuleBasedNLPProvider
            fallback = RuleBasedNLPProvider()
            extracted_dict = fallback.extract_resume(clean_text, det_meta)

        # 2. Merge deterministic fields if LLM missed them
        if not extracted_dict.get("email") and det_meta["email"]:
            extracted_dict["email"] = det_meta["email"]
        if not extracted_dict.get("phone") and det_meta["phone"]:
            extracted_dict["phone"] = det_meta["phone"]
        if not extracted_dict.get("links") and det_meta["links"]:
            extracted_dict["links"] = det_meta["links"]

        # 3. Normalize skills list
        if "skills" in extracted_dict and isinstance(extracted_dict["skills"], list):
            extracted_dict["skills"] = normalize_skill_list(extracted_dict["skills"])

        # 4. Strict Pydantic Validation with Controlled Repair
        try:
            validated_resume = ResumeSchema(**extracted_dict)
            return validated_resume
        except ValidationError as val_err:
            logger.warning(f"Validation error in LLM output: {val_err}. Triggering controlled repair.")
            try:
                repaired = self.repair_data(extracted_dict, clean_text)
                return ResumeSchema(**repaired)
            except Exception as repair_err:
                logger.error(f"Controlled repair failed: {repair_err}")
                raise ValueError(f"Resume extraction schema validation failed: {repair_err}")
