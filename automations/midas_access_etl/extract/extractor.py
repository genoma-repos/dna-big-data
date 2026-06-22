from __future__ import annotations

import logging
from dataclasses import dataclass

from automations.midas_access_etl.constants import DEFAULT_SOURCE
from automations.midas_access_etl.exceptions import MidasAccessAuthError, MidasAccessQueryError
from automations.midas_access_etl.extract.access_query import AccessQueryResult, build_raw_payload
from automations.midas_access_etl.extract.client import MidasWebClient
from automations.midas_access_etl.extract.filters import AccessFilters
from automations.midas_access_etl.monitor.execution_monitor import ExecutionMonitor

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MidasAccessExtractor:
    client: MidasWebClient

    def login(self, usuario: str, senha: str) -> None:
        """Autentica a sessão uma única vez. Chamadas subsequentes são ignoradas."""
        self.client.login(usuario, senha)

    def extract(
        self,
        filters: AccessFilters,
        source: str = DEFAULT_SOURCE,
        monitor: ExecutionMonitor | None = None,
    ) -> AccessQueryResult:
        if not self.client.is_authenticated:
            raise MidasAccessAuthError("Sessão não autenticada. Chame login() antes de extract().")
        self.client.definir_filtros(filters)
        payload = self.client.buscar_acessos()
        rows = payload.get("data")
        if not isinstance(rows, list):
            raise MidasAccessQueryError("Payload sem lista de dados")
        raw_payload = build_raw_payload(payload, source=source)
        total_records = int(payload.get("recordsFiltered", len(rows)))
        logger.info("Extração concluída: %d registros (filtro: %s → %s)", total_records, filters.data_de, filters.data_ate)
        return AccessQueryResult(raw_payload=raw_payload, rows=rows, total_records=total_records, filters=filters)
