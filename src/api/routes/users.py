from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from loguru import logger

from src.database.mongodb import mongodb
from src.api.middleware.auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    timezone: Optional[str] = "UTC"
    notification_preferences: Optional[dict] = None
    theme: Optional[str] = "dark"
    language: Optional[str] = "en"


class UserProfileResponse(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None
    timezone: str = "UTC"
    theme: str = "dark"
    language: str = "en"
    notification_preferences: dict = Field(default_factory=lambda: {
        "email": False,
        "push": True,
        "telegram": True,
        "price_alerts": True,
        "whale_alerts": True,
        "portfolio_updates": True,
    })
    is_active: bool = True
    created_at: datetime
    last_login: datetime
    total_alerts: int = 0
    active_alerts: int = 0


class UserStatsResponse(BaseModel):
    total_alerts_created: int = 0
    alerts_triggered: int = 0
    portfolio_coins: int = 0
    portfolio_value_usd: float = 0.0
    member_since: datetime
    last_activity: datetime


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    user = await mongodb.db.web_users.find_one(
        {"telegram_id": current_user["telegram_id"]}
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    alert_counts = await mongodb.db.alerts.aggregate([
        {"$match": {"chat_id": current_user["telegram_id"]}},
        {"$group": {
            "_id": None,
            "total": {"$sum": 1},
            "active": {"$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}}
        }}
    ]).to_list(1)
    
    counts = alert_counts[0] if alert_counts else {"total": 0, "active": 0}
    
    return UserProfileResponse(
        telegram_id=user["telegram_id"],
        username=user.get("username"),
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        display_name=user.get("display_name"),
        email=user.get("email"),
        photo_url=user.get("photo_url"),
        timezone=user.get("timezone", "UTC"),
        theme=user.get("theme", "dark"),
        language=user.get("language", "en"),
        notification_preferences=user.get("notification_preferences", {
            "email": False,
            "push": True,
            "telegram": True,
            "price_alerts": True,
            "whale_alerts": True,
            "portfolio_updates": True,
        }),
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
        last_login=user["last_login"],
        total_alerts=counts["total"],
        active_alerts=counts["active"],
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    update_data = {
        k: v for k, v in profile_update.model_dump().items() 
        if v is not None
    }
    update_data["updated_at"] = datetime.utcnow()
    
    result = await mongodb.db.web_users.update_one(
        {"telegram_id": current_user["telegram_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await mongodb.db.activity_logs.insert_one({
        "user_telegram_id": current_user["telegram_id"],
        "action": "profile_update",
        "details": {"fields_updated": list(update_data.keys())},
        "created_at": datetime.utcnow(),
    })
    
    logger.info(f"User {current_user['telegram_id']} updated profile")
    
    return await get_user_profile(current_user)


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    user = await mongodb.db.web_users.find_one(
        {"telegram_id": current_user["telegram_id"]}
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    total_alerts = await mongodb.db.alerts.count_documents(
        {"chat_id": current_user["telegram_id"]}
    )
    
    triggered_alerts = await mongodb.db.alerts.count_documents({
        "chat_id": current_user["telegram_id"],
        "triggered": True
    })
    
    portfolio_items = await mongodb.db.portfolio.find(
        {"user_telegram_id": current_user["telegram_id"]}
    ).to_list(100)
    
    portfolio_value = sum(
        item.get("amount", 0) * item.get("current_price", item.get("buy_price", 0))
        for item in portfolio_items
    )
    
    last_activity = await mongodb.db.activity_logs.find_one(
        {"user_telegram_id": current_user["telegram_id"]},
        sort=[("created_at", -1)]
    )
    
    return UserStatsResponse(
        total_alerts_created=total_alerts,
        alerts_triggered=triggered_alerts,
        portfolio_coins=len(portfolio_items),
        portfolio_value_usd=portfolio_value,
        member_since=user["created_at"],
        last_activity=last_activity["created_at"] if last_activity else user["last_login"],
    )


@router.delete("/account")
async def delete_user_account(current_user: dict = Depends(get_current_user)):
    telegram_id = current_user["telegram_id"]
    
    await mongodb.db.sessions.delete_many({"user_telegram_id": telegram_id})
    await mongodb.db.portfolio.delete_many({"user_telegram_id": telegram_id})
    await mongodb.db.activity_logs.delete_many({"user_telegram_id": telegram_id})
    
    await mongodb.db.web_users.update_one(
        {"telegram_id": telegram_id},
        {"$set": {"is_active": False, "deleted_at": datetime.utcnow()}}
    )
    
    logger.warning(f"User {telegram_id} deleted their account")
    
    return {"message": "Account deleted successfully"}
