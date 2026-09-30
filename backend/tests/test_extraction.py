import pytest
from backend.app.utils.text_cleaner import extract_emails, extract_phones, extract_urls, normalize_whitespace
from backend.app.utils.skill_normalizer import normalize_skill, normalize_skill_list, match_skills_deterministically
from backend.app.services.resume_extractor import ResumeExtractor
from backend.app.services.jd_extractor import JobDescriptionExtractor
from backend.app.models.schemas import ResumeSchema


def test_deterministic_text_cleaner(sample_resume_text):
    emails = extract_emails(sample_resume_text)
    phones = extract_phones(sample_resume_text)
    urls = extract_urls(sample_resume_text)

    assert "alex.morgan.fake@example.com" in emails
    assert len(phones) >= 1
    assert any("github.com" in u for u in urls)
    assert any("linkedin.com" in u for u in urls)


def test_skill_normalization():
    assert normalize_skill("Postgres") == "PostgreSQL"
    assert normalize_skill("postgresql") == "PostgreSQL"
    assert normalize_skill("ReactJS") == "React"
    assert normalize_skill("React.js") == "React"
    assert normalize_skill("NodeJS") == "Node.js"
    assert normalize_skill("node.js") == "Node.js"
    assert normalize_skill("js") == "JavaScript"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("fastapi") == "FastAPI"

    raw_skills = ["reactjs", "React", "Postgres", "postgresql", "AWS", "aws"]
    normalized = normalize_skill_list(raw_skills)
    assert normalized == ["React", "PostgreSQL", "AWS"]


def test_deterministic_skill_matching():
    candidate_skills = ["Python", "React", "PostgreSQL", "Docker"]
    required_jd_skills = ["Python", "PostgreSQL", "FastAPI", "Kubernetes"]

    matched, missing = match_skills_deterministically(candidate_skills, required_jd_skills)
    assert "Python" in matched
    assert "PostgreSQL" in matched
    assert "FastAPI" in missing
    assert "Kubernetes" in missing


def test_resume_extraction_pipeline(sample_resume_text):
    extractor = ResumeExtractor()
    resume_model = extractor.extract(sample_resume_text)

    assert isinstance(resume_model, ResumeSchema)
    assert "alex.morgan.fake@example.com" == resume_model.email
    assert len(resume_model.skills) > 0
    assert any(s in resume_model.skills for s in ["Python", "FastAPI", "PostgreSQL"])
    assert len(resume_model.experience) > 0
    assert len(resume_model.education) > 0


def test_job_description_extraction(sample_jd_text):
    jd_extractor = JobDescriptionExtractor()
    jd = jd_extractor.extract(sample_jd_text)

    assert len(jd.required_skills) > 0
    assert "Python" in jd.required_skills or "PostgreSQL" in jd.required_skills
    assert len(jd.responsibilities) > 0
    assert len(jd.experience_requirements) > 0
