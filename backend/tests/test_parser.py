import pytest
from backend.app.services.resume_parser import ResumeParser


def test_pdf_extraction(sample_pdf_bytes):
    text, page_count, warnings = ResumeParser.parse_pdf(sample_pdf_bytes)
    assert page_count >= 1
    assert "ALEXANDER MORGAN" in text
    assert "FastAPI" in text
    assert isinstance(warnings, list)


def test_docx_extraction(sample_docx_bytes):
    text, page_count, warnings = ResumeParser.parse_docx(sample_docx_bytes)
    assert page_count >= 1
    assert "ALEXANDER MORGAN" in text
    assert "FastAPI" in text
    assert isinstance(warnings, list)


def test_section_detection(sample_resume_text):
    sections = ResumeParser.detect_sections(sample_resume_text)
    assert "Summary" in sections
    assert "Skills" in sections
    assert "Experience" in sections
    assert "Education" in sections
    assert "Projects" in sections


def test_corrupted_file_handling():
    corrupted_bytes = b"Not a valid PDF or DOCX file content"
    with pytest.raises(ValueError) as exc:
        ResumeParser.parse_pdf(corrupted_bytes)
    assert "corrupted" in str(exc.value).lower()


def test_file_validation_size_limit():
    # Test valid
    ResumeParser.validate_file("resume.pdf", 1024, "application/pdf", max_size_mb=5)

    # Test oversized
    with pytest.raises(ValueError) as exc:
        ResumeParser.validate_file("resume.pdf", 6 * 1024 * 1024, "application/pdf", max_size_mb=5)
    assert "exceeds" in str(exc.value).lower()

    # Test invalid extension
    with pytest.raises(ValueError) as exc:
        ResumeParser.validate_file("resume.exe", 1024, "application/octet-stream")
    assert "unsupported" in str(exc.value).lower()
