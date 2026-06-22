from __future__ import annotations

import importlib
import logging

from shared.utils.contracts import ExecutionRepositoryPort
from shared.utils.models import ExecutionRecord, ExecutionStatus

logger = logging.getLogger(__name__)


class SupabaseExecutionRepository(ExecutionRepositoryPort):
    def __init__(self, url: str, key: str, table_name: str = "automation_executions") -> None:
        supabase_module = importlib.import_module("supabase")
        self.client = supabase_module.create_client(url, key)
        self.table_name = table_name

    def _to_payload(self, record: ExecutionRecord) -> dict:
        return {
            "id": str(record.id),
            "automation_name": record.automation_name,
            "status": record.status.value,
            "started_at": record.started_at.isoformat(),
            "finished_at": record.finished_at.isoformat() if record.finished_at else None,
            "retries": record.retries,
            "payload": record.payload,
            "error_message": record.error_message,
        }

    def create(self, record: ExecutionRecord) -> None:
        self.client.table(self.table_name).insert(self._to_payload(record)).execute()

    def update(self, record: ExecutionRecord) -> None:
        self.client.table(self.table_name).upsert(
            self._to_payload(record), on_conflict="id"
        ).execute()

    def list(self, automation_name: str | None = None) -> list[ExecutionRecord]:
        query = self.client.table(self.table_name).select("*")
        if automation_name:
            query = query.eq("automation_name", automation_name)
        response = query.execute()
        return [
            ExecutionRecord(
                automation_name=row["automation_name"],
                status=ExecutionStatus(row["status"]),
                started_at=row["started_at"],
                finished_at=row.get("finished_at"),
                retries=row.get("retries", 0),
                payload=row.get("payload", {}),
                error_message=row.get("error_message"),
            )
            for row in response.data
        ]
