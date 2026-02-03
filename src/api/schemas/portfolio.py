from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PortfolioCreate(BaseModel):
    coin_id: str
    coin_symbol: str
    coin_name: str
    amount: float = Field(..., gt=0)
    buy_price: Optional[float] = Field(None, gt=0)
    buy_date: Optional[datetime] = None
    notes: Optional[str] = None


class PortfolioUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    buy_price: Optional[float] = Field(None, gt=0)
    buy_date: Optional[datetime] = None
    notes: Optional[str] = None


class PortfolioResponse(BaseModel):
    id: str
    coin_id: str
    coin_symbol: str
    coin_name: str
    amount: float
    buy_price: Optional[float] = None
    buy_date: Optional[datetime] = None
    notes: Optional[str] = None
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class PortfolioSummary(BaseModel):
    total_value: float
    total_invested: float
    total_profit_loss: float
    total_profit_loss_percent: float
    positions_count: int
    positions: list[PortfolioResponse]
