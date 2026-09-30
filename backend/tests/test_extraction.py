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


def test_jd_scraper_ssrf_and_validation():
    from backend.app.services.jd_scraper import JobDescriptionScraper, JDScraperError
    # Test invalid schemes
    with pytest.raises(JDScraperError):
        JobDescriptionScraper.validate_url("ftp://example.com/job")
    with pytest.raises(JDScraperError):
        JobDescriptionScraper.validate_url("file:///etc/passwd")

    # Test SSRF block on localhost and private networks
    with pytest.raises(JDScraperError):
        JobDescriptionScraper.validate_url("http://localhost:8000/api")
    with pytest.raises(JDScraperError):
        JobDescriptionScraper.validate_url("http://127.0.0.1:8000")
    with pytest.raises(JDScraperError):
        JobDescriptionScraper.validate_url("http://192.168.1.50/job")
    with pytest.raises(JDScraperError):
        JobDescriptionScraper.validate_url("http://10.0.0.1/admin")


def test_jd_scraper_json_ld_extraction():
    from bs4 import BeautifulSoup
    from backend.app.services.jd_scraper import JobDescriptionScraper

    mock_html = """
    <html>
    <head>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org/",
      "@type": "JobPosting",
      "title": "Principal Distributed Systems Engineer",
      "hiringOrganization": { "@type": "Organization", "name": "Stripe" },
      "description": "<p>We are seeking a Principal Engineer to lead our core transaction infrastructure.</p><ul><li>10+ years backend engineering</li><li>Go, Python, and distributed DBs</li><li>High-throughput systems architecture</li></ul>"
    }
    </script>
    </head>
    <body><h1>Stripe Careers</h1></body>
    </html>
    """
    soup = BeautifulSoup(mock_html, "html.parser")
    result = JobDescriptionScraper.extract_from_json_ld(soup)
    assert result is not None
    assert result["title"] == "Principal Distributed Systems Engineer"
    assert result["company"] == "Stripe"
    assert "transaction infrastructure" in result["jd_text"]
    assert "- 10+ years backend engineering" in result["jd_text"]


def test_jd_scraper_dom_selectors():
    from bs4 import BeautifulSoup
    from backend.app.services.jd_scraper import JobDescriptionScraper

    greenhouse_html = """
    <div id="header">
      <h1 class="app-title">Lead Site Reliability Engineer</h1>
      <span class="company-name">at Datadog</span>
    </div>
    <div id="content">
      <p>Datadog is building world-class monitoring software.</p>
      <h3>Requirements</h3>
      <ul>
        <li>Extensive experience with Kubernetes and Linux internals</li>
        <li>Proficiency in Python or Go</li>
      </ul>
    </div>
    """
    soup = BeautifulSoup(greenhouse_html, "html.parser")
    res = JobDescriptionScraper.extract_from_specialized_selectors(soup, "https://boards.greenhouse.io/datadog/jobs/123")
    assert res is not None
    assert "Lead Site Reliability Engineer" in res["title"]
    assert "Datadog" in res["company"]
    assert "Kubernetes and Linux" in res["jd_text"]

