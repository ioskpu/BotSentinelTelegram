from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    coin_id: str
    coin_symbol: str
    alert_type: Literal["price_above", "price_below", "percent_change"]
    threshold: float = Field(..., gt=0)


class AlertUpdate(BaseModel):
    coin_id: Optional[str] = None
    coin_symbol: Optional[str] = None
    alert_type: Optional[Literal["price_above", "price_below", "percent_change"]] = None
    threshold: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class AlertResponse(BaseModel):
    id: str
    coin_id: str
    coin_symbol: str
    alert_type: str
    threshold: float
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None


class AlertStats(BaseModel):
    total_alerts: int
    active_alerts: int
    triggered_alerts: int
    alerts_by_coin: dict[str, int]
    alerts_by_type: dict[str, int]
