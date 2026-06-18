from __future__ import annotations

import logging
from typing import Any

import structlog


def setup_structured_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def log_event(pipeline: str, step: str, status: str, message: str, duration_ms: int | None = None, **metadata: Any) -> None:
    logger = structlog.get_logger(pipeline)
    payload = {"pipeline": pipeline, "step": step, "status": status, "message": message}
    if duration_ms is not None:
        payload["duration_ms"] = duration_ms
    if metadata:
        payload.update(metadata)
    logger.info("pipeline_event", **payload)
