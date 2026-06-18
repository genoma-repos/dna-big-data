from __future__ import annotations

from typing import Any

from automations.midas_access_etl.config import MidasAccessSettings


def create_supabase_client(settings: MidasAccessSettings) -> Any | None:
    if not settings.supabase_url or not settings.supabase_key:
        return None
    from supabase import create_client

    return create_client(settings.supabase_url, settings.supabase_key)
