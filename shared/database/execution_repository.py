from __future__ import annotations

from shared.utils.contracts import ExecutionRepositoryPort
from shared.utils.models import ExecutionRecord


class InMemoryExecutionRepository(ExecutionRepositoryPort):
    def __init__(self) -> None:
        self._records: list[ExecutionRecord] = []

    def save(self, record: ExecutionRecord) -> None:
        self._records.append(record)

    def list(self, automation_name: str | None = None) -> list[ExecutionRecord]:
        if automation_name is None:
            return list(self._records)
        return [record for record in self._records if record.automation_name == automation_name]
