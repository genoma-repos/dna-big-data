from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from automations.midas_access_etl.constants import (
    DEFAULT_MIN_RECORDS,
    DEFAULT_ORIGEM_ACESSO,
    MIDAS_ACCESS_FILTER_URL,
    MIDAS_ACCESS_QUERY_URL,
    MIDAS_LOGIN_URL,
)


class MidasAccessSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    sentry_dsn: str = Field(default="", alias="SENTRY_DSN")
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")
    midas_usuario: str = Field(default="", alias="MIDAS_USUARIO")
    midas_senha: str = Field(default="", alias="MIDAS_SENHA")
    midas_login_url: str = Field(default=MIDAS_LOGIN_URL, alias="MIDAS_LOGIN_URL")
    midas_filter_url: str = Field(default=MIDAS_ACCESS_FILTER_URL, alias="MIDAS_FILTER_URL")
    midas_query_url: str = Field(default=MIDAS_ACCESS_QUERY_URL, alias="MIDAS_QUERY_URL")
    offline_mode: bool = Field(default=True, alias="MIDAS_OFFLINE_MODE")
    default_filial: str = Field(default="", alias="MIDAS_FILIAL")
    default_corretor: str = Field(default="", alias="MIDAS_CORRETOR")
    default_imovel: str = Field(default="", alias="MIDAS_IMOVEL")
    default_endereco: str = Field(default="", alias="MIDAS_ENDERECO")
    default_data_de: str = Field(default="01/01/1970", alias="MIDAS_DATA_DE")
    default_data_ate: str = Field(default="31/12/2099", alias="MIDAS_DATA_ATE")
    default_acessou_tel: str = Field(default="S", alias="MIDAS_ACESSOU_TEL")
    minimum_records: int = Field(default=DEFAULT_MIN_RECORDS, alias="MIDAS_MINIMUM_RECORDS")
    origem_acesso: str = Field(default=DEFAULT_ORIGEM_ACESSO, alias="MIDAS_ORIGEM_ACESSO")
    execution_timeout_seconds: int = Field(default=900, alias="MIDAS_TIMEOUT_SECONDS")


@lru_cache(maxsize=1)
def get_midas_settings() -> MidasAccessSettings:
    return MidasAccessSettings()
