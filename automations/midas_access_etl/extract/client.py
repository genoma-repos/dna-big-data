from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import requests

from automations.midas_access_etl.constants import (
    MIDAS_ACCESS_FILTER_URL,
    MIDAS_ACCESS_QUERY_URL,
    MIDAS_LOGIN_URL,
)
from automations.midas_access_etl.exceptions import MidasAccessQueryError
from automations.midas_access_etl.extract.auth import SessionAuthenticator
from automations.midas_access_etl.extract.filters import AccessFilters

logger = logging.getLogger(__name__)


def _sample_response() -> dict[str, Any]:
    return {
        "draw": 1,
        "recordsTotal": 2,
        "recordsFiltered": 2,
        "data": [
            [
                '<span class="text-start no-wrap" data-sort="1781118510">10/06/2026 16:08</span>',
                "<span>Cadastro de Imóveis (novo)</span>",
                "<span>302004-Gino</span>",
                "<span>Dentro Empresa</span>",
                "<span>Não</span>",
                "<span>Sim</span>",
                "<span>Recepção Botafogo Praia</span>",
                "<span>Botafogo Praia</span>",
                "<span>NBAP25281</span>",
                "<span>Rua Faro 76 Apto. 201</span>",
                "<span>Apartamento</span>",
                "<span>Jardim Botânico</span>",
                "<span>2</span>",
                "<span>Midas Web</span>",
            ],
            [
                '<span class="text-start no-wrap" data-sort="1781119510">10/06/2026 16:25</span>',
                "<span>Recepção Cliente</span>",
                "<span>201122-Ana Paula</span>",
                "<span>Dentro Empresa</span>",
                "<span>Sim</span>",
                "<span>Não</span>",
                "<span>Recepção Copacabana</span>",
                "<span>Copacabana</span>",
                "<span>CPA33901</span>",
                "<span>Av. Atlântica 900</span>",
                "<span>Casa</span>",
                "<span>Copacabana</span>",
                "<span>3</span>",
                "<span>Midas Web</span>",
            ],
        ],
    }


@dataclass(slots=True)
class MidasWebClient:
    session: requests.Session = field(default_factory=requests.Session)
    login_url: str = MIDAS_LOGIN_URL
    filter_url: str = MIDAS_ACCESS_FILTER_URL
    query_url: str = MIDAS_ACCESS_QUERY_URL
    offline_mode: bool = True
    timeout_seconds: int = 30
    auth: SessionAuthenticator = field(init=False, repr=False)
    _authenticated: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self.auth = SessionAuthenticator(self.session, self.login_url, self.timeout_seconds)

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated or bool(self.session.cookies.get("PHPSESSID"))

    def login(self, usuario: str, senha: str) -> bool:
        if self.is_authenticated:
            logger.debug("Sessão já autenticada — login ignorado")
            return True
        if self.offline_mode:
            self.session.cookies.set("PHPSESSID", "offline-session")
            self._authenticated = True
            logger.debug("Modo offline — sessão simulada")
            return True
        self.auth.login(usuario, senha)
        self._authenticated = True
        logger.info("Login realizado com sucesso")
        return True

    def definir_filtros(self, filters: AccessFilters) -> bool:
        if self.offline_mode:
            return True
        try:
            response = self.session.get(
                self.filter_url,
                params=filters.to_params(),
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failure path
            raise MidasAccessQueryError(str(exc)) from exc
        if response.status_code >= 400:
            raise MidasAccessQueryError(f"Erro ao definir filtros: {response.status_code}")
        logger.debug("Filtros aplicados: %s", filters.to_params())
        return True

    def buscar_acessos(self) -> dict[str, Any]:
        if self.offline_mode:
            return _sample_response()
        try:
            response = self.session.post(
                self.query_url,
                data={"length": -1, "start": 0},
                headers={"X-Requested-With": "XMLHttpRequest"},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:  # pragma: no cover - network failure path
            raise MidasAccessQueryError(str(exc)) from exc
        if not isinstance(payload, dict) or "data" not in payload:
            raise MidasAccessQueryError("Resposta inválida da consulta AJAX")
        logger.debug("Acessos retornados: %d registros", len(payload.get("data", [])))
        return payload
