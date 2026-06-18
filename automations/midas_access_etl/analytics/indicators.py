from __future__ import annotations

from dataclasses import dataclass

from automations.midas_access_etl.analytics.aggregations import build_indicators
from automations.midas_access_etl.load.loader import MidasAccessLoader
from automations.midas_access_etl.schemas import AccessRecord


@dataclass(slots=True)
class AnalyticsUpdater:
    loader: MidasAccessLoader

    def update(self, records: list[AccessRecord]) -> int:
        indicators = build_indicators(records)
        return self.loader.update_analytics(indicators)
