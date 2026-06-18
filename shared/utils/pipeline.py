from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


ETLStep = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(slots=True)
class ETLPipeline:
    extract: ETLStep
    transform: ETLStep
    load: ETLStep
    metadata: dict[str, Any] = field(default_factory=dict)

    def run(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        execution_context = context or {}
        extracted = self.extract(execution_context)
        transformed = self.transform(extracted)
        loaded = self.load(transformed)
        return {
            "extract": extracted,
            "transform": transformed,
            "load": loaded,
        }
