from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from prefect import flow

from automations.midas_access_etl.analytics.indicators import AnalyticsUpdater
from automations.midas_access_etl.config import MidasAccessSettings, get_midas_settings
from automations.midas_access_etl.constants import PIPELINE_NAME
from automations.midas_access_etl.extract.client import MidasWebClient
from automations.midas_access_etl.extract.extractor import MidasAccessExtractor
from automations.midas_access_etl.extract.filters import AccessFilters
from automations.midas_access_etl.load.loader import MidasAccessLoader
from automations.midas_access_etl.load.repository import InMemoryMidasAccessRepository, SupabaseMidasAccessRepository
from automations.midas_access_etl.load.supabase_client import create_supabase_client
from automations.midas_access_etl.monitor.execution_monitor import ExecutionMonitor
from automations.midas_access_etl.monitor.logger import setup_structured_logging
from automations.midas_access_etl.monitor.metrics import build_metrics
from automations.midas_access_etl.schemas import AlertSeverity, LogStatus, PipelineStatus
from automations.midas_access_etl.transform.transformer import MidasAccessTransformer
from shared.utils.models import AutomationResult, ExecutionStatus


def _build_repository(settings: MidasAccessSettings):
    if settings.offline_mode or not (settings.supabase_url and settings.supabase_key):
        return InMemoryMidasAccessRepository()
    client = create_supabase_client(settings)
    if client is None:
        return InMemoryMidasAccessRepository()
    return SupabaseMidasAccessRepository(client=client)


@dataclass(slots=True)
class MidasAccessPipelineRunner:
    settings: MidasAccessSettings = field(default_factory=get_midas_settings)

    def run(self) -> AutomationResult:
        setup_structured_logging(self.settings.log_level)
        repository = _build_repository(self.settings)
        loader = MidasAccessLoader(repository=repository)
        monitor = ExecutionMonitor(loader=loader, pipeline_name=PIPELINE_NAME)
        extractor = MidasAccessExtractor(
            client=MidasWebClient(
                offline_mode=self.settings.offline_mode or not (self.settings.midas_usuario and self.settings.midas_senha),
                login_url=self.settings.midas_login_url,
                filter_url=self.settings.midas_filter_url,
                query_url=self.settings.midas_query_url,
            )
        )
        transformer = MidasAccessTransformer(
            origem_acesso=self.settings.origem_acesso,
            minimum_records=self.settings.minimum_records,
        )
        analytics_updater = AnalyticsUpdater(loader=loader)
        execution = monitor.start()
        started_at = execution.started_at
        extracted_count = 0
        transformed_count = 0
        loaded_count = 0

        try:
            filters = AccessFilters(
                data_de=self.settings.default_data_de,
                data_ate=self.settings.default_data_ate,
                filial=self.settings.default_filial,
                corretor=self.settings.default_corretor,
                imovel=self.settings.default_imovel,
                endereco=self.settings.default_endereco,
                acessou_tel=self.settings.default_acessou_tel,
            )
            extracted = extractor.extract(
                usuario=self.settings.midas_usuario,
                senha=self.settings.midas_senha,
                filters=filters,
            )
            extracted_count = extracted.total_records
            loader.save_raw_payload(extracted.raw_payload)
            monitor.log("extract", LogStatus.INFO, "Payload bruto salvo", records=extracted.total_records)

            transformed_records, quality_report = transformer.transform(extracted.rows)
            transformed_count = len(transformed_records)
            loader.ensure_functionalities(quality_report.unknown_functionalities)
            if quality_report.unknown_functionalities:
                monitor.alert(
                    alert_type="new_functionality",
                    severity=AlertSeverity.MEDIUM,
                    title="Nova funcionalidade identificada",
                    message=", ".join(quality_report.unknown_functionalities),
                )

            if not quality_report.is_valid:
                raise ValueError("; ".join(quality_report.errors))

            loaded_count = loader.load_curated(transformed_records)
            monitor.log("load_curated", LogStatus.INFO, "Registros curados persistidos", records=loaded_count)

            analytics_count = analytics_updater.update(transformed_records)
            monitor.log("update_analytics", LogStatus.INFO, "Indicadores atualizados", records=analytics_count)

            finished_at = datetime.now(timezone.utc)
            metrics = build_metrics(
                started_at=started_at,
                finished_at=finished_at,
                records_extracted=extracted.total_records,
                records_transformed=len(transformed_records),
                records_loaded=loaded_count,
            )
            monitor.finish(
                status=PipelineStatus.SUCCESS,
                records_extracted=extracted.total_records,
                records_transformed=transformed_count,
                records_loaded=loaded_count,
                metadata={"quality_report": quality_report.model_dump(), "metrics": metrics},
            )
            return AutomationResult(
                automation_name=PIPELINE_NAME,
                status=ExecutionStatus.SUCCESS,
                started_at=started_at,
                finished_at=finished_at,
                rows_extracted=extracted.total_records,
                rows_transformed=transformed_count,
                rows_loaded=loaded_count,
                details={"quality_report": quality_report.model_dump(), "metrics": metrics},
            )
        except Exception as exc:  # noqa: BLE001
            monitor.alert(
                alert_type="pipeline_error",
                severity=AlertSeverity.HIGH,
                title="Falha na automação",
                message=str(exc),
            )
            monitor.finish(
                status=PipelineStatus.FAILED,
                records_extracted=extracted_count,
                records_transformed=transformed_count,
                records_loaded=loaded_count,
                error_message=str(exc),
            )
            return AutomationResult(
                automation_name=PIPELINE_NAME,
                status=ExecutionStatus.FAILED,
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
                error_message=str(exc),
                details={"error": str(exc)},
            )


@flow(name=PIPELINE_NAME)
def midas_access_etl_flow(settings: MidasAccessSettings | None = None) -> AutomationResult:
    return MidasAccessPipelineRunner(settings=settings or get_midas_settings()).run()
