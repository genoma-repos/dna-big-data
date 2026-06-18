from __future__ import annotations

import importlib

from orchestrator.flows.automation_registry import AutomationRegistry
from orchestrator.flows.orchestrator import Orchestrator
from shared.config.settings import get_settings
from shared.database.execution_repository import InMemoryExecutionRepository
from shared.logging.json_logger import setup_logging
from shared.notifications.notifier import ConsoleNotifier

prefect = importlib.import_module("prefect")
flow = prefect.flow
task = prefect.task


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
    orchestrate()


if __name__ == "__main__":
    main()
