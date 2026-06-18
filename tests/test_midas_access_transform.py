from __future__ import annotations

from automations.midas_access_etl.transform.deduplicator import deduplicate_records
from automations.midas_access_etl.transform.normalizer import normalize_access_row
from automations.midas_access_etl.transform.validators import validate_quality


def test_normalize_access_row_parses_and_cleans_values() -> None:
    record = normalize_access_row(
        [
            '<span>10/06/2026 16:08</span>',
            '<span>Cadastro de Imóveis (novo)</span>',
            '<span>302004-Gino</span>',
            '<span>Dentro Empresa</span>',
            '<span>Não</span>',
            '<span>Sim</span>',
            '<span>Recepção Botafogo Praia</span>',
            '<span>Botafogo Praia</span>',
            '<span>NBAP25281</span>',
            '<span>Rua Faro 76 Apto. 201</span>',
            '<span>Apartamento</span>',
            '<span>Jardim Botânico</span>',
            '<span>2</span>',
            '<span>Midas Web</span>',
        ]
    )

    assert record.codigo_imovel == "NBAP25281"
    assert record.acessou_telefone is True
    assert record.dormitorios == 2
    assert record.data_hora.tzinfo is not None


def test_deduplicate_records_uses_logical_key() -> None:
    record = normalize_access_row(
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
    )

    unique_records = deduplicate_records([record, record])

    assert len(unique_records) == 1


def test_validate_quality_accepts_known_dataset() -> None:
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
        )
    ]

    report = validate_quality(records)

    assert report.is_valid is True
    assert report.valid_records == 1
