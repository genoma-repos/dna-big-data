from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class StorageAdapter(Protocol):
    def write_dataset(self, name: str, rows: list[dict]) -> None:
        ...

    def read_dataset(self, name: str) -> list[dict]:
        ...
