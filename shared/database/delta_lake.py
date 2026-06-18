from __future__ import annotations

from shared.database.storage import StorageAdapter


class DeltaLakeAdapter(StorageAdapter):
    def __init__(self, connection_string: str | None = None) -> None:
        self.connection_string = connection_string

    def write_dataset(self, name: str, rows: list[dict]) -> None:
        raise NotImplementedError("Delta Lake será suportado em migração futura.")

    def read_dataset(self, name: str) -> list[dict]:
        raise NotImplementedError("Delta Lake será suportado em migração futura.")
