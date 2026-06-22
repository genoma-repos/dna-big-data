from __future__ import annotations

from shared.utils.contracts import ExecutionRepositoryPort
from shared.utils.models import ExecutionRecord


class InMemoryExecutionRepository(ExecutionRepositoryPort):
    def __init__(self) -> None:
        self._records: dict[str, ExecutionRecord] = {}

    def create(self, record: ExecutionRecord) -> None:
        self._records[str(record.id)] = record

    def update(self, record: ExecutionRecord) -> None:
        self._records[str(record.id)] = record

    def list(self, automation_name: str | None = None) -> list[ExecutionRecord]:
        records = list(self._records.values())
        if automation_name is None:
            return records
        return [r for r in records if r.automation_name == automation_name]
