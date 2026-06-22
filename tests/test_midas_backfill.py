"""Testa o BackfillRunner — iteração de dias e reuso de sessão."""
from __future__ import annotations

import os
from datetime import date
from unittest.mock import MagicMock, call, patch

import pytest

from automations.midas_access_etl.backfill import BackfillResult, BackfillRunner, _format_date, _iter_days, _parse_date
from automations.midas_access_etl.config import MidasAccessSettings
from automations.midas_access_etl.flow import MidasAccessPipelineRunner
from automations.midas_access_etl.load.repository import InMemoryMidasAccessRepository
from shared.utils.models import AutomationResult, ExecutionStatus


def _offline_settings() -> MidasAccessSettings:
    with patch.dict(os.environ, {"MIDAS_OFFLINE_MODE": "true", "SUPABASE_URL": "", "SUPABASE_KEY": "", "SENTRY_DSN": ""}):
        return MidasAccessSettings()


# --- utilitários de data ---

def test_parse_date() -> None:
    assert _parse_date("01/06/2026") == date(2026, 6, 1)


def test_format_date() -> None:
    assert _format_date(date(2026, 6, 1)) == "01/06/2026"


def test_iter_days_single() -> None:
    days = list(_iter_days("05/06/2026", "05/06/2026"))
    assert days == [date(2026, 6, 5)]


def test_iter_days_range() -> None:
    days = list(_iter_days("01/06/2026", "03/06/2026"))
    assert days == [date(2026, 6, 1), date(2026, 6, 2), date(2026, 6, 3)]


# --- BackfillRunner ---

def _make_mock_result(status: ExecutionStatus = ExecutionStatus.SUCCESS) -> AutomationResult:
    return AutomationResult(
        automation_name="midas-access-etl",
        status=status,
        started_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        finished_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        rows_loaded=2,
    )


def test_backfill_calls_runner_for_each_day() -> None:
    settings = _offline_settings()
    called_with: list[tuple[str, str]] = []

    def fake_run(self, data_de=None, data_ate=None):  # noqa: ANN001
        called_with.append((data_de, data_ate))
        return _make_mock_result()

    with patch("automations.midas_access_etl.backfill._build_repository", return_value=InMemoryMidasAccessRepository(), create=True), \
         patch.object(MidasAccessPipelineRunner, "run", fake_run), \
         patch("automations.midas_access_etl.flow._build_repository", return_value=InMemoryMidasAccessRepository()):
        result = BackfillRunner(settings=settings).run("01/06/2026", "03/06/2026")

    assert called_with == [
        ("01/06/2026", "01/06/2026"),
        ("02/06/2026", "02/06/2026"),
        ("03/06/2026", "03/06/2026"),
    ]
    assert result.total_days == 3
    assert result.succeeded == 3
    assert result.failed == 0
    assert result.success is True


def test_backfill_counts_failures() -> None:
    settings = _offline_settings()
    call_count = [0]

    def fake_run(self, data_de=None, data_ate=None):  # noqa: ANN001
        call_count[0] += 1
        status = ExecutionStatus.FAILED if call_count[0] == 2 else ExecutionStatus.SUCCESS
        return _make_mock_result(status)

    with patch.object(MidasAccessPipelineRunner, "run", fake_run), \
         patch("automations.midas_access_etl.flow._build_repository", return_value=InMemoryMidasAccessRepository()):
        result = BackfillRunner(settings=settings).run("01/06/2026", "03/06/2026")

    assert result.succeeded == 2
    assert result.failed == 1
    assert result.success is False


def test_backfill_shares_single_extractor() -> None:
    """Garante que o mesmo extractor (mesma sessão) é passado para todos os dias."""
    settings = _offline_settings()
    extractor_ids: set[int] = set()

    def fake_run(self, data_de=None, data_ate=None):  # noqa: ANN001
        extractor_ids.add(id(self.extractor))
        return _make_mock_result()

    with patch.object(MidasAccessPipelineRunner, "run", fake_run), \
         patch("automations.midas_access_etl.flow._build_repository", return_value=InMemoryMidasAccessRepository()):
        BackfillRunner(settings=settings).run("01/06/2026", "03/06/2026")

    assert len(extractor_ids) == 1, "Extractor reutilizado em todos os dias"
