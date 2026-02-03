from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Query
from loguru import logger

from src.database.mongodb import mongodb
from src.api.schemas.alerts import AlertCreate, AlertUpdate, AlertResponse, AlertStats
from src.api.middleware.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    current_user: dict = Depends(get_current_user),
    is_active: bool | None = None,
    coin_symbol: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    query = {"user_id": current_user["_id"]}
    
    if is_active is not None:
        query["is_active"] = is_active
    if coin_symbol:
        query["coin_symbol"] = coin_symbol.upper()
    
    cursor = mongodb.alerts.find(query).skip(skip).limit(limit).sort("created_at", -1)
    alerts = await cursor.to_list(length=limit)
    
    return [
        AlertResponse(
            id=str(alert["_id"]),
            coin_id=alert["coin_id"],
            coin_symbol=alert["coin_symbol"],
            alert_type=alert["alert_type"],
            threshold=alert["threshold"],
            is_active=alert.get("is_active", True),
            created_at=alert["created_at"],
            triggered_at=alert.get("triggered_at"),
        )
        for alert in alerts
    ]


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    current_user: dict = Depends(get_current_user),
):
    now = datetime.utcnow()
    alert_doc = {
        "user_id": current_user["_id"],  # The ObjectId from the 'users' collection
        "user_telegram_id": current_user["telegram_id"],
        "coin_id": alert_data.coin_id,
        "coin_symbol": alert_data.coin_symbol.upper(),
        "alert_type": alert_data.alert_type,
        "threshold": alert_data.threshold,
        "is_active": True,
        "created_at": now,
        "triggered_at": None,
    }
    
    result = await mongodb.alerts.insert_one(alert_doc)
    alert_doc["_id"] = result.inserted_id
    
    await mongodb.activity_logs.insert_one({
        "user_id": current_user["_id"],
        "user_telegram_id": current_user["telegram_id"],
        "action": "alert_created",
        "details": {
            "coin_symbol": alert_data.coin_symbol,
            "alert_type": alert_data.alert_type,
            "threshold": alert_data.threshold,
        },
        "created_at": now,
    })
    
    logger.info(f"Alert created for user {current_user['telegram_id']}: {alert_data.coin_symbol}")
    
    return AlertResponse(
        id=str(alert_doc["_id"]),
        coin_id=alert_doc["coin_id"],
        coin_symbol=alert_doc["coin_symbol"],
        alert_type=alert_doc["alert_type"],
        threshold=alert_doc["threshold"],
        is_active=alert_doc["is_active"],
        created_at=alert_doc["created_at"],
        triggered_at=alert_doc["triggered_at"],
    )


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    current_user: dict = Depends(get_current_user),
):
    if not ObjectId.is_valid(alert_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid alert ID",
        )
    
    alert = await mongodb.alerts.find_one({
        "_id": ObjectId(alert_id),
        "user_id": current_user["_id"],
    })
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    update_data = {k: v for k, v in alert_update.model_dump().items() if v is not None}
    if "coin_symbol" in update_data:
        update_data["coin_symbol"] = update_data["coin_symbol"].upper()
    
    if update_data:
        await mongodb.alerts.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": update_data}
        )
    
    updated_alert = await mongodb.alerts.find_one({"_id": ObjectId(alert_id)})
    
    return AlertResponse(
        id=str(updated_alert["_id"]),
        coin_id=updated_alert["coin_id"],
        coin_symbol=updated_alert["coin_symbol"],
        alert_type=updated_alert["alert_type"],
        threshold=updated_alert["threshold"],
        is_active=updated_alert.get("is_active", True),
        created_at=updated_alert["created_at"],
        triggered_at=updated_alert.get("triggered_at"),
    )


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
):
    if not ObjectId.is_valid(alert_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid alert ID",
        )
    
    result = await mongodb.alerts.delete_one({
        "_id": ObjectId(alert_id),
        "user_id": current_user["_id"],
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    await mongodb.activity_logs.insert_one({
        "user_id": current_user["_id"],
        "user_telegram_id": current_user["telegram_id"],
        "action": "alert_deleted",
        "details": {"alert_id": alert_id},
        "created_at": datetime.utcnow(),
    })


@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(current_user: dict = Depends(get_current_user)):
    user_filter = {"user_id": current_user["_id"]}
    
    total_alerts = await mongodb.alerts.count_documents(user_filter)
    active_alerts = await mongodb.alerts.count_documents({**user_filter, "is_active": True})
    triggered_alerts = await mongodb.alerts.count_documents({
        **user_filter,
        "triggered_at": {"$ne": None}
    })
    
    pipeline_by_coin = [
        {"$match": user_filter},
        {"$group": {"_id": "$coin_symbol", "count": {"$sum": 1}}},
    ]
    alerts_by_coin_cursor = mongodb.alerts.aggregate(pipeline_by_coin)
    alerts_by_coin = {doc["_id"]: doc["count"] async for doc in alerts_by_coin_cursor}
    
    pipeline_by_type = [
        {"$match": user_filter},
        {"$group": {"_id": "$alert_type", "count": {"$sum": 1}}},
    ]
    alerts_by_type_cursor = mongodb.alerts.aggregate(pipeline_by_type)
    alerts_by_type = {doc["_id"]: doc["count"] async for doc in alerts_by_type_cursor}
    
    return AlertStats(
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        triggered_alerts=triggered_alerts,
        alerts_by_coin=alerts_by_coin,
        alerts_by_type=alerts_by_type,
    )


@router.post("/{alert_id}/toggle", response_model=AlertResponse)
async def toggle_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
):
    if not ObjectId.is_valid(alert_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid alert ID",
        )
    
    alert = await mongodb.alerts.find_one({
        "_id": ObjectId(alert_id),
        "user_id": current_user["_id"],
    })
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    new_status = not alert.get("is_active", True)
    await mongodb.alerts.update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": {"is_active": new_status}}
    )
    
    updated_alert = await mongodb.alerts.find_one({"_id": ObjectId(alert_id)})
    
    return AlertResponse(
        id=str(updated_alert["_id"]),
        coin_id=updated_alert["coin_id"],
        coin_symbol=updated_alert["coin_symbol"],
        alert_type=updated_alert["alert_type"],
        threshold=updated_alert["threshold"],
        is_active=updated_alert.get("is_active", True),
        created_at=updated_alert["created_at"],
        triggered_at=updated_alert.get("triggered_at"),
    )
