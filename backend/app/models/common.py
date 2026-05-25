from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database: str = "not_connected"


class ChartPoint(BaseModel):
    label: str
    value: float
