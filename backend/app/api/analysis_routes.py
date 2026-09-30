from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.models.database_models import Resume, JobDescription, Analysis
from backend.app.models.schemas import (
    AnalyzeRequest,
    AnalysisResponse,
    ResumeSchema,
    BulletImprovementRequest,
    BulletImprovementResponse,
    JDScrapeRequest,
    JDScrapeResponse,
)
from backend.app.services.jd_extractor import JobDescriptionExtractor
from backend.app.services.jd_scraper import JobDescriptionScraper, JDScraperError
from backend.app.services.ats_scorer import ATSScorer
from backend.app.services.recommendation_engine import RecommendationEngine
from backend.app.services.linguistic_analyzer import LinguisticAnalyzer
from backend.app.services.llm_provider import get_llm_provider
from backend.app.utils.logger import logger

router = APIRouter(tags=["Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_resume_against_jd(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
):
    """
    Full Analysis Pipeline:
    1. Retrieve or parse Resume
    2. Extract and structure Job Description requirements
    3. Deterministic skill & alias matching
    4. Semantic matching via all-MiniLM-L6-v2 embeddings
    5. Calculate explainable ATS score (0-100)
    6. Generate evidence-grounded recommendations
    7. Persist analysis record
    """
    resume_obj: ResumeSchema

    # 1. Resolve Resume
    if payload.resume_id:
        db_resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()
        if not db_resume:
            raise HTTPException(status_code=404, detail="Resume ID not found.")
        resume_obj = ResumeSchema(**db_resume.structured_json)
        resume_id = db_resume.id
    elif payload.resume_data:
        resume_obj = payload.resume_data
        resume_id = None
    else:
        raise HTTPException(status_code=400, detail="Either resume_id or resume_data must be provided.")

    # 2. Extract JD Requirements
    jd_extractor = JobDescriptionExtractor()
    try:
        jd_schema = jd_extractor.extract(payload.jd_text)
    except Exception as e:
        logger.error(f"Failed to extract JD: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse Job Description: {str(e)}")

    # Save Job Description in DB
    db_jd = JobDescription(
        title=jd_schema.title,
        text=payload.jd_text,
        structured_json=jd_schema.model_dump(),
    )
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)

    # 3. Match & Score ATS
    scorer = ATSScorer()
    try:
        match_result = scorer.evaluate(resume_obj, jd_schema)
    except Exception as e:
        logger.error(f"Error during ATS scoring: {e}")
        raise HTTPException(status_code=500, detail=f"ATS scoring failed: {str(e)}")

    # 4. Generate AI Recommendations
    rec_engine = RecommendationEngine()
    try:
        suggestions = rec_engine.generate(resume_obj, jd_schema, match_result)
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        suggestions = []

    # 5. Linguistic & Action Verb Quality Analysis
    linguistic_data = LinguisticAnalyzer.analyze(resume_obj)

    # 6. Persist Analysis record
    db_analysis = Analysis(
        resume_id=resume_id,
        jd_id=db_jd.id,
        match_data=match_result.model_dump(),
        suggestions=[s.model_dump() for s in suggestions],
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    return AnalysisResponse(
        analysis_id=db_analysis.id,
        resume_id=resume_id,
        jd_id=db_jd.id,
        match_data=match_result,
        suggestions=suggestions,
        linguistic_analysis=linguistic_data,
        created_at=db_analysis.created_at.isoformat(),
    )


@router.post("/improve", response_model=BulletImprovementResponse)
def improve_bullet(payload: BulletImprovementRequest):
    """
    Improve a weak bullet point following the Google XYZ formula:
    'Accomplished X as measured by Y, by doing Z' without inventing metrics.
    """
    llm = get_llm_provider()
    try:
        result = llm.improve_bullet_point(
            bullet=payload.bullet_text,
            target_role=payload.target_role or "",
            context=payload.context or "",
        )
        return BulletImprovementResponse(**result)
    except Exception as e:
        logger.warning(f"Groq bullet improvement encountered: {e}. Falling back to RuleBasedNLPProvider.")
        try:
            from backend.app.services.llm_provider import RuleBasedNLPProvider
            fallback = RuleBasedNLPProvider()
            result = fallback.improve_bullet_point(
                bullet=payload.bullet_text,
                target_role=payload.target_role or "",
                context=payload.context or "",
            )
            return BulletImprovementResponse(**result)
        except Exception as inner_e:
            logger.error(f"Fallback also failed: {inner_e}")
            raise HTTPException(status_code=500, detail=f"Failed to improve bullet point: {str(e)}")


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_by_id(analysis_id: int, db: Session = Depends(get_db)):
    """Fetch stored analysis by ID."""
    db_analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not db_analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return AnalysisResponse(
        analysis_id=db_analysis.id,
        resume_id=db_analysis.resume_id,
        jd_id=db_analysis.jd_id,
        match_data=db_analysis.match_data,
        suggestions=db_analysis.suggestions,
        created_at=db_analysis.created_at.isoformat(),
    )


@router.post("/scrape-jd", response_model=JDScrapeResponse)
@router.post("/jd/scrape", response_model=JDScrapeResponse)
def scrape_job_description(payload: JDScrapeRequest):
    """
    Auto-fetch and extract a job description from a public URL (Greenhouse, Lever, LinkedIn, etc.).
    Extracts job title, company, and clean plaintext job description without HTML or boilerplate.
    """
    try:
        scraped_data = JobDescriptionScraper.scrape(payload.url)
        return JDScrapeResponse(**scraped_data)
    except JDScraperError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error scraping JD from {payload.url}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while scraping the job description: {str(e)}"
        )

