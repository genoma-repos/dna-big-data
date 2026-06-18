from __future__ import annotations

from automations.midas_access_etl.schemas import AccessRecord


def deduplicate_records(records: list[AccessRecord]) -> list[AccessRecord]:
    seen: set[tuple[str, str, str, str]] = set()
    unique_records: list[AccessRecord] = []
    for record in records:
        key = (
            record.data_hora.isoformat(),
            record.usuario,
            record.codigo_imovel,
            record.funcao_acessada,
        )
        if key in seen:
            continue
        seen.add(key)
        unique_records.append(record)
    return unique_records
