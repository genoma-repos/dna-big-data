from __future__ import annotations

import json
import logging
from datetime import datetime, timezone


class ColoredFormatter(logging.Formatter):
    """Formatter padrão com formatação legível para console."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level = record.levelname
        color = self.COLORS.get(level, self.RESET)
        message = record.getMessage()
        
        formatted = f"[{timestamp}] [{level:8}] {message}"
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return f"{color}{formatted}{self.RESET}"


class JsonFormatter(logging.Formatter):
    """Formatter estruturado em JSON para logs mais estruturados."""
    
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, indent=2)


def setup_logging(level: str = "INFO", use_json: bool = False) -> None:
    """Configura o sistema de logging com formatação legível.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Se True, usa formatação JSON; caso contrário, usa formatação colorida
    """
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level.upper())

    handler = logging.StreamHandler()
    formatter = JsonFormatter() if use_json else ColoredFormatter()
    handler.setFormatter(formatter)
    root.addHandler(handler)
