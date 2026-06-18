from __future__ import annotations

from dataclasses import dataclass

from automations.midas_access_etl.constants import DEFAULT_SOURCE
from automations.midas_access_etl.exceptions import MidasAccessQueryError
from automations.midas_access_etl.extract.access_query import AccessQueryResult, build_raw_payload
from automations.midas_access_etl.extract.client import MidasWebClient
from automations.midas_access_etl.extract.filters import AccessFilters


@dataclass(slots=True)
class MidasAccessExtractor:
    client: MidasWebClient

    def extract(
        self,
        usuario: str,
        senha: str,
        filters: AccessFilters,
        source: str = DEFAULT_SOURCE,
    ) -> AccessQueryResult:
        self.client.login(usuario, senha)
        self.client.definir_filtros(filters)
        payload = self.client.buscar_acessos()
        rows = payload.get("data")
        if not isinstance(rows, list):
            raise MidasAccessQueryError("Payload sem lista de dados")
        raw_payload = build_raw_payload(payload, source=source)
        total_records = int(payload.get("recordsFiltered", len(rows)))
        return AccessQueryResult(raw_payload=raw_payload, rows=rows, total_records=total_records, filters=filters)
