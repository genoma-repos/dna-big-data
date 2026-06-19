from __future__ import annotations

from dataclasses import dataclass

from automations.midas_access_etl.constants import DEFAULT_ORIGEM_ACESSO
from automations.midas_access_etl.schemas import AccessRecord, QualityReport
from automations.midas_access_etl.transform.deduplicator import deduplicate_records
from automations.midas_access_etl.transform.normalizer import normalize_access_row
from automations.midas_access_etl.transform.validators import validate_quality
from automations.midas_access_etl.transform.fingerprint import build_fingerprint


@dataclass(slots=True)
class MidasAccessTransformer:
    origem_acesso: str = DEFAULT_ORIGEM_ACESSO
    minimum_records: int = 1

    def transform(self, rows: list[list[str]]) -> tuple[list[AccessRecord], QualityReport]:
        normalized = [normalize_access_row(row, origem_acesso=self.origem_acesso) for row in rows]
        enriched = [
            build_fingerprint(record)
            for record in normalized
        ]
        unique_records = deduplicate_records(enriched)
        quality_report = validate_quality(unique_records, minimum_records=self.minimum_records)
        return unique_records, quality_report
