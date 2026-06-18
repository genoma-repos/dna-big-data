from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, runtime_checkable

from shared.utils.models import AutomationMetadata, AutomationResult, ExecutionRecord


@runtime_checkable
class Automation(Protocol):
    metadata: AutomationMetadata

    def run(self) -> AutomationResult:
        ...


@runtime_checkable
class AutomationRegistryPort(Protocol):
    def register(self, automation: Automation) -> None:
        ...

    def get(self, name: str) -> Automation:
        ...

    def list(self) -> Iterable[Automation]:
        ...


@runtime_checkable
class ExecutionRepositoryPort(Protocol):
    def save(self, record: ExecutionRecord) -> None:
        ...

    def list(self, automation_name: str | None = None) -> list[ExecutionRecord]:
        ...


@runtime_checkable
class NotificationPort(Protocol):
    def send(self, title: str, message: str) -> None:
        ...


@runtime_checkable
class DataLakePort(Protocol):
    def write(self, dataset_name: str, rows: list[dict]) -> None:
        ...

    def read(self, dataset_name: str) -> list[dict]:
        ...
