from datetime import date
from typing import List, Literal, Optional, Union

from pydantic import BaseModel


ReportType = Literal["financial", "attendance", "membership"]
ExportFormat = Literal["csv", "pdf"]


class ReportEntry(BaseModel):
    label: str
    value: Union[int, float]
    date: date


class ReportResponse(BaseModel):
    report_type: ReportType
    data: List[ReportEntry]


class ReportQuery(BaseModel):
    report_type: ReportType
    report_date: Optional[date] = None

