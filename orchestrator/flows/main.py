from __future__ import annotations

import importlib
import logging

from orchestrator.flows.automation_registry import AutomationRegistry
from orchestrator.flows.orchestrator import Orchestrator
from shared.config.settings import get_settings
from shared.database.execution_repository import InMemoryExecutionRepository
from shared.logging.json_logger import setup_logging
from shared.notifications.notifier import ConsoleNotifier

logger = logging.getLogger(__name__)

try:
    prefect = importlib.import_module("prefect")
except ModuleNotFoundError:  # pragma: no cover - environment fallback
    prefect = None

if prefect is not None:
    flow = prefect.flow
    task = prefect.task
else:
    def flow(*_args, **_kwargs):
        def decorator(func):
            return func

        return decorator

    def task(func):
        return func


@task
def run_registered_automation(automation_name: str) -> str:
    from automations.midas_access_etl.automation import MidasAccessETL

    registry = AutomationRegistry()
    registry.register(MidasAccessETL())
    orchestrator = Orchestrator(
        registry=registry,
        repository=InMemoryExecutionRepository(),
        notifier=ConsoleNotifier(),
    )
    result = orchestrator.execute(automation_name)
    return result.status.value


@flow(name="automation-platform-orchestrator")
def orchestrate(automation_name: str = "midas-access-etl") -> str:
    return run_registered_automation(automation_name)


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    try:
        status = orchestrate()
        logger.info("orchestrator_finished", extra={"status": status})
    except Exception as exc:  # noqa: BLE001
        logger.exception("orchestrator_failed", extra={"error": str(exc)})
        raise


if __name__ == "__main__":
    main()
