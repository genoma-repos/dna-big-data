from __future__ import annotations

from automations.midas_access_etl.analytics.aggregations import build_indicators
from automations.midas_access_etl.transform.normalizer import normalize_access_row


def test_build_indicators_groups_by_reference_and_dimensions() -> None:
    records = [
        normalize_access_row(
            [
                "10/06/2026 16:08",
                "Cadastro de Imóveis (novo)",
                "302004-Gino",
                "Dentro Empresa",
                "Não",
                "Sim",
                "Recepção Botafogo Praia",
                "Botafogo Praia",
                "NBAP25281",
                "Rua Faro 76 Apto. 201",
                "Apartamento",
                "Jardim Botânico",
                "2",
                "Midas Web",
            ]
        ),
        normalize_access_row(
            [
                "10/06/2026 16:25",
                "Cadastro de Imóveis (novo)",
                "302004-Gino",
                "Dentro Empresa",
                "Não",
                "Sim",
                "Recepção Botafogo Praia",
                "Botafogo Praia",
                "NBAP25281",
                "Rua Faro 76 Apto. 201",
                "Apartamento",
                "Jardim Botânico",
                "2",
                "Midas Web",
            ]
        ),
    ]

    indicators = build_indicators(records)

    assert len(indicators) == 1
    assert indicators[0].referencia == "2026-06"
    assert indicators[0].total_acessos == 2
