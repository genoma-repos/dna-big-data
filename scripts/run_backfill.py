"""Script de backfill do Midas Access ETL.

Uso:
    python scripts/run_backfill.py                        # 22/06/2026 → hoje
    python scripts/run_backfill.py 22/06/2026 22/06/2026  # intervalo explícito
"""
from __future__ import annotations

import sys
from datetime import date

from automations.midas_access_etl.backfill import BackfillRunner
from automations.midas_access_etl.monitor.logger import setup_structured_logging

BACKFILL_START = "22/06/2026" # ULTIMO DIA DE ACESSO DO MIDAS (22/06/2026)


def _today() -> str:
    return date.today().strftime("%d/%m/%Y")


def main() -> int:
    setup_structured_logging("INFO")

    args = sys.argv[1:]
    data_de = args[0] if len(args) >= 1 else BACKFILL_START
    data_ate = args[1] if len(args) >= 2 else _today()

    result = BackfillRunner().run(data_de=data_de, data_ate=data_ate)

    print(f"\n{'='*50}")
    print(f"Backfill finalizado: {result.data_de} a {result.data_ate}")
    print(f"  Total de dias : {result.total_days}")
    print(f"  Sucesso       : {result.succeeded}")
    print(f"  Falhas        : {result.failed}")
    print(f"{'='*50}")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
