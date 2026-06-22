"""Inicia o runner Prefect com deployment de cron diário.

Este script é de longa duração (blocking). Execute-o como um serviço
ou em um terminal dedicado:

    python scripts/serve_prefect.py

Equivalente declarativo (requer Prefect server rodando):
    prefect deploy --all
    prefect worker start --pool default-agent-pool
"""
from __future__ import annotations

import sys

from automations.midas_access_etl.flow import midas_access_etl_flow
from automations.midas_access_etl.monitor.logger import setup_structured_logging
from orchestrator.schedules.deployment import build_deployment_config


def main() -> None:
    setup_structured_logging("INFO")
    cfg = build_deployment_config()

    print(f"Iniciando deployment: {cfg.name}")
    print(f"  Cron    : {cfg.cron} ({cfg.timezone})")
    print(f"  Tags    : {cfg.tags}")
    print(f"  Flow    : {midas_access_etl_flow.name}")
    print()

    # flow.serve() registra o deployment na API do Prefect e fica em loop
    # atendendo runs agendadas e manuais (blocking).
    midas_access_etl_flow.serve(
        name=cfg.name,
        cron=cfg.cron,
        timezone=cfg.timezone,
        tags=cfg.tags,
        description=cfg.description,
        pause_on_shutdown=False,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRunner interrompido.")
        sys.exit(0)
