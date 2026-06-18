from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from automations.midas_access_etl.constants import DEFAULT_SOURCE
from automations.midas_access_etl.extract.filters import AccessFilters
from automations.midas_access_etl.schemas import RawPayload


@dataclass(slots=True)
class AccessQueryResult:
    raw_payload: RawPayload
    rows: list[list[str]]
    total_records: int
    filters: AccessFilters


def build_raw_payload(payload: dict, source: str = DEFAULT_SOURCE) -> RawPayload:
    return RawPayload(
        extraction_date=datetime.now(timezone.utc),
        source=source,
        payload=payload,
    )
