from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, validate_assignment=True)


class PipelineStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class LogStatus(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RawPayload(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    extraction_date: datetime
    source: str
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessRecord(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    data_hora: datetime
    funcao_acessada: str
    proprietario: str | None = None
    local: str | None = None
    acessou_pelo: str | None = None
    acessou_telefone: bool | None = None
    usuario: str
    filial: str | None = None
    codigo_imovel: str
    endereco: str | None = None
    tipo_imovel: str | None = None
    bairro: str | None = None
    dormitorios: int | None = None
    acesso: str | None = None
    origem_acesso: str = "Midas Web"
    data_carga: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PipelineExecution(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    pipeline_name: str
    started_at: datetime
    finished_at: datetime | None = None
    status: PipelineStatus = PipelineStatus.RUNNING
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    duration_seconds: float | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PipelineLog(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    execution_id: UUID | None = None
    pipeline_name: str
    step: str
    status: LogStatus
    message: str
    duration_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PipelineAlert(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    execution_id: UUID | None = None
    pipeline_name: str
    alert_type: str
    severity: AlertSeverity
    title: str
    message: str | None = None
    sent: bool = False
    sent_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IndicadorAcesso(DomainModel):
    id: UUID = Field(default_factory=uuid4)
    referencia: str
    filial: str | None = None
    usuario: str | None = None
    bairro: str | None = None
    tipo_imovel: str | None = None
    funcao_acessada: str | None = None
    total_acessos: int = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QualityReport(DomainModel):
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    unknown_functionalities: list[str] = Field(default_factory=list)
    minimum_required: int = 1
    is_valid: bool = True
