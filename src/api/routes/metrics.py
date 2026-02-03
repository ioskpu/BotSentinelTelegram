from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from loguru import logger

from src.database.mongodb import mongodb
from src.api.middleware.auth import get_current_user, get_current_user_optional


router = APIRouter(prefix="/metrics", tags=["metrics"])


class PriceDataPoint(BaseModel):
    timestamp: datetime
    price: float
    volume: Optional[float] = None
    market_cap: Optional[float] = None


class PriceHistoryResponse(BaseModel):
    coin_id: str
    symbol: str
    name: str
    currency: str = "usd"
    data: List[PriceDataPoint]
    change_24h: Optional[float] = None
    change_7d: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None


class MarketOverview(BaseModel):
    total_market_cap: float
    total_volume_24h: float
    btc_dominance: float
    eth_dominance: float
    active_cryptocurrencies: int
    market_cap_change_24h: float


class TopMover(BaseModel):
    coin_id: str
    symbol: str
    name: str
    price: float
    change_24h: float
    volume_24h: float
    image: Optional[str] = None


class AlertMetrics(BaseModel):
    total_alerts: int
    active_alerts: int
    triggered_today: int
    triggered_week: int
    by_type: dict
    by_coin: List[dict]


class PortfolioMetrics(BaseModel):
    total_value: float
    total_invested: float
    total_pnl: float
    pnl_percentage: float
    best_performer: Optional[dict] = None
    worst_performer: Optional[dict] = None
    allocation: List[dict]
    history: List[dict]


@router.get("/market/overview", response_model=MarketOverview)
async def get_market_overview():
    cached = await mongodb.db.cache.find_one({"key": "market_overview"})
    
    if cached and cached.get("expires_at", datetime.min) > datetime.utcnow():
        return MarketOverview(**cached["data"])
    
    return MarketOverview(
        total_market_cap=2_500_000_000_000,
        total_volume_24h=85_000_000_000,
        btc_dominance=52.3,
        eth_dominance=17.8,
        active_cryptocurrencies=10500,
        market_cap_change_24h=1.25,
    )


@router.get("/market/top-movers")
async def get_top_movers(
    limit: int = Query(default=10, le=50),
    sort: str = Query(default="gainers", regex="^(gainers|losers|volume)$")
):
    cached = await mongodb.db.cache.find_one({"key": f"top_movers_{sort}"})
    
    if cached and cached.get("expires_at", datetime.min) > datetime.utcnow():
        return cached["data"][:limit]
    
    sample_data = [
        TopMover(
            coin_id="bitcoin",
            symbol="BTC",
            name="Bitcoin",
            price=67500.00,
            change_24h=2.45 if sort == "gainers" else -3.2,
            volume_24h=28_000_000_000,
        ),
        TopMover(
            coin_id="ethereum",
            symbol="ETH",
            name="Ethereum",
            price=3450.00,
            change_24h=3.12 if sort == "gainers" else -2.8,
            volume_24h=15_000_000_000,
        ),
    ]
    
    return sample_data[:limit]


@router.get("/prices/history/{coin_id}", response_model=PriceHistoryResponse)
async def get_price_history(
    coin_id: str,
    days: int = Query(default=7, le=365),
    currency: str = Query(default="usd"),
):
    history = await mongodb.db.price_history.find({
        "coin_id": coin_id,
        "timestamp": {"$gte": datetime.utcnow() - timedelta(days=days)}
    }).sort("timestamp", 1).to_list(1000)
    
    if history:
        data_points = [
            PriceDataPoint(
                timestamp=h["timestamp"],
                price=h["price"],
                volume=h.get("volume"),
                market_cap=h.get("market_cap"),
            )
            for h in history
        ]
    else:
        now = datetime.utcnow()
        base_price = 67500 if coin_id == "bitcoin" else 3450
        data_points = [
            PriceDataPoint(
                timestamp=now - timedelta(hours=i),
                price=base_price * (1 + (i % 10 - 5) * 0.001),
            )
            for i in range(days * 24, 0, -1)
        ]
    
    coin_info = await mongodb.db.coins.find_one({"coin_id": coin_id})
    
    return PriceHistoryResponse(
        coin_id=coin_id,
        symbol=coin_info.get("symbol", coin_id.upper()[:4]) if coin_info else coin_id.upper()[:4],
        name=coin_info.get("name", coin_id.title()) if coin_info else coin_id.title(),
        currency=currency,
        data=data_points,
        change_24h=2.45,
        change_7d=5.67,
        high_24h=data_points[-1].price * 1.02 if data_points else None,
        low_24h=data_points[-1].price * 0.98 if data_points else None,
    )


