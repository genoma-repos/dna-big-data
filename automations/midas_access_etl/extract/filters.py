from __future__ import annotations

from dataclasses import dataclass


def _to_iso(date_str: str) -> str:
    """Converte DD/MM/YYYY para YYYY-MM-DD exigido pela API do Midas."""
    day, month, year = date_str.split("/")
    return f"{year}-{month}-{day}"


@dataclass(slots=True)
class AccessFilters:
    data_de: str
    data_ate: str
    filial: str = ""
    corretor: str = ""
    imovel: str = ""
    endereco: str = ""
    acessou_tel: str = "S"

    def to_params(self) -> dict[str, str]:
        return {
            "data_de": _to_iso(self.data_de),
            "data_ate": _to_iso(self.data_ate),
            "filial": self.filial,
            "corretor": self.corretor,
            "imovel": self.imovel,
            "endereco": self.endereco,
            "acessou_tel": self.acessou_tel,
        }
