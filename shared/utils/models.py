from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass(slots=True)
class AutomationMetadata:
    name: str
    description: str
    domain: str
    version: str = "1.0.0"


@dataclass(slots=True)
class AutomationResult:
    automation_name: str
    status: ExecutionStatus
    rows_extracted: int = 0
    rows_transformed: int = 0
    rows_loaded: int = 0
    details: dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    error_message: str | None = None


@dataclass(slots=True)
class ExecutionRecord:
    automation_name: str
    status: ExecutionStatus
    started_at: datetime
    id: UUID = field(default_factory=uuid4)
    finished_at: datetime | None = None
    retries: int = 0
    payload: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