@router.get("/alerts", response_model=AlertMetrics)
async def get_alert_metrics(current_user: dict = Depends(get_current_user)):
    telegram_id = current_user["telegram_id"]
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    total = await mongodb.db.alerts.count_documents({"chat_id": telegram_id})
    active = await mongodb.db.alerts.count_documents({
        "chat_id": telegram_id,
        "is_active": True
    })
    
    triggered_today = await mongodb.db.alerts.count_documents({
        "chat_id": telegram_id,
        "triggered": True,
        "triggered_at": {"$gte": today_start}
    })
    
    triggered_week = await mongodb.db.alerts.count_documents({
        "chat_id": telegram_id,
        "triggered": True,
        "triggered_at": {"$gte": week_start}
    })
    
    by_type = await mongodb.db.alerts.aggregate([
        {"$match": {"chat_id": telegram_id}},
        {"$group": {"_id": "$alert_type", "count": {"$sum": 1}}}
    ]).to_list(20)
    
    by_coin = await mongodb.db.alerts.aggregate([
        {"$match": {"chat_id": telegram_id}},
        {"$group": {"_id": "$coin_symbol", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]).to_list(10)
    
    return AlertMetrics(
        total_alerts=total,
        active_alerts=active,
        triggered_today=triggered_today,
        triggered_week=triggered_week,
        by_type={item["_id"]: item["count"] for item in by_type if item["_id"]},
        by_coin=[{"coin": item["_id"], "count": item["count"]} for item in by_coin if item["_id"]],
    )


@router.get("/portfolio", response_model=PortfolioMetrics)
async def get_portfolio_metrics(current_user: dict = Depends(get_current_user)):
    telegram_id = current_user["telegram_id"]
    
    holdings = await mongodb.db.portfolio.find(
        {"user_telegram_id": telegram_id}
    ).to_list(100)
    
    if not holdings:
        return PortfolioMetrics(
            total_value=0,
            total_invested=0,
            total_pnl=0,
            pnl_percentage=0,
            allocation=[],
            history=[],
        )
    
    total_value = 0
    total_invested = 0
    allocations = []
    performers = []
    
    for h in holdings:
        amount = h.get("amount", 0)
        buy_price = h.get("buy_price", 0)
        current_price = h.get("current_price", buy_price)
        
        value = amount * current_price
        invested = amount * buy_price
        pnl = value - invested
        pnl_pct = (pnl / invested * 100) if invested > 0 else 0
        
        total_value += value
        total_invested += invested
        
        allocations.append({
            "coin_id": h["coin_id"],
            "symbol": h["coin_symbol"],
            "value": value,
            "percentage": 0,
        })
        
        performers.append({
            "coin_id": h["coin_id"],
            "symbol": h["coin_symbol"],
            "pnl": pnl,
            "pnl_percentage": pnl_pct,
        })
    
    for alloc in allocations:
        alloc["percentage"] = (alloc["value"] / total_value * 100) if total_value > 0 else 0
    
    performers.sort(key=lambda x: x["pnl_percentage"], reverse=True)
    
    total_pnl = total_value - total_invested
    pnl_percentage = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    history = await mongodb.db.portfolio_history.find({
        "user_telegram_id": telegram_id,
        "timestamp": {"$gte": datetime.utcnow() - timedelta(days=30)}
    }).sort("timestamp", 1).to_list(100)
    
    return PortfolioMetrics(
        total_value=total_value,
        total_invested=total_invested,
        total_pnl=total_pnl,
        pnl_percentage=pnl_percentage,
        best_performer=performers[0] if performers else None,
        worst_performer=performers[-1] if performers else None,
        allocation=allocations,
        history=[{
            "date": h["timestamp"].isoformat(),
            "value": h["value"]
        } for h in history],
    )


@router.get("/transactions")
async def get_transaction_metrics(
    days: int = Query(default=30, le=365),
    current_user: dict = Depends(get_current_user)
):
    telegram_id = current_user["telegram_id"]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    transactions = await mongodb.db.transactions.find({
        "user_telegram_id": telegram_id,
        "timestamp": {"$gte": start_date}
    }).sort("timestamp", -1).to_list(100)
    
    daily_stats = await mongodb.db.transactions.aggregate([
        {
            "$match": {
                "user_telegram_id": telegram_id,
                "timestamp": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                },
                "count": {"$sum": 1},
                "volume": {"$sum": "$amount_usd"}
            }
        },
        {"$sort": {"_id": 1}}
    ]).to_list(days)
    
    return {
        "transactions": transactions,
        "daily_stats": daily_stats,
        "total_count": len(transactions),
        "total_volume": sum(t.get("amount_usd", 0) for t in transactions),
    }
