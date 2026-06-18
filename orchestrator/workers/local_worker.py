from __future__ import annotations

from orchestrator.flows.main import orchestrate


def run_local_worker() -> str:
    return orchestrate()
