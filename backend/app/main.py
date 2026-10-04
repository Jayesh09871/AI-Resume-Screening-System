import sys
import os
import time
from contextlib import asynccontextmanager

# Ensure project root and backend directories are in sys.path for cloud deployment
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_current_dir)
_project_root = os.path.dirname(_backend_dir)
for _path in [_project_root, _backend_dir]:
    if _path and _path not in sys.path:
        sys.path.insert(0, _path)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.config import settings
from backend.app.database.database import init_db, engine
from backend.app.utils.logger import logger
from backend.app.api.resume_routes import router as resume_router
from backend.app.api.analysis_routes import router as analysis_router
from backend.app.api.history_routes import router as history_router
from backend.app.api.interview_routes import router as interview_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    logger.info("Initializing application and database...")
    init_db()
    # Pre-warm embedding model only in local dev if explicitly requested (disabled on Render to keep memory under 512Mi)
    if not os.getenv("RENDER") and os.getenv("PREWARM_EMBEDDINGS", "false").lower() in ("true", "1"):
        try:
            from backend.app.services.semantic_matcher import get_embedding_model
            get_embedding_model()
            logger.info("Embedding model pre-warmed successfully.")
        except Exception as e:
            logger.warning(f"Could not pre-warm embedding model: {e}")
    yield
    # Shutdown
    logger.info("Application shutting down...")


app = FastAPI(
    title="AI Resume Screening & Builder API",
    description="Explainable ATS compatibility screening, semantic alignment matching, and professional PDF generation.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing & Observability Middleware
@app.middleware("http")
async def add_process_time_and_logging(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time-Seconds"] = str(round(process_time, 4))
        
        # Log request without sensitive data
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} in {round(process_time, 4)}s",
            extra={
                "extra_data": {
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": round(process_time, 4),
                }
            },
        )
        return response
    except Exception as exc:
        process_time = time.time() - start_time
        logger.error(
            f"Unhandled error in {request.method} {request.url.path}: {str(exc)}",
            extra={
                "extra_data": {
                    "method": request.method,
                    "endpoint": request.url.path,
                    "duration_seconds": round(process_time, 4),
                    "error": str(exc),
                }
            },
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please verify your request or try again."},
        )


# Health check endpoints
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    # Verify DB connectivity
    db_status = "healthy"
    try:
        with engine.connect() as conn:
            pass
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "ok",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "groq_configured": bool(settings.GROQ_API_KEY),
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "version": "1.0.0",
    }


# Include Routers with /api prefix
app.include_router(resume_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(interview_router, prefix="/api")