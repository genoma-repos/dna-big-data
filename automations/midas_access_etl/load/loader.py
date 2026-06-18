from __future__ import annotations

from dataclasses import dataclass

from automations.midas_access_etl.load.repository import MidasAccessRepositoryPort
from automations.midas_access_etl.schemas import AccessRecord, IndicadorAcesso, PipelineAlert, PipelineExecution, PipelineLog, RawPayload


@dataclass(slots=True)
class MidasAccessLoader:
    repository: MidasAccessRepositoryPort

    def save_raw_payload(self, payload: RawPayload) -> None:
        self.repository.save_raw_payload(payload)

    def load_curated(self, records: list[AccessRecord]) -> int:
        return self.repository.upsert_curated_records(records)

    def ensure_functionalities(self, names: list[str]) -> None:
        for name in names:
            self.repository.upsert_functionality(name)

    def update_analytics(self, indicators: list[IndicadorAcesso]) -> int:
        return self.repository.upsert_indicators(indicators)

    def create_execution(self, execution: PipelineExecution) -> None:
        self.repository.create_execution(execution)

    def update_execution(self, execution: PipelineExecution) -> None:
        self.repository.update_execution(execution)

    def create_log(self, log: PipelineLog) -> None:
        self.repository.create_log(log)

    def create_alert(self, alert: PipelineAlert) -> None:
        self.repository.create_alert(alert)
