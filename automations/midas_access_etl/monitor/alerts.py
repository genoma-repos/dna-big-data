from __future__ import annotations

from datetime import datetime, timezone

from automations.midas_access_etl.schemas import AlertSeverity, PipelineAlert


def build_alert(
    pipeline_name: str,
    alert_type: str,
    severity: AlertSeverity,
    title: str,
    message: str,
    execution_id=None,
    metadata: dict | None = None,
) -> PipelineAlert:
    return PipelineAlert(
        execution_id=execution_id,
        pipeline_name=pipeline_name,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        sent=False,
        sent_at=None,
        metadata=metadata or {},
        created_at=datetime.now(timezone.utc),
    )
