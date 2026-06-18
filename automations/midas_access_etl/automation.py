from __future__ import annotations

import importlib
from dataclasses import dataclass, field

from shared.utils.models import AutomationMetadata, AutomationResult, ExecutionStatus
from shared.utils.pipeline import ETLPipeline


@dataclass(slots=True)
class MidasAccessETL:
    metadata: AutomationMetadata = field(
        default_factory=lambda: AutomationMetadata(
            name="midas-access-etl",
            description="ETL principal do domínio Midas Access.",
            domain="midas_access",
            version="1.0.0",
        )
    )

    def run(self) -> AutomationResult:
        pipeline = ETLPipeline(
            extract=self._extract,
            transform=self._transform,
            load=self._load,
            metadata={"source": "in-memory"},
        )
        output = pipeline.run()
        rows = output["load"]["rows_loaded"]
        return AutomationResult(
            automation_name=self.metadata.name,
            status=ExecutionStatus.SUCCESS,
            rows_extracted=output["extract"]["rows_extracted"],
            rows_transformed=output["transform"]["rows_transformed"],
            rows_loaded=rows,
            details=output,
        )

    def _extract(self, context: dict) -> dict:
        pandas_module = importlib.import_module("pandas")
        data = pandas_module.DataFrame(
            [
                {"id": 1, "value": 10},
                {"id": 2, "value": 20},
            ]
        )
        return {"rows_extracted": len(data), "data": data, "context": context}

    def _transform(self, payload: dict) -> dict:
        polars_module = importlib.import_module("polars")
        table = polars_module.from_pandas(payload["data"])
        transformed = table.with_columns((polars_module.col("value") * 2).alias("value_double"))
        return {"rows_transformed": transformed.height, "data": transformed}

    def _load(self, payload: dict) -> dict:
        table = payload["data"]
        return {"rows_loaded": table.height, "data": table.to_dicts()}
