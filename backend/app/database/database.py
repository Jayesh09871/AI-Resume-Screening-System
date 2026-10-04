import os
import socket
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings
from backend.app.utils.logger import logger


def get_database_url() -> str:
    """
    Retrieve and format PostgreSQL connection URL.
    Reads from environment variable DATABASE_URL or settings.DATABASE_URL.
    Ensures compatibility with SQLAlchemy 2.0 (replaces postgres:// with postgresql://).
    Resolves Render internal hostnames to external domain if executed outside Render's private network.
    """
    url = os.getenv("DATABASE_URL") or settings.DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL is not set. Please configure DATABASE_URL in your .env or environment.")

    # SQLAlchemy 1.4+ / 2.0 requires postgresql:// instead of legacy postgres://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # Render internal hostnames (e.g. dpg-xxxx-a with no dots) only resolve within Render's internal VPC.
    # When connecting from local development machines, route to the external Render hostname with sslmode=require.
    try:
        parsed = urlparse(url)
        if parsed.hostname and parsed.hostname.startswith("dpg-") and "." not in parsed.hostname:
            try:
                socket.gethostbyname(parsed.hostname)
            except socket.gaierror:
                ext_host = f"{parsed.hostname}.oregon-postgres.render.com"
                netloc = parsed.netloc.replace(parsed.hostname, ext_host)
                query = parsed.query
                if "sslmode" not in query:
                    query = f"{query}&sslmode=require" if query else "sslmode=require"
                parsed = parsed._replace(netloc=netloc, query=query)
                url = urlunparse(parsed)
    except Exception:
        pass

    return url


DATABASE_URL = get_database_url()

# Configure SQLAlchemy engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database."""
    try:
        # Import models so Base.metadata knows about all tables
        import backend.app.models.database_models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        masked_host = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "configured host"
        logger.info(f"Database initialized successfully with host: {masked_host}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e
