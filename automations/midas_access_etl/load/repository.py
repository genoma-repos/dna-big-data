from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from automations.midas_access_etl.schemas import AccessRecord, IndicadorAcesso, PipelineAlert, PipelineExecution, PipelineLog, RawPayload


@runtime_checkable
class MidasAccessRepositoryPort(Protocol):
    def save_raw_payload(self, payload: RawPayload) -> None: ...

    def upsert_curated_records(self, records: list[AccessRecord]) -> int: ...

    def upsert_functionality(self, name: str) -> None: ...

    def upsert_indicators(self, indicators: list[IndicadorAcesso]) -> int: ...

    def create_execution(self, execution: PipelineExecution) -> None: ...

    def update_execution(self, execution: PipelineExecution) -> None: ...

    def create_log(self, log: PipelineLog) -> None: ...

    def create_alert(self, alert: PipelineAlert) -> None: ...


@dataclass(slots=True)
class InMemoryMidasAccessRepository(MidasAccessRepositoryPort):
    raw_payloads: list[RawPayload] = field(default_factory=list)
    curated_records: dict[tuple[str, str, str], AccessRecord] = field(default_factory=dict)
    functionalities: set[str] = field(default_factory=set)
    indicators: list[IndicadorAcesso] = field(default_factory=list)
    executions: dict[str, PipelineExecution] = field(default_factory=dict)
    logs: list[PipelineLog] = field(default_factory=list)
    alerts: list[PipelineAlert] = field(default_factory=list)

    def save_raw_payload(self, payload: RawPayload) -> None:
        self.raw_payloads.append(payload)

    def upsert_curated_records(self, records: list[AccessRecord]) -> int:
        for record in records:
            key = (record.data_hora.isoformat(), record.usuario, record.codigo_imovel)
            self.curated_records[key] = record
        return len(records)

    def upsert_functionality(self, name: str) -> None:
        self.functionalities.add(name)

    def upsert_indicators(self, indicators: list[IndicadorAcesso]) -> int:
        self.indicators.extend(indicators)
        return len(indicators)

    def create_execution(self, execution: PipelineExecution) -> None:
        self.executions[str(execution.id)] = execution

    def update_execution(self, execution: PipelineExecution) -> None:
        self.executions[str(execution.id)] = execution

    def create_log(self, log: PipelineLog) -> None:
        self.logs.append(log)

    def create_alert(self, alert: PipelineAlert) -> None:
        self.alerts.append(alert)


@dataclass(slots=True)
class SupabaseMidasAccessRepository(MidasAccessRepositoryPort):
    client: Any
    raw_table: str = "midas_access_payloads"
    curated_table: str = "acessos_corretores_imoveis"
    dimension_table: str = "dim_funcionalidades"
    execution_table: str = "pipeline_executions"
    logs_table: str = "pipeline_logs"
    alerts_table: str = "pipeline_alerts"
    indicators_table: str = "indicadores_acessos"

    def _schema(self, schema_name: str) -> Any:
        schema_method = getattr(self.client, "schema", None)
        if callable(schema_method):
            return schema_method(schema_name)
        return self.client

    def _table(self, schema_name: str, table_name: str) -> Any:
        return self._schema(schema_name).table(table_name)

    def save_raw_payload(self, payload: RawPayload) -> None:
        self._table("raw", self.raw_table).insert(payload.model_dump(mode="json")).execute()

    def upsert_curated_records(self, records: list[AccessRecord]) -> int:
        if not records:
            return 0
        rows = [record.model_dump(mode="json") for record in records]
        self._table("curated", self.curated_table).upsert(rows, on_conflict="data_hora,usuario,codigo_imovel").execute()
        return len(rows)

    def upsert_functionality(self, name: str) -> None:
        self._table("curated", self.dimension_table).upsert([
            {"nome": name, "ativo": True}
        ], on_conflict="nome").execute()

    def upsert_indicators(self, indicators: list[IndicadorAcesso]) -> int:
        if not indicators:
            return 0
        rows = [indicator.model_dump(mode="json") for indicator in indicators]
        self._table("analytics", self.indicators_table).upsert(
            rows,
            on_conflict="referencia,filial,usuario,bairro,tipo_imovel,funcao_acessada",
        ).execute()
        return len(rows)

    def create_execution(self, execution: PipelineExecution) -> None:
        self._table("monitoring", self.execution_table).insert(execution.model_dump(mode="json")).execute()

    def update_execution(self, execution: PipelineExecution) -> None:
        self._table("monitoring", self.execution_table).upsert(execution.model_dump(mode="json")).execute()

    def create_log(self, log: PipelineLog) -> None:
        self._table("monitoring", self.logs_table).insert(log.model_dump(mode="json")).execute()

    def create_alert(self, alert: PipelineAlert) -> None:
        self._table("monitoring", self.alerts_table).insert(alert.model_dump(mode="json")).execute()
