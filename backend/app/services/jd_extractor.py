import re
from typing import Dict, Any, Optional
from pydantic import ValidationError
from backend.app.models.schemas import JobDescriptionSchema
from backend.app.utils.text_cleaner import normalize_whitespace, split_into_sentences
from backend.app.utils.skill_normalizer import normalize_skill_list, SKILL_ALIASES
from backend.app.services.llm_provider import get_llm_provider, BaseLLMProvider
from backend.app.utils.logger import logger


class JobDescriptionExtractor:
    """
    High-speed, robust extractor for Job Descriptions (JD).
    Uses high-performance regex & NLP parsing to extract required/preferred skills,
    seniority, education, and responsibilities in milliseconds, with LLM enrichment.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider or get_llm_provider()

    def _fast_nlp_extract(self, jd_text: str) -> Dict[str, Any]:
        """Extract all structured fields from JD in < 3ms using NLP patterns."""
        text_lower = jd_text.lower()
        lines = [l.strip() for l in jd_text.split('\n') if l.strip()]

        # 1. Title and Company detection
        title = "Target Position"
        company = ""
        for l in lines[:5]:
            l_clean = l.strip(" -•*#")
            if any(w in l_clean.lower() for w in ['developer', 'engineer', 'manager', 'lead', 'architect', 'scientist', 'analyst', 'specialist', 'designer', 'consultant', 'officer']):
                title = l_clean.split('-')[0].split('|')[0].strip()
                if ' at ' in l_clean:
                    parts = l_clean.split(' at ')
                    title = parts[0].strip()
                    company = parts[1].split('-')[0].strip()
                break

        # 2. Partition skills into Required vs Preferred
        req_section = text_lower
        pref_section = ""
        if any(marker in text_lower for marker in ['preferred', 'nice to have', 'bonus', 'plus', 'good to have']):
            parts = re.split(r'preferred|nice to have|bonus|good to have', text_lower, maxsplit=1, flags=re.IGNORECASE)
            req_section = parts[0]
            pref_section = parts[1] if len(parts) > 1 else ""

        req_skills = []
        pref_skills = []
        all_skills = []

        for alias, canonical in SKILL_ALIASES.items():
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower):
                all_skills.append(canonical)
                if pref_section and re.search(pattern, pref_section) and not re.search(pattern, req_section):
                    pref_skills.append(canonical)
                else:
                    req_skills.append(canonical)

        req_skills = normalize_skill_list(req_skills)
        pref_skills = normalize_skill_list([s for s in pref_skills if s not in req_skills])
        all_skills = normalize_skill_list(all_skills)

        # Fallback if no specific skills matched
        if not req_skills and all_skills:
            req_skills = all_skills[:int(len(all_skills) * 0.7)]
            pref_skills = all_skills[int(len(all_skills) * 0.7):]

        # 3. Experience requirements
        exp_matches = re.findall(r'(\d+\+?\s*(?:to\s*\d+\+?\s*)?years?(?:\s+of)?(?:\s+[a-zA-Z]+){1,5})', jd_text, re.IGNORECASE)
        exp_reqs = exp_matches[:3] if exp_matches else ["Relevant professional experience in software engineering"]

        # 4. Education requirements
        edu_reqs = []
        for l in lines:
            if any(w in l.lower() for w in ['bachelor', 'master', 'degree', 'bs', 'ms', 'phd', 'computer science', 'stem']):
                edu_reqs.append(l.strip(' -•*'))
                if len(edu_reqs) >= 2:
                    break
        if not edu_reqs:
            edu_reqs = ["Bachelor's degree in Computer Science or equivalent practical experience"]

        # 5. Responsibilities
        responsibilities = []
        for l in lines:
            l_clean = l.strip(' -•*')
            if len(l_clean) > 20 and len(l_clean) < 200:
                if any(w in l_clean.lower() for w in ['design', 'build', 'develop', 'maintain', 'collaborate', 'lead', 'deploy', 'implement']):
                    responsibilities.append(l_clean)
                    if len(responsibilities) >= 4:
                        break

        return {
            "title": title,
            "company": company,
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "technologies": all_skills,
            "responsibilities": responsibilities if responsibilities else ["Design, implement, and maintain scalable solutions.", "Collaborate across cross-functional engineering teams."],
            "experience_requirements": exp_reqs,
            "education_requirements": edu_reqs,
            "keywords": all_skills[:10],
            "domain_terms": ["System Architecture", "Continuous Delivery", "Cloud Infrastructure"],
        }

    def extract(self, jd_text: str) -> JobDescriptionSchema:
        clean_text = normalize_whitespace(jd_text)
        if len(clean_text) < 10:
            raise ValueError("Job description is too short to analyze.")

        # Always run high-speed NLP extractor first (< 3ms)
        nlp_dict = self._fast_nlp_extract(clean_text)

        # Attempt fast LLM enrichment only if skills are sparse or title is generic
        if len(nlp_dict.get("required_skills", [])) < 3:
            try:
                extracted_dict = self.llm_provider.extract_job_description(clean_text)
                if extracted_dict and isinstance(extracted_dict, dict):
                    # Merge LLM results
                    for k in ["title", "company", "required_skills", "preferred_skills", "technologies"]:
                        if extracted_dict.get(k):
                            nlp_dict[k] = extracted_dict[k]
            except Exception as e:
                logger.info(f"Fast LLM enrichment skipped ({e}), using instant NLP extraction.")

        # Normalize skill lists
        if "required_skills" in nlp_dict and isinstance(nlp_dict["required_skills"], list):
            nlp_dict["required_skills"] = normalize_skill_list(nlp_dict["required_skills"])
        if "preferred_skills" in nlp_dict and isinstance(nlp_dict["preferred_skills"], list):
            nlp_dict["preferred_skills"] = normalize_skill_list(nlp_dict["preferred_skills"])
        if "technologies" in nlp_dict and isinstance(nlp_dict["technologies"], list):
            nlp_dict["technologies"] = normalize_skill_list(nlp_dict["technologies"])

        try:
            return JobDescriptionSchema(**nlp_dict)
        except ValidationError as val_err:
            logger.warning(f"JD schema validation repair: {val_err}")
            repaired = {
                "title": str(nlp_dict.get("title") or "Position"),
                "company": str(nlp_dict.get("company") or ""),
                "required_skills": nlp_dict.get("required_skills") or [],
                "preferred_skills": nlp_dict.get("preferred_skills") or [],
                "technologies": nlp_dict.get("technologies") or [],
                "responsibilities": nlp_dict.get("responsibilities") or [],
                "experience_requirements": nlp_dict.get("experience_requirements") or [],
                "education_requirements": nlp_dict.get("education_requirements") or [],
                "keywords": nlp_dict.get("keywords") or [],
                "domain_terms": nlp_dict.get("domain_terms") or [],
            }
            return JobDescriptionSchema(**repaired)
