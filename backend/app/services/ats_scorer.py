from typing import Dict, Any, List
from backend.app.models.schemas import (
    ResumeSchema,
    JobDescriptionSchema,
    ATSScoreBreakdown,
    MatchResultSchema,
    SemanticMatchItem,
)
from backend.app.services.skill_matcher import SkillMatcher
from backend.app.services.semantic_matcher import SemanticMatcher


class ATSScorer:
    """
    Computes an explainable ATS Compatibility Score (0-100) combining:
    1. Required Skill Coverage (Weight: 40%)
    2. Preferred Skill Coverage (Weight: 15%)
    3. Experience Relevance (Weight: 25%)
    4. Semantic Similarity (Weight: 20%)
    """

    def __init__(self):
        self.skill_matcher = SkillMatcher()
        self.semantic_matcher = SemanticMatcher()

    def calculate_experience_relevance(self, resume: ResumeSchema, jd: JobDescriptionSchema) -> int:
        """
        Evaluate how relevant candidate's work experience is to the JD:
        - Presence of job titles matching or related to JD title/domain
        - Keyword and technology occurrences inside experience bullet points
        - Overall depth of experience entries
        """
        if not resume.experience:
            return 30  # Fresh graduate / entry level base score

        total_bullets = 0
        relevant_bullets = 0

        target_keywords = set([k.lower() for k in jd.required_skills + jd.technologies + jd.keywords])
        if not target_keywords:
            target_keywords = {"software", "engineer", "developer", "data", "system", "code"}

        for exp in resume.experience:
            # Check title relevance
            if jd.title and any(w in exp.title.lower() for w in jd.title.lower().split() if len(w) > 3):
                relevant_bullets += 1

            for h in exp.highlights:
                total_bullets += 1
                h_lower = h.lower()
                if any(kw in h_lower for kw in target_keywords):
                    relevant_bullets += 1

        if total_bullets == 0:
            return 30 if len(resume.experience) > 0 else 10

        ratio = relevant_bullets / max(1, total_bullets)
        # Dynamic scale reflecting actual depth of matched project/job highlights
        score = int(min(100, max(10, round(ratio * 100))))
        return score

    def evaluate(self, resume: ResumeSchema, jd: JobDescriptionSchema) -> MatchResultSchema:
        # 1. Deterministic Skill Matching
        skill_res = self.skill_matcher.match(resume, jd)
        
        req_count = len(jd.required_skills)
        matched_req_count = len(skill_res["matched_required_skills"])
        # If JD has required skills, evaluate ratio; otherwise score baseline
        required_skill_score = int((matched_req_count / req_count) * 100) if req_count > 0 else 60

        pref_count = len(jd.preferred_skills)
        matched_pref_count = len(skill_res["matched_preferred_skills"])
        preferred_skill_score = int((matched_pref_count / pref_count) * 100) if pref_count > 0 else 50

        # 2. Experience Relevance
        experience_relevance = self.calculate_experience_relevance(resume, jd)

        # 3. Semantic Similarity via sentence-transformers
        semantic_res = self.semantic_matcher.match(resume, jd)
        semantic_similarity = semantic_res["semantic_score"]
        semantic_matches = semantic_res["semantic_matches"]

        # 4. Weighted Formula
        # Required (40%), Preferred (15%), Experience (25%), Semantic (20%)
        overall = int(
            round(
                (0.40 * required_skill_score)
                + (0.15 * preferred_skill_score)
                + (0.25 * experience_relevance)
                + (0.20 * semantic_similarity)
            )
        )
        overall = min(100, max(0, overall))

        breakdown = ATSScoreBreakdown(
            overall_score=overall,
            required_skill_score=required_skill_score,
            preferred_skill_score=preferred_skill_score,
            experience_relevance=experience_relevance,
            semantic_similarity=semantic_similarity,
            disclaimer="This is an application-generated compatibility score and NOT a guarantee of passing commercial ATS systems."
        )

        return MatchResultSchema(
            breakdown=breakdown,
            matched_required_skills=skill_res["matched_required_skills"],
            missing_required_skills=skill_res["missing_required_skills"],
            matched_preferred_skills=skill_res["matched_preferred_skills"],
            missing_preferred_skills=skill_res["missing_preferred_skills"],
            keywords_found=skill_res["keywords_found"],
            keywords_missing=skill_res["keywords_missing"],
            semantic_matches=semantic_matches,
        )
