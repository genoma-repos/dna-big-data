from __future__ import annotations

from dataclasses import dataclass, field

DAILY_CRON = "0 6 * * 1-5"
TIMEZONE = "America/Sao_Paulo"
DEPLOYMENT_NAME = "midas-access-etl-daily"
DEPLOYMENT_TAGS = ["etl", "midas", "daily"]


@dataclass(slots=True)
class DeploymentConfig:
    name: str = DEPLOYMENT_NAME
    cron: str = DAILY_CRON
    timezone: str = TIMEZONE
    tags: list[str] = field(default_factory=lambda: list(DEPLOYMENT_TAGS))
    description: str = "ETL diário de acessos de corretores a imóveis do sistema Midas Web."


def build_deployment_config() -> DeploymentConfig:
    return DeploymentConfig()
