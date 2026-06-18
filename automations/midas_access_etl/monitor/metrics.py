from __future__ import annotations

from datetime import datetime


def build_metrics(
    started_at: datetime,
    finished_at: datetime,
    records_extracted: int,
    records_transformed: int,
    records_loaded: int,
    error_count: int = 0,
) -> dict[str, float | int]:
    duration_seconds = max((finished_at - started_at).total_seconds(), 0.0)
    error_rate = error_count / records_extracted if records_extracted else 0.0
    return {
        "duration_seconds": duration_seconds,
        "records_extracted": records_extracted,
        "records_transformed": records_transformed,
        "records_loaded": records_loaded,
        "error_rate": error_rate,
    }
