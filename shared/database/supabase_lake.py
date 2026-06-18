from __future__ import annotations

import importlib

from shared.database.storage import StorageAdapter


class SupabaseDataLake(StorageAdapter):
    def __init__(self, url: str, key: str, bucket: str = "data_lake") -> None:
        supabase_module = importlib.import_module("supabase")
        self.client = supabase_module.create_client(url, key)
        self.bucket = bucket

    def write_dataset(self, name: str, rows: list[dict]) -> None:
        self.client.table(name).upsert(rows).execute()

    def read_dataset(self, name: str) -> list[dict]:
        response = self.client.table(name).select("*").execute()
        return list(response.data)
