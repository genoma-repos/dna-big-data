from __future__ import annotations

from datetime import datetime, timezone

from automations.midas_access_etl.constants import DEFAULT_ORIGEM_ACESSO
from automations.midas_access_etl.schemas import AccessRecord
from automations.midas_access_etl.transform.html_cleaner import clean_text


def parse_bool(value: str | None) -> bool | None:
    cleaned = clean_text(value).lower()
    if cleaned in {"sim", "s", "true", "1", "yes"}:
        return True
    if cleaned in {"não", "nao", "n", "false", "0", "no"}:
        return False
    return None


def parse_int(value: str | None) -> int | None:
    cleaned = clean_text(value)
    if not cleaned:
        return None
    digits = "".join(ch for ch in cleaned if ch.isdigit() or ch == "-")
    return int(digits) if digits not in {"", "-"} else None


def parse_datetime(value: str | None) -> datetime:
    cleaned = clean_text(value)
    parsed = datetime.strptime(cleaned, "%d/%m/%Y %H:%M")
    return parsed.replace(tzinfo=timezone.utc)


def normalize_access_row(row: list[str], origem_acesso: str = DEFAULT_ORIGEM_ACESSO) -> AccessRecord:
    columns = [clean_text(cell) for cell in row]
    if len(columns) < 14:
        columns.extend([""] * (14 - len(columns)))
    return AccessRecord(
        data_hora=parse_datetime(columns[0]),
        funcao_acessada=columns[1],
        proprietario=columns[2] or None,
        local=columns[3] or None,
        acessou_pelo=columns[4] or None,
        acessou_telefone=parse_bool(columns[5]),
        usuario=columns[6],
        filial=columns[7] or None,
        codigo_imovel=columns[8],
        endereco=columns[9] or None,
        tipo_imovel=columns[10] or None,
        bairro=columns[11] or None,
        dormitorios=parse_int(columns[12]),
        acesso=columns[13] or None,
        origem_acesso=origem_acesso,
    )
