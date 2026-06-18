from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from automations.midas_access_etl.schemas import AccessRecord, IndicadorAcesso


def build_indicators(records: list[AccessRecord]) -> list[IndicadorAcesso]:
    grouped: dict[tuple[str, str | None, str | None, str | None, str | None, str | None], int] = defaultdict(int)
    for record in records:
        referencia = record.data_hora.astimezone(timezone.utc).strftime("%Y-%m")
        key = (referencia, record.filial, record.usuario, record.bairro, record.tipo_imovel, record.funcao_acessada)
        grouped[key] += 1
    now = datetime.now(timezone.utc)
    return [
        IndicadorAcesso(
            referencia=referencia,
            filial=filial,
            usuario=usuario,
            bairro=bairro,
            tipo_imovel=tipo_imovel,
            funcao_acessada=funcao,
            total_acessos=total,
            updated_at=now,
        )
        for (referencia, filial, usuario, bairro, tipo_imovel, funcao), total in grouped.items()
    ]
