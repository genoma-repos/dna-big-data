from __future__ import annotations

from dataclasses import dataclass

import requests

from automations.midas_access_etl.constants import MIDAS_LOGIN_URL
from automations.midas_access_etl.exceptions import MidasAccessAuthError


@dataclass(slots=True)
class SessionAuthenticator:
    session: requests.Session
    login_url: str = MIDAS_LOGIN_URL
    timeout_seconds: int = 30

    def login(self, usuario: str, senha: str) -> requests.Response:
        payload = {
            "nm_form_submit": "1",
            "bok": "OK",
            "nmgp_opcao": "alterar",
            "login": usuario,
            "pswd": senha,
        }
        try:
            response = self.session.post(self.login_url, data=payload, timeout=self.timeout_seconds)
        except requests.RequestException as exc:  # pragma: no cover - network failure path
            raise MidasAccessAuthError(str(exc)) from exc

        if response.status_code >= 400:
            raise MidasAccessAuthError(f"Erro HTTP no login: {response.status_code}")
        if not response.cookies.get("PHPSESSID") and "PHPSESSID" not in self.session.cookies:
            raise MidasAccessAuthError("Sessão inválida ou PHPSESSID não encontrado")
        return response
