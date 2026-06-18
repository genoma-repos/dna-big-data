from automations.midas_access_etl.automation import MidasAccessETL
from orchestrator.flows.automation_registry import AutomationRegistry
from orchestrator.flows.orchestrator import Orchestrator
from shared.database.execution_repository import InMemoryExecutionRepository
from shared.notifications.notifier import ConsoleNotifier
from shared.utils.models import ExecutionStatus


class SilentNotifier(ConsoleNotifier):
    def send(self, title: str, message: str) -> None:
        return None


def test_orchestrator_executes_automation() -> None:
    registry = AutomationRegistry()
    registry.register(MidasAccessETL())

    orchestrator = Orchestrator(
        registry=registry,
        repository=InMemoryExecutionRepository(),
        notifier=SilentNotifier(),
    )

    result = orchestrator.execute("midas-access-etl")

    assert result.status == ExecutionStatus.SUCCESS
