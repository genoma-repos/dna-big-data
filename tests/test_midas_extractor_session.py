"""Testa que extractor/client reutilizam sessão sem re-login."""
from __future__ import annotations

import pytest

from automations.midas_access_etl.exceptions import MidasAccessAuthError
from automations.midas_access_etl.extract.client import MidasWebClient
from automations.midas_access_etl.extract.extractor import MidasAccessExtractor
from automations.midas_access_etl.extract.filters import AccessFilters


def _make_extractor(offline: bool = True) -> MidasAccessExtractor:
    return MidasAccessExtractor(client=MidasWebClient(offline_mode=offline))


def test_client_login_is_idempotent() -> None:
    client = MidasWebClient(offline_mode=True)
    assert not client.is_authenticated

    client.login("user", "pass")
    assert client.is_authenticated

    # Segunda chamada não altera o cookie nem levanta exceção
    cookie_before = client.session.cookies.get("PHPSESSID")
    client.login("user", "pass")
    assert client.session.cookies.get("PHPSESSID") == cookie_before


def test_extract_raises_if_not_logged_in() -> None:
    extractor = _make_extractor()
    # Forçar estado não-autenticado usando client online sem login
    extractor.client._authenticated = False
    extractor.client.session.cookies.clear()

    filters = AccessFilters(data_de="01/01/2026", data_ate="01/01/2026")
    with pytest.raises(MidasAccessAuthError):
        extractor.extract(filters)


def test_extract_reuses_session_across_calls() -> None:
    extractor = _make_extractor()
    extractor.login("user", "pass")

    filters_a = AccessFilters(data_de="01/06/2026", data_ate="01/06/2026")
    filters_b = AccessFilters(data_de="02/06/2026", data_ate="02/06/2026")

    result_a = extractor.extract(filters_a)
    result_b = extractor.extract(filters_b)

    assert result_a.total_records == 2
    assert result_b.total_records == 2
    # Mesma sessão: PHPSESSID não mudou entre extrações
    assert extractor.client.session.cookies.get("PHPSESSID") == "offline-session"


def test_session_cookie_detected_as_authenticated() -> None:
    client = MidasWebClient(offline_mode=False)
    assert not client.is_authenticated
    client.session.cookies.set("PHPSESSID", "abc123")
    assert client.is_authenticated
