from __future__ import annotations

from dataclasses import dataclass, field

from shared.utils.models import AutomationMetadata, AutomationResult, ExecutionStatus


@dataclass(slots=True)
class FutureAutomation01:
    metadata: AutomationMetadata = field(
        default_factory=lambda: AutomationMetadata(
            name="future-automation-01",
            description="Placeholder para futura automação.",
            domain="future",
            version="0.1.0",
        )
    )

    def run(self) -> AutomationResult:
        return AutomationResult(
            automation_name=self.metadata.name,
            status=ExecutionStatus.PENDING,
            details={"message": "Automation not implemented yet"},
        )
