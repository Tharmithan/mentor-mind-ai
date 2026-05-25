from pydantic import BaseModel


class DailyTipResponse(BaseModel):
    tip: str
    category: str
    focus_topic: str | None = None
