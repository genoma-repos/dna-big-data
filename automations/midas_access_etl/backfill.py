from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta

from automations.midas_access_etl.config import MidasAccessSettings, get_midas_settings
from automations.midas_access_etl.extract.client import MidasWebClient
from automations.midas_access_etl.extract.extractor import MidasAccessExtractor
from automations.midas_access_etl.flow import MidasAccessPipelineRunner
from shared.utils.models import AutomationResult, ExecutionStatus

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BackfillResult:
    data_de: str
    data_ate: str
    total_days: int
    succeeded: int
    failed: int
    results: list[AutomationResult] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.failed == 0


def _parse_date(date_str: str) -> date:
    """Converte DD/MM/YYYY para date."""
    day, month, year = date_str.split("/")
    return date(int(year), int(month), int(day))


def _format_date(d: date) -> str:
    """Converte date para DD/MM/YYYY."""
    return d.strftime("%d/%m/%Y")


def _iter_days(data_de: str, data_ate: str):
    start = _parse_date(data_de)
    end = _parse_date(data_ate)
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


@dataclass(slots=True)
class BackfillRunner:
    settings: MidasAccessSettings = field(default_factory=get_midas_settings)

    def run(self, data_de: str, data_ate: str) -> BackfillResult:
        days = list(_iter_days(data_de, data_ate))
        logger.info("Backfill iniciado: %s → %s (%d dias)", data_de, data_ate, len(days))

        client = MidasWebClient(
            offline_mode=self.settings.offline_mode or not (self.settings.midas_usuario and self.settings.midas_senha),
            login_url=self.settings.midas_login_url,
            filter_url=self.settings.midas_filter_url,
            query_url=self.settings.midas_query_url,
            timeout_seconds=self.settings.execution_timeout_seconds,
        )
        extractor = MidasAccessExtractor(client=client)
        extractor.login(self.settings.midas_usuario, self.settings.midas_senha)

        results: list[AutomationResult] = []
        succeeded = 0
        failed = 0

        for day in days:
            day_str = _format_date(day)
            logger.info("[%s] Extraindo...", day_str)
            result = MidasAccessPipelineRunner(settings=self.settings, extractor=extractor).run(
                data_de=day_str,
                data_ate=day_str,
            )
            results.append(result)
            if result.status == ExecutionStatus.SUCCESS:
                succeeded += 1
                logger.info("[%s] OK — %d registros carregados", day_str, result.rows_loaded)
            else:
                failed += 1
                logger.error("[%s] FALHOU — %s", day_str, result.error_message)

        logger.info("Backfill concluído: %d/%d dias com sucesso", succeeded, len(days))
        return BackfillResult(
            data_de=data_de,
            data_ate=data_ate,
            total_days=len(days),
            succeeded=succeeded,
            failed=failed,
            results=results,
        )
