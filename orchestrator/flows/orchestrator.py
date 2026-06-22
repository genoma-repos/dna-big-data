from __future__ import annotations

import logging
import time
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
        max_retries: int = 3,
        retry_delay_seconds: float = 5.0,
    ) -> None:
        self.registry = registry
        self.repository = repository
        self.notifier = notifier
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

    def execute(self, automation_name: str) -> AutomationResult:
        automation = self.registry.get(automation_name)
        started_at = datetime.now(timezone.utc)
        record = ExecutionRecord(
            automation_name=automation_name,
            status=ExecutionStatus.RUNNING,
            started_at=started_at,
        )
        self.repository.create(record)

        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                delay = self.retry_delay_seconds * (2 ** (attempt - 1))
                logger.warning(
                    "Retry %d/%d para '%s' em %.1fs",
                    attempt, self.max_retries, automation_name, delay,
                )
                record.status = ExecutionStatus.RETRYING
                record.retries = attempt
                self.repository.update(record)
                time.sleep(delay)

            try:
                result = automation.run()
                result.started_at = started_at
                result.finished_at = datetime.now(timezone.utc)
                record.status = result.status
                record.finished_at = result.finished_at
                record.payload = result.details
                record.retries = attempt
                self.repository.update(record)
                self.notifier.send(
                    title=f"Automação finalizada: {automation_name}",
                    message=f"Status: {result.status.value}",
                )
                return result
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.exception(
                    "automation_attempt_failed",
                    extra={"automation": automation_name, "attempt": attempt},
                )

        # Todas as tentativas esgotadas
        finished_at = datetime.now(timezone.utc)
        record.status = ExecutionStatus.FAILED
        record.finished_at = finished_at
        record.error_message = str(last_exc)
        self.repository.update(record)
        self.notifier.send(
            title=f"Falha na automação: {automation_name}",
            message=f"Falhou após {self.max_retries} retries — {last_exc}",
        )
        return AutomationResult(
            automation_name=automation_name,
            status=ExecutionStatus.FAILED,
            started_at=started_at,
            finished_at=finished_at,
            error_message=str(last_exc),
        )
