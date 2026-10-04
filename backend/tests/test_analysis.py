import pytest
from backend.app.services.recommendation_engine import RecommendationEngine
from backend.app.services.ats_scorer import ATSScorer
from backend.app.services.llm_provider import RuleBasedNLPProvider
from backend.app.models.schemas import JobDescriptionSchema


def test_recommendation_engine(sample_resume_model):
    jd = JobDescriptionSchema(
        title="Senior Python Backend Developer",
        required_skills=["Python", "FastAPI", "PostgreSQL", "Kubernetes"],
        preferred_skills=["GraphQL"],
        keywords=["microservices", "distributed systems"],
    )
    scorer = ATSScorer()
    match_result = scorer.evaluate(sample_resume_model, jd)

    rec_engine = RecommendationEngine()
    suggestions = rec_engine.generate(sample_resume_model, jd, match_result)

    assert len(suggestions) >= 3
    for s in suggestions:
        assert s.recommendation
        assert s.reason
        assert s.resume_evidence
        assert s.related_jd_requirement
        assert s.category in ["keyword", "summary", "experience_bullet", "project", "skill_priority"]


def test_bullet_point_improvement():
    provider = RuleBasedNLPProvider()
    original = "worked on database queries"
    res = provider.improve_bullet_point(original, target_role="Backend Developer")

    assert res["original_bullet"] == original
    assert len(res["improved_bullet"]) > len(original)
    assert res["reasoning"]
    assert "metric" in res["notes"].lower()


def test_linguistic_analyzer(sample_resume_model):
    from backend.app.services.linguistic_analyzer import LinguisticAnalyzer
    res = LinguisticAnalyzer.analyze(sample_resume_model)
    assert 0 <= res["linguistic_score"] <= 100
    assert len(res["action_verbs_found"]) > 0
    assert "total_bullets_count" in res
    assert res["quantified_bullets_count"] >= 0
    assert res["overall_feedback"]


def test_api_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "healthy" in data["database"]


def test_api_resume_upload_and_lifecycle(client, sample_pdf_bytes):
    # 1. Upload
    files = {"file": ("test_resume.pdf", sample_pdf_bytes, "application/pdf")}
    upload_res = client.post("/api/resumes/upload", files=files)
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    resume_id = upload_data["resume_id"]
    assert resume_id is not None
    assert upload_data["structured_data"]["email"] == "alex.morgan.fake@example.com"

    # JD Mandatory First: Do NOT generate ATS score on upload
    assert upload_data.get("base_ats_score") is None

    # 2. Retrieve
    get_res = client.get(f"/api/resumes/{resume_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == resume_id

    # 3. Update
    structured = upload_data["structured_data"]
    structured["summary"] = "Updated professional summary for testing."
    put_res = client.put(f"/api/resumes/{resume_id}", json={"structured_data": structured})
    assert put_res.status_code == 200
    assert put_res.json()["version"] == 2

    # 4. Analyze with Mandatory Job Description (Generates ATS & Match % based on JD)
    analyze_payload = {
        "resume_id": resume_id,
        "jd_text": "We need a Python and FastAPI engineer with PostgreSQL experience."
    }
    analyze_res = client.post("/api/analyze", json=analyze_payload)
    assert analyze_res.status_code == 200
    analysis_data = analyze_res.json()
    match_data = analysis_data["match_data"]
    assert match_data["breakdown"]["overall_score"] > 0
    assert match_data["match_percentage"] > 0
    assert "experience_match" in match_data
    assert "education_match" in match_data
    assert "strengths" in match_data
    assert "required_skills" in match_data
    assert len(analysis_data["suggestions"]) > 0

    # 5. Fast Interview Preparation Generation based on Resume + JD
    interview_payload = {
        "resume_id": resume_id,
        "resume_data": structured,
        "jd_text": "We need a Python and FastAPI engineer with PostgreSQL experience.",
        "matched_skills": match_data["matched_required_skills"],
        "missing_skills": match_data["missing_required_skills"],
        "target_role": "Python FastAPI Engineer",
    }
    interview_res = client.post("/api/interview-prep", json=interview_payload)
    assert interview_res.status_code == 200
    interview_data = interview_res.json()
    assert len(interview_data["technical_questions"]) == 5
    assert len(interview_data["behavioral_questions"]) == 3
    for q in interview_data["technical_questions"] + interview_data["behavioral_questions"]:
        assert "question" in q and len(q["question"]) > 0
        assert "suggested_answer" in q and len(q["suggested_answer"]) > 0
        assert "tips" in q and len(q["tips"]) > 0

    # 6. History
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1

    # 7. Delete from history and verify cascade delete of resume
    analysis_id = analysis_data["analysis_id"]
    del_hist = client.delete(f"/api/history/{analysis_id}")
    assert del_hist.status_code == 200
    assert del_hist.json()["analysis_id"] == analysis_id

    # Verify resume is no longer found in backend
    res_after_delete = client.get(f"/api/resumes/{resume_id}")
    assert res_after_delete.status_code == 404



def test_resume_quality_scorer(sample_resume_model):
    from backend.app.services.resume_quality_scorer import ResumeQualityScorer
    result = ResumeQualityScorer.evaluate(sample_resume_model)
    assert 0 <= result.overall_score <= 100
    assert result.section_score > 0
    assert result.contact_score > 0
    assert result.linguistic_score > 0
    assert len(result.strengths) > 0
