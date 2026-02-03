from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PriceResponse(BaseModel):
    coin_id: str
    symbol: str
    name: str
    current_price: float
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    last_updated: datetime


class PriceHistoryPoint(BaseModel):
    timestamp: datetime
    price: float


class PriceHistoryResponse(BaseModel):
    coin_id: str
    symbol: str
    history: list[PriceHistoryPoint]
    period: str


class DashboardStats(BaseModel):
    total_users: int
    active_alerts: int
    total_portfolio_value: float
    price_updates_today: int


class ActivityItem(BaseModel):
    id: str
    action: str
    details: Optional[dict] = None
    created_at: datetime
