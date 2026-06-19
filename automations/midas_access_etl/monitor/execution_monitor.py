from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from automations.midas_access_etl.constants import PIPELINE_NAME
from automations.midas_access_etl.monitor.alerts import build_alert
from automations.midas_access_etl.monitor.logger import log_event
from automations.midas_access_etl.schemas import AlertSeverity, LogStatus, PipelineExecution, PipelineLog, PipelineStatus
from automations.midas_access_etl.load.loader import MidasAccessLoader


@dataclass(slots=True)
class ExecutionMonitor:
    loader: MidasAccessLoader
    pipeline_name: str = PIPELINE_NAME
    execution: PipelineExecution | None = field(default=None, init=False)

    def start(self) -> PipelineExecution:
        self.execution = PipelineExecution(pipeline_name=self.pipeline_name, started_at=datetime.now(timezone.utc))
        self.loader.create_execution(self.execution)
        self.log("start", LogStatus.INFO, "Pipeline iniciado")
        return self.execution

    def log(self, step: str, status: LogStatus, message: str, duration_ms: int | None = None, **metadata: object) -> None:
        execution_id = self.execution.id if self.execution else None
        log = PipelineLog(
            execution_id=execution_id,
            pipeline_name=self.pipeline_name,
            step=step,
            status=status,
            message=message,
            duration_ms=duration_ms,
            metadata=dict(metadata),
        )
        self.loader.create_log(log)
        log_event(self.pipeline_name, step, status.value, message, duration_ms=duration_ms, **metadata)

    def alert(self, alert_type: str, severity: AlertSeverity, title: str, message: str, **metadata: object) -> None:
        execution_id = self.execution.id if self.execution else None
        alert = build_alert(
            pipeline_name=self.pipeline_name,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            execution_id=execution_id,
            metadata=dict(metadata),
        )
        self.loader.create_alert(alert)
        self.log("alert", LogStatus.WARNING, title, duration_ms=None, **metadata)

    def finish(
        self,
        status: PipelineStatus,
        records_extracted: int,
        records_transformed: int,
        records_loaded: int,
        error_message: str | None = None,
        **metadata: object,
    ) -> PipelineExecution:
        if self.execution is None:
            self.start()
        assert self.execution is not None
        self.execution.finished_at = datetime.now(timezone.utc)
        self.execution.status = status
        self.execution.records_extracted = records_extracted
        self.execution.records_transformed = records_transformed
        self.execution.records_loaded = records_loaded
        self.execution.error_message = error_message
        self.execution.duration_seconds = (self.execution.finished_at - self.execution.started_at).total_seconds()
        self.execution.metadata.update(dict(metadata))
        self.loader.update_execution(self.execution)
        self.log("finish", LogStatus.INFO, f"Pipeline finalizado com status {status.value}", duration_ms=None, **metadata)
        return self.execution
