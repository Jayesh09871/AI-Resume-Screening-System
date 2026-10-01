from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.models.database_models import Analysis, Resume, JobDescription

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=List[Dict[str, Any]])
def get_analysis_history(db: Session = Depends(get_db)):
    """Retrieve history of all resume-job analyses."""
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).all()
    history_items = []

    for a in analyses:
        resume_title = a.resume.title if a.resume else "Direct Input Resume"
        jd_title = a.job_description.title if a.job_description else "Target Job"
        match_data = a.match_data or {}
        breakdown = match_data.get("breakdown", {})

        history_items.append({
            "id": a.id,
            "resume_id": a.resume_id,
            "resume_title": resume_title,
            "jd_id": a.jd_id,
            "jd_title": jd_title,
            "overall_score": breakdown.get("overall_score", 0),
            "breakdown": breakdown,
            "matched_skills_count": len(match_data.get("matched_required_skills", [])),
            "missing_skills_count": len(match_data.get("missing_required_skills", [])),
            "suggestions_count": len(a.suggestions) if a.suggestions else 0,
            "created_at": a.created_at.isoformat(),
        })

    return history_items


@router.delete("/{analysis_id}")
def delete_analysis_record(analysis_id: int, db: Session = Depends(get_db)):
    """Delete an analysis record and its associated resume from history."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    resume_id = analysis.resume_id
    resume = db.query(Resume).filter(Resume.id == resume_id).first() if resume_id else None

    if resume:
        # Cascade-deletes analysis, resume_versions, and the resume itself
        db.delete(resume)
    else:
        db.delete(analysis)

    db.commit()
    return {
        "message": "Analysis and associated resume deleted from history.",
        "analysis_id": analysis_id,
        "resume_id": resume_id,
    }

