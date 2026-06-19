from __future__ import annotations

from automations.midas_access_etl.constants import KNOWN_FUNCTIONALITIES
from automations.midas_access_etl.schemas import AccessRecord, QualityReport


def validate_quality(records: list[AccessRecord], minimum_records: int = 1) -> QualityReport:
    errors: list[str] = []
    warnings: list[str] = []
    unknown_functions = sorted({record.funcao_acessada for record in records if record.funcao_acessada not in KNOWN_FUNCTIONALITIES})

    print("[MIDAS] -------------------------------- Validating data quality -------------------------------- ")
    if len(records) < minimum_records:
        print(f"[MIDAS] Quantidade de registros abaixo do mínimo: {len(records)} < {minimum_records}")
        errors.append(f"Quantidade de registros abaixo do mínimo: {len(records)} < {minimum_records}")

    valid_count = 0
    for record in records:
        if not record.data_hora:
            print(f"[MIDAS] Registro com data_hora inválida: {record.usuario} -- {record.data_hora}")
            errors.append("Registro sem data_hora")
            continue
        if not record.codigo_imovel:
            print(f"[MIDAS] Registro com codigo_imovel inválido: {record.usuario} -- {record.data_hora}")
            # errors.append("Registro sem codigo_imovel")
            continue
        if not record.funcao_acessada:
            print(f"[MIDAS] Registro com funcao_acessada inválida: {record.usuario} -- {record.data_hora}")
            errors.append("Registro sem funcao_acessada")
            continue
        valid_count += 1

    if unknown_functions:
        print(f"[MIDAS] Unknown functionalities: {unknown_functions}")
        warnings.append("Foram encontradas funcionalidades novas na dimensão de acesso")
    print("[MIDAS] -------------------------------- Quality validation completed  -------------------------------- ")

    return QualityReport(
        total_records=len(records),
        valid_records=valid_count,
        invalid_records=max(len(records) - valid_count, 0),
        errors=errors,
        warnings=warnings,
        unknown_functionalities=unknown_functions,
        minimum_required=minimum_records,
        is_valid=not errors,
    )
