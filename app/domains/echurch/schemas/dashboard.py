from typing import List

from pydantic import BaseModel


class DashboardCard(BaseModel):
    label: str
    value: int
    trend_percent: float = 0.0


class DashboardSummaryResponse(BaseModel):
    cards: List[DashboardCard]
    attendance_trend: List[dict]
    new_members_trend: List[dict]

