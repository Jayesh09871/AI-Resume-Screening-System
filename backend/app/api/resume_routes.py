import os
import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, status
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.models.database_models import Resume, ResumeVersion
from backend.app.models.schemas import (
    ResumeSchema,
    ResumeUploadResponse,
    ResumeUpdateRequest,
    BaseATSScoreBreakdown,
)
from backend.app.services.resume_parser import ResumeParser
from backend.app.services.resume_extractor import ResumeExtractor
from backend.app.services.pdf_generator import PDFGenerator
from backend.app.services.resume_quality_scorer import ResumeQualityScorer
from backend.app.config import settings
from backend.app.utils.logger import logger

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and parse a resume file (PDF or DOCX).
    Extracts text, segments sections, converts to structured Pydantic model,
    and stores resume in the database.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    content = await file.read()
    file_size = len(content)

    try:
        parsed_doc = ResumeParser.parse_document(
            filename=file.filename,
            file_bytes=content,
            content_type=file.content_type or "",
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error parsing resume file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

    # Extract structured data
    extractor = ResumeExtractor()
    try:
        structured_data = extractor.extract(parsed_doc["raw_text"])
    except Exception as e:
        logger.error(f"Structured extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract structured data: {str(e)}")

    # Save to database
    db_resume = Resume(
        title=file.filename,
        raw_text=parsed_doc["raw_text"],
        structured_json=structured_data.model_dump(),
        version=1,
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    # Also save initial version
    initial_version = ResumeVersion(
        resume_id=db_resume.id,
        structured_json=structured_data.model_dump(),
    )
    db.add(initial_version)
    db.commit()

    # Compute baseline ATS score (No JD required)
    base_score = ResumeQualityScorer.evaluate(structured_data)

    return ResumeUploadResponse(
        resume_id=db_resume.id,
        raw_text=parsed_doc["raw_text"],
        page_count=parsed_doc["page_count"],
        detected_sections=parsed_doc["detected_sections"],
        warnings=parsed_doc["warnings"],
        structured_data=structured_data,
        base_ats_score=base_score,
    )


@router.post("/base-score", response_model=BaseATSScoreBreakdown)
def calculate_base_score(payload: ResumeSchema):
    """Calculate the baseline ATS quality score of a resume without needing a JD."""
    return ResumeQualityScorer.evaluate(payload)


@router.get("/{resume_id}/base-score", response_model=BaseATSScoreBreakdown)
def get_resume_base_score(resume_id: int, db: Session = Depends(get_db)):
    """Retrieve the baseline ATS score for an existing resume by ID."""
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    resume_model = ResumeSchema(**db_resume.structured_json)
    return ResumeQualityScorer.evaluate(resume_model)


@router.get("/{resume_id}", response_model=Dict[str, Any])
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Retrieve resume metadata and structured JSON."""
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {
        "id": db_resume.id,
        "title": db_resume.title,
        "raw_text": db_resume.raw_text,
        "structured_data": db_resume.structured_json,
        "version": db_resume.version,
        "created_at": db_resume.created_at.isoformat(),
        "updated_at": db_resume.updated_at.isoformat() if db_resume.updated_at else db_resume.created_at.isoformat(),
    }


@router.put("/{resume_id}", response_model=Dict[str, Any])
def update_resume(
    resume_id: int,
    payload: ResumeUpdateRequest,
    db: Session = Depends(get_db),
):
    """Update resume structured data and record version change."""
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    new_data = payload.structured_data.model_dump()
    db_resume.structured_json = new_data
    if payload.title:
        db_resume.title = payload.title
    db_resume.version += 1

    # Record new version history
    version_entry = ResumeVersion(
        resume_id=db_resume.id,
        structured_json=new_data,
    )
    db.add(version_entry)
    db.commit()
    db.refresh(db_resume)

    return {
        "message": "Resume updated successfully.",
        "id": db_resume.id,
        "version": db_resume.version,
        "structured_data": db_resume.structured_json,
    }


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    """Delete a resume and associated versions/analyses."""
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    db.delete(db_resume)
    db.commit()
    return {"message": "Resume deleted successfully."}


@router.post("/{resume_id}/pdf")
def generate_resume_pdf(
    resume_id: int,
    template: str = "classic_ats",
    db: Session = Depends(get_db)
):
    """Generate and return an ATS-optimized PDF resume via ReportLab (classic_ats, modern_tech, executive)."""
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        resume_model = ResumeSchema(**db_resume.structured_json)
        pdf_bytes = PDFGenerator.generate(resume_model, template=template)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    filename = f"{resume_model.name.replace(' ', '_') or 'Resume'}_{template}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
