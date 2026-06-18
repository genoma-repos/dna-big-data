from automations.midas_access_etl.automation import MidasAccessETL
from orchestrator.flows.automation_registry import AutomationRegistry


def test_registry_returns_registered_automation() -> None:
    registry = AutomationRegistry()
    automation = MidasAccessETL()
    registry.register(automation)

    loaded = registry.get("midas-access-etl")

    assert loaded.metadata.name == "midas-access-etl"
