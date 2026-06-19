# transform/fingerprint.py

import hashlib

from automations.midas_access_etl.schemas import AccessRecord


def build_fingerprint(record: AccessRecord) -> AccessRecord:
    payload = "|".join([
        record.data_hora.isoformat(),
        record.usuario or "",
        record.codigo_imovel or "",
        record.funcao_acessada or "",
        record.origem_acesso or "",
    ])

    fingerprint = hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()
    record.fingerprint = fingerprint
    return record