from __future__ import annotations

import logging
from typing import Any

try:
    import structlog
except ModuleNotFoundError:  # pragma: no cover - environment fallback
    structlog = None


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para melhor legibilidade no terminal."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        log_message = super().format(record)
        return f"{color}{log_message}{self.RESET}"


def setup_structured_logging(level: str = "INFO", sentry_dsn: str = "", app_env: str = "development") -> None:
    """Configura logging estruturado com melhor formatação visual."""
    logging_level = getattr(logging, level.upper(), logging.INFO)
    
    # Cria handler com formatação melhorada
    handler = logging.StreamHandler()
    format_str = "[%(asctime)s] [%(levelname)s] %(message)s"
    formatter = ColoredFormatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    
    # Configura root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    from shared.logging.sentry import init_sentry
    init_sentry(dsn=sentry_dsn, environment=app_env)

    if structlog is None:
        return
    
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
    """Registra evento do pipeline com formatação estruturada e espaçamento visual."""
    # Prepara payload com informações do evento
    payload = {
        "pipeline": pipeline,
        "step": step,
        "status": status,
        "message": message,
    }
    
    if duration_ms is not None:
        payload["duration_ms"] = f"{duration_ms}ms"
    
    if metadata:
        payload.update(metadata)
    
    # Formata a mensagem de log de forma legível
    separator = "┌" + "─" * 98 + "┐"
    footer = "└" + "─" * 98 + "┘"
    
    if structlog is None:
        # Fallback para logging padrão quando structlog não está disponível
        logger_instance = logging.getLogger(pipeline)
        logger_instance.info("")  # Linha em branco para separação
        logger_instance.info(separator)
        logger_instance.info(f"  Pipeline: {pipeline} | Step: {step} | Status: {status}")
        logger_instance.info(f"  Message: {message}")
        if duration_ms is not None:
            logger_instance.info(f"  Duration: {duration_ms}ms")
        if metadata:
            for key, value in metadata.items():
                logger_instance.info(f"  {key}: {value}")
        logger_instance.info(footer)
        logger_instance.info("")  # Linha em branco para separação
        return
    
    # Com structlog
    logger_instance = structlog.get_logger(pipeline)
    logger_instance.info("")  # Linha em branco
    logger_instance.info(separator)
    
    # Formata informações principais
    status_display = f"[{status.upper()}]" if status else ""
    logger_instance.info(f"  {status_display} {message}")
    logger_instance.info(f"  Pipeline: {pipeline} | Step: {step}")
    
    if duration_ms is not None:
        logger_instance.info(f"  Duration: {duration_ms}ms")
    
    if metadata:
        for key, value in metadata.items():
            logger_instance.info(f"  {key}: {value}")
    
    logger_instance.info(footer)
    logger_instance.info("")  # Linha em branco
