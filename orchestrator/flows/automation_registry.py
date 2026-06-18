from __future__ import annotations

from collections.abc import Iterable

from shared.utils.contracts import Automation


class AutomationRegistry:
    def __init__(self) -> None:
        self._automations: dict[str, Automation] = {}

    def register(self, automation: Automation) -> None:
        self._automations[automation.metadata.name] = automation

    def get(self, name: str) -> Automation:
        return self._automations[name]

    def list(self) -> Iterable[Automation]:
        return self._automations.values()
