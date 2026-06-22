from __future__ import annotations

from unittest.mock import patch

from orchestrator.flows.automation_registry import AutomationRegistry
from orchestrator.flows.orchestrator import Orchestrator
from shared.database.execution_repository import InMemoryExecutionRepository
from shared.notifications.notifier import ConsoleNotifier
from shared.utils.models import AutomationMetadata, AutomationResult, ExecutionStatus


class SilentNotifier(ConsoleNotifier):
    def send(self, title: str, message: str) -> None:
        return None


class StubAutomation:
    metadata = AutomationMetadata(name="stub", description="stub", domain="test")

    def __init__(self, fail_times: int = 0) -> None:
        self._fail_times = fail_times
        self._calls = 0

    def run(self, data_de=None, data_ate=None) -> AutomationResult:
        self._calls += 1
        if self._calls <= self._fail_times:
            raise RuntimeError(f"falha simulada #{self._calls}")
        return AutomationResult(automation_name="stub", status=ExecutionStatus.SUCCESS)


def _make_orchestrator(
    automation: StubAutomation,
    max_retries: int = 3,
) -> tuple[Orchestrator, InMemoryExecutionRepository]:
    registry = AutomationRegistry()
    registry.register(automation)
    repo = InMemoryExecutionRepository()
    orchestrator = Orchestrator(
        registry=registry,
        repository=repo,
        notifier=SilentNotifier(),
        max_retries=max_retries,
        retry_delay_seconds=0,  # sem espera nos testes
    )
    return orchestrator, repo


def test_success_on_first_attempt() -> None:
    orchestrator, repo = _make_orchestrator(StubAutomation(fail_times=0))
    result = orchestrator.execute("stub")

    assert result.status == ExecutionStatus.SUCCESS
    records = repo.list()
    assert len(records) == 1
    assert records[0].status == ExecutionStatus.SUCCESS
    assert records[0].retries == 0


def test_success_after_retries() -> None:
    orchestrator, repo = _make_orchestrator(StubAutomation(fail_times=2), max_retries=3)
    result = orchestrator.execute("stub")

    assert result.status == ExecutionStatus.SUCCESS
    records = repo.list()
    assert len(records) == 1
    assert records[0].retries == 2


def test_failure_after_all_retries_exhausted() -> None:
    orchestrator, repo = _make_orchestrator(StubAutomation(fail_times=99), max_retries=2)
    result = orchestrator.execute("stub")

    assert result.status == ExecutionStatus.FAILED
    assert "falha simulada" in result.error_message
    records = repo.list()
    assert len(records) == 1
    assert records[0].status == ExecutionStatus.FAILED


def test_retries_counter_matches_attempts() -> None:
    automation = StubAutomation(fail_times=99)
    orchestrator, repo = _make_orchestrator(automation, max_retries=3)
    orchestrator.execute("stub")

    assert automation._calls == 4  # 1 inicial + 3 retries


def test_zero_retries_fails_immediately() -> None:
    automation = StubAutomation(fail_times=1)
    orchestrator, repo = _make_orchestrator(automation, max_retries=0)
    result = orchestrator.execute("stub")

    assert result.status == ExecutionStatus.FAILED
    assert automation._calls == 1


def test_execution_record_has_id() -> None:
    orchestrator, repo = _make_orchestrator(StubAutomation())
    orchestrator.execute("stub")
    assert repo.list()[0].id is not None


def test_list_filters_by_automation_name() -> None:
    orchestrator, repo = _make_orchestrator(StubAutomation())
    orchestrator.execute("stub")
    assert len(repo.list("stub")) == 1
    assert len(repo.list("outro")) == 0
