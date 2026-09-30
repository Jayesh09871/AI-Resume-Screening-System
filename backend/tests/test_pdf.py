import fitz
from backend.app.services.pdf_generator import PDFGenerator
from backend.app.models.schemas import ResumeSchema


def test_pdf_generation(sample_resume_model):
    pdf_bytes = PDFGenerator.generate(sample_resume_model)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")

    # Verify that the generated PDF can be read back by PyMuPDF and contains text
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    assert len(doc) >= 1
    extracted_text = doc[0].get_text()
    doc.close()

    assert "ALEXANDER MORGAN" in extracted_text
    assert "FastAPI" in extracted_text
    assert "CloudScale Tech" in extracted_text


def test_api_pdf_download_endpoint(client, sample_pdf_bytes):
    # Upload first
    files = {"file": ("resume_for_pdf.pdf", sample_pdf_bytes, "application/pdf")}
    upload_res = client.post("/api/resumes/upload", files=files)
    assert upload_res.status_code == 200
    resume_id = upload_res.json()["resume_id"]

    # Download generated ATS PDF
    pdf_res = client.post(f"/api/resumes/{resume_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")
