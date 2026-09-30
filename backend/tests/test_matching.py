import pytest
from backend.app.services.skill_matcher import SkillMatcher
from backend.app.services.semantic_matcher import SemanticMatcher
from backend.app.services.ats_scorer import ATSScorer
from backend.app.models.schemas import JobDescriptionSchema


def test_skill_matcher(sample_resume_model):
    jd = JobDescriptionSchema(
        title="Backend Engineer",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Go"],
        preferred_skills=["Docker", "Kubernetes"],
        keywords=["microservices", "API"],
    )
    result = SkillMatcher.match(sample_resume_model, jd)
    assert "Python" in result["matched_required_skills"]
    assert "FastAPI" in result["matched_required_skills"]
    assert "PostgreSQL" in result["matched_required_skills"]
    assert "Docker" in result["matched_preferred_skills"]
    assert "Kubernetes" in result["missing_preferred_skills"]
    assert result["required_coverage_ratio"] >= 0.75


def test_semantic_matcher(sample_resume_model):
    matcher = SemanticMatcher()
    jd = JobDescriptionSchema(
        title="Python Backend Developer",
        required_skills=["Python", "FastAPI"],
        responsibilities=["Design and deploy scalable microservice architectures."],
        experience_requirements=["Experience handling production database optimizations."],
    )
    res = matcher.match(sample_resume_model, jd)
    assert 0 <= res["semantic_score"] <= 100
    assert len(res["semantic_matches"]) > 0

    # Verify that each match has requirement, resume evidence, and status
    for item in res["semantic_matches"]:
        assert item.jd_requirement
        assert item.resume_evidence
        assert 0.0 <= item.similarity_score <= 1.0
        assert item.status in ["strong", "moderate", "weak"]


def test_ats_scorer(sample_resume_model):
    scorer = ATSScorer()
    jd = JobDescriptionSchema(
        title="Senior Backend Engineer",
        required_skills=["Python", "FastAPI", "PostgreSQL"],
        preferred_skills=["Docker", "AWS"],
        technologies=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        responsibilities=["Build high-throughput microservices."],
        experience_requirements=["3+ years backend software development."],
        keywords=["microservices", "FastAPI", "PostgreSQL"],
    )
    match_result = scorer.evaluate(sample_resume_model, jd)
    breakdown = match_result.breakdown

    assert 0 <= breakdown.overall_score <= 100
    assert 0 <= breakdown.required_skill_score <= 100
    assert 0 <= breakdown.preferred_skill_score <= 100
    assert 0 <= breakdown.experience_relevance <= 100
    assert 0 <= breakdown.semantic_similarity <= 100
    assert len(match_result.matched_required_skills) == 3
    assert len(match_result.missing_required_skills) == 0
