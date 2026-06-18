from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DailySchedule:
    automation_name: str
    cron: str = "0 6 * * *"


def build_daily_schedule(automation_name: str) -> DailySchedule:
    return DailySchedule(automation_name=automation_name)
