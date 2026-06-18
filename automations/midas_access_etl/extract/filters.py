from __future__ import annotations

from dataclasses import dataclass


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
            "data_de": self.data_de,
            "data_ate": self.data_ate,
            "filial": self.filial,
            "corretor": self.corretor,
            "imovel": self.imovel,
            "endereco": self.endereco,
            "acessou_tel": self.acessou_tel,
        }
