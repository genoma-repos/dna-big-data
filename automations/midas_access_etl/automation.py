from __future__ import annotations

from dataclasses import dataclass, field

from automations.midas_access_etl.config import MidasAccessSettings, get_midas_settings
from automations.midas_access_etl.constants import PIPELINE_NAME
from automations.midas_access_etl.flow import MidasAccessPipelineRunner
from shared.utils.models import AutomationMetadata, AutomationResult


@dataclass(slots=True)
class MidasAccessETL:
    settings: MidasAccessSettings = field(default_factory=get_midas_settings)
    metadata: AutomationMetadata = field(
        default_factory=lambda: AutomationMetadata(
            name=PIPELINE_NAME,
            description="ETL diário de acessos de corretores a imóveis do sistema Midas Web.",
            domain="midas-access",
            version="1.0.0",
        )
    )

    def run(self) -> AutomationResult:
        return MidasAccessPipelineRunner(self.settings).run()
