from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    telegram_id: int
    auth_date: int
    hash: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None


class UserResponse(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    last_login: datetime


class DashboardMetrics(BaseModel):
    total_users: int = 0
    active_users_24h: int = 0
    total_alerts: int = 0
    active_alerts: int = 0
    alerts_triggered_24h: int = 0
    total_portfolio_value: float = 0.0
    top_coins_tracked: List[str] = []
    market_sentiment: Literal["bullish", "bearish", "neutral"] = "neutral"


class PricePoint(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None


class PriceHistory(BaseModel):
    coin_id: str
    symbol: str
    name: str
    currency: str = "usd"
    interval: Literal["1m", "5m", "15m", "1h", "4h", "1d", "1w"] = "1h"
    data: List[PricePoint] = []
    current_price: float
    price_change_24h: float
    price_change_percentage_24h: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None


class AlertUpdate(BaseModel):
    alert_id: str
    is_active: Optional[bool] = None
    target_price: Optional[float] = None
    percentage_change: Optional[float] = None
    notes: Optional[str] = None


class AlertTriggerEvent(BaseModel):
    alert_id: str
    coin_id: str
    coin_symbol: str
    alert_type: str
    target_value: float
    triggered_value: float
    triggered_at: datetime
    message: str


class WebSocketMessage(BaseModel):
    type: Literal[
        "auth",
        "auth_success",
        "auth_error",
        "ping",
        "pong",
        "subscribe",
        "unsubscribe",
        "subscribed",
        "unsubscribed",
        "error",
        "price_update",
        "alert_triggered",
        "portfolio_update",
        "notification",
    ]
    data: Optional[dict] = None
    channel: Optional[str] = None
    message: Optional[str] = None
    timestamp: Optional[datetime] = None


class LivePriceUpdate(BaseModel):
    coin_id: str
    symbol: str
    price: float
    price_change_24h: float
    price_change_percentage_24h: float
    volume_24h: float
    market_cap: float
    last_updated: datetime


class LiveAlertUpdate(BaseModel):
    event: Literal["created", "updated", "deleted", "triggered"]
    alert_id: str
    alert_data: Optional[dict] = None
    timestamp: datetime


class LivePortfolioUpdate(BaseModel):
    total_value: float
    total_pnl: float
    pnl_percentage: float
    holdings: List[dict]
    timestamp: datetime


class LiveUpdate(BaseModel):
    type: Literal["price", "alert", "portfolio", "notification"]
    payload: LivePriceUpdate | LiveAlertUpdate | LivePortfolioUpdate | dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationMessage(BaseModel):
    id: str
    type: Literal["info", "success", "warning", "error", "alert"]
    title: str
    message: str
    data: Optional[dict] = None
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DashboardCacheEntry(BaseModel):
    key: str
    data: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    ttl_seconds: int
