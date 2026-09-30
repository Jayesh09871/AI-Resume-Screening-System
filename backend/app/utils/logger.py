import logging
import sys
import json
import time
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """
    Format logs as JSON objects for structured observability while masking sensitive details.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include structured extra data if present
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            # Sanitize to never leak keys or full resumes
            sanitized = {}
            for k, v in record.extra_data.items():
                if any(secret in k.lower() for secret in ["key", "secret", "token", "password", "auth"]):
                    sanitized[k] = "[REDACTED]"
                elif k in ["raw_text", "resume_content", "document_text"] and isinstance(v, str):
                    sanitized[k] = f"[TEXT LENGTH: {len(v)} chars]"
                else:
                    sanitized[k] = v
            log_obj["data"] = sanitized

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def get_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = get_logger("ai-resume-screening")


def log_llm_call(
    provider: str,
    model: str,
    latency: float,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    retry_count: int = 0,
    error: Optional[str] = None
):
    extra = {
        "llm_provider": provider,
        "model_name": model,
        "llm_latency_seconds": round(latency, 3),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "retry_count": retry_count,
        "error": error
    }
    if error:
        logger.error("LLM Call Failed", extra={"extra_data": extra})
    else:
        logger.info("LLM Call Successful", extra={"extra_data": extra})
