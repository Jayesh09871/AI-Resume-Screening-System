from typing import Dict, List, Tuple, Any
from backend.app.utils.skill_normalizer import normalize_skill, normalize_skill_list, match_skills_deterministically
from backend.app.models.schemas import ResumeSchema, JobDescriptionSchema


class SkillMatcher:
    """
    Performs deterministic and alias-based matching between Resume skills and JD skills.
    Executes before semantic matching to guarantee 100% exact & alias precision.
    """

    @staticmethod
    def match(resume: ResumeSchema, jd: JobDescriptionSchema) -> Dict[str, Any]:
        # Collect all resume skills and any skills mentioned in experience/projects
        all_resume_skills = set(resume.skills)
        
        # Also check project technologies
        for proj in resume.projects:
            for tech in proj.technologies:
                all_resume_skills.add(tech)
                
        resume_skill_list = list(all_resume_skills)

        # Match Required Skills
        matched_required, missing_required = match_skills_deterministically(
            resume_skill_list, jd.required_skills
        )

        # Match Preferred Skills
        matched_preferred, missing_preferred = match_skills_deterministically(
            resume_skill_list, jd.preferred_skills
        )

        # Match Keywords
        all_resume_text = f"{resume.summary} {' '.join(resume_skill_list)} " + " ".join([
            f"{e.title} {e.company} {' '.join(e.highlights)}" for e in resume.experience
        ])
        all_resume_text_lower = all_resume_text.lower()

        keywords_found = []
        keywords_missing = []
        for kw in jd.keywords:
            if kw.lower() in all_resume_text_lower:
                keywords_found.append(kw)
            else:
                keywords_missing.append(kw)

        # Calculate preliminary coverage ratios
        req_ratio = len(matched_required) / len(jd.required_skills) if jd.required_skills else 1.0
        pref_ratio = len(matched_preferred) / len(jd.preferred_skills) if jd.preferred_skills else 1.0

        return {
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
            "missing_preferred_skills": missing_preferred,
            "keywords_found": keywords_found,
            "keywords_missing": keywords_missing,
            "required_coverage_ratio": req_ratio,
            "preferred_coverage_ratio": pref_ratio,
        }
