"""Testa que MidasAccessETL.run() aceita data_de/data_ate como parâmetros."""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

from automations.midas_access_etl.automation import MidasAccessETL
from automations.midas_access_etl.config import MidasAccessSettings
from automations.midas_access_etl.extract.extractor import MidasAccessExtractor
from automations.midas_access_etl.extract.filters import AccessFilters
from automations.midas_access_etl.flow import MidasAccessPipelineRunner
from automations.midas_access_etl.load.repository import InMemoryMidasAccessRepository


def _offline_settings(**overrides: str) -> MidasAccessSettings:
    """Cria settings em modo offline, sem ler do lru_cache."""
    env = {
        "MIDAS_OFFLINE_MODE": "true",
        "SUPABASE_URL": "",
        "SUPABASE_KEY": "",
        "SENTRY_DSN": "",
        "MIDAS_USUARIO": "test",
        "MIDAS_SENHA": "test",
    }
    env.update(overrides)
    with patch.dict(os.environ, env):
        return MidasAccessSettings()


def _run_and_capture_filters(data_de: str | None, data_ate: str | None) -> AccessFilters:
    """Executa o runner em modo offline e captura os filtros usados na extração."""
    captured: list[AccessFilters] = []
    original = MidasAccessExtractor.extract

    def spy(self, filters, **kwargs):  # noqa: ANN001
        captured.append(filters)
        return original(self, filters, **kwargs)

    with patch("automations.midas_access_etl.flow._build_repository", return_value=InMemoryMidasAccessRepository()), \
         patch.object(MidasAccessExtractor, "extract", spy):
        MidasAccessPipelineRunner(settings=_offline_settings()).run(data_de=data_de, data_ate=data_ate)

    assert captured, "extract() não foi chamado — verifique se o pipeline chegou na etapa de extração"
    return captured[0]


def test_run_uses_default_dates_when_no_params() -> None:
    settings = _offline_settings()
    filters = _run_and_capture_filters(data_de=None, data_ate=None)
    assert filters.data_de == settings.default_data_de
    assert filters.data_ate == settings.default_data_ate


def test_run_overrides_data_de() -> None:
    filters = _run_and_capture_filters(data_de="01/06/2026", data_ate=None)
    assert filters.data_de == "01/06/2026"


def test_run_overrides_data_ate() -> None:
    filters = _run_and_capture_filters(data_de=None, data_ate="30/06/2026")
    assert filters.data_ate == "30/06/2026"


def test_run_overrides_both_dates() -> None:
    filters = _run_and_capture_filters(data_de="01/06/2026", data_ate="30/06/2026")
    assert filters.data_de == "01/06/2026"
    assert filters.data_ate == "30/06/2026"


def test_automation_run_passes_dates_to_runner() -> None:
    """MidasAccessETL.run() repassa os parâmetros ao runner."""
    with patch.object(MidasAccessPipelineRunner, "run", return_value=MagicMock()) as mock_run:
        MidasAccessETL().run(data_de="10/06/2026", data_ate="20/06/2026")
        mock_run.assert_called_once_with(data_de="10/06/2026", data_ate="20/06/2026")
