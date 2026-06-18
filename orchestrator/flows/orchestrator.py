from __future__ import annotations

import logging
from datetime import datetime, timezone

from orchestrator.flows.automation_registry import AutomationRegistry
from shared.utils.contracts import ExecutionRepositoryPort, NotificationPort
from shared.utils.models import AutomationResult, ExecutionRecord, ExecutionStatus

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(
        self,
        registry: AutomationRegistry,
        repository: ExecutionRepositoryPort,
        notifier: NotificationPort,
    ) -> None:
        self.registry = registry
        self.repository = repository
        self.notifier = notifier

    def execute(self, automation_name: str) -> AutomationResult:
        automation = self.registry.get(automation_name)
        started_at = datetime.now(timezone.utc)
        record = ExecutionRecord(
            automation_name=automation_name,
            status=ExecutionStatus.RUNNING,
            started_at=started_at,
        )
        self.repository.save(record)

        try:
            result = automation.run()
            result.started_at = started_at
            result.finished_at = datetime.now(timezone.utc)
            record.status = result.status
            record.finished_at = result.finished_at
            record.payload = result.details
            self.repository.save(record)
            self.notifier.send(
                title=f"Automação finalizada: {automation_name}",
                message=f"Status: {result.status.value}",
            )
            return result
        except Exception as exc:  # noqa: BLE001
            logger.exception("automation_failed", extra={"automation": automation_name})
            failed_result = AutomationResult(
                automation_name=automation_name,
                status=ExecutionStatus.FAILED,
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                error_message=str(exc),
            )
            record.status = ExecutionStatus.FAILED
            record.finished_at = failed_result.finished_at
            record.error_message = str(exc)
            self.repository.save(record)
            self.notifier.send(
                title=f"Falha na automação: {automation_name}",
                message=str(exc),
            )
            return failed_result
