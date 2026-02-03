from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from loguru import logger

from src.database.mongodb import mongodb
from src.api.schemas.prices import DashboardStats, ActivityItem
from src.api.middleware.auth import get_current_user
from src.api.routes.prices import fetch_coingecko_prices, SUPPORTED_COINS

router = APIRouter(prefix="", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    telegram_id = current_user["telegram_id"]
    
    total_users = await mongodb.web_users.count_documents({})
    
    active_alerts = await mongodb.alerts.count_documents({
        "user_id": current_user["_id"],
        "is_active": True
    })
    
    cursor = mongodb.portfolio.find({"user_id": current_user["_id"]})
    positions = await cursor.to_list(length=100)
    
    total_portfolio_value = 0
    if positions:
        coin_ids = list(set(p["coin_id"] for p in positions if p["coin_id"] in SUPPORTED_COINS))
        if coin_ids:
            try:
                prices = await fetch_coingecko_prices(coin_ids)
                for pos in positions:
                    coin_id = pos["coin_id"]
                    if coin_id in prices:
                        price = prices[coin_id].get("usd", 0)
                        total_portfolio_value += price * pos["amount"]
            except Exception as e:
                logger.error(f"Error fetching prices for dashboard: {e}")
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    price_updates_today = await mongodb.price_history.count_documents({
        "timestamp": {"$gte": today_start}
    })
    
    return DashboardStats(
        total_users=total_users,
        active_alerts=active_alerts,
        total_portfolio_value=total_portfolio_value,
        price_updates_today=price_updates_today,
    )


@router.get("/activity", response_model=list[ActivityItem])
async def get_recent_activity(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
):
    cursor = mongodb.activity_logs.find({
        "user_id": current_user["_id"]
    }).sort("created_at", -1).limit(limit)
    
    activities = await cursor.to_list(length=limit)
    
    return [
        ActivityItem(
            id=str(activity["_id"]),
            action=activity["action"],
            details=activity.get("details"),
            created_at=activity["created_at"],
        )
        for activity in activities
    ]
