from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Query
from loguru import logger

from src.database.mongodb import mongodb
from src.api.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioSummary,
)
from src.api.middleware.auth import get_current_user
from src.api.routes.prices import fetch_coingecko_prices, SUPPORTED_COINS

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


async def enrich_position_with_prices(position: dict, prices: dict) -> PortfolioResponse:
    coin_id = position["coin_id"]
    amount = position["amount"]
    buy_price = position.get("buy_price")
    
    current_price = None
    current_value = None
    profit_loss = None
    profit_loss_percent = None
    
    if coin_id in prices:
        current_price = prices[coin_id].get("usd", 0)
        current_value = current_price * amount
        
        if buy_price and buy_price > 0:
            invested = buy_price * amount
            profit_loss = current_value - invested
            profit_loss_percent = ((current_value - invested) / invested) * 100
    
    return PortfolioResponse(
        id=str(position["_id"]),
        coin_id=coin_id,
        coin_symbol=position["coin_symbol"],
        coin_name=position["coin_name"],
        amount=amount,
        buy_price=buy_price,
        buy_date=position.get("buy_date"),
        notes=position.get("notes"),
        current_price=current_price,
        current_value=current_value,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent,
        created_at=position["created_at"],
        updated_at=position.get("updated_at", position["created_at"]),
    )


@router.get("", response_model=PortfolioSummary)
async def get_portfolio(current_user: dict = Depends(get_current_user)):
    cursor = mongodb.portfolio.find({
        "user_telegram_id": current_user["telegram_id"]
    }).sort("created_at", -1)
    
    positions = await cursor.to_list(length=100)
    
    if not positions:
        return PortfolioSummary(
            total_value=0,
            total_invested=0,
            total_profit_loss=0,
            total_profit_loss_percent=0,
            positions_count=0,
            positions=[],
        )
    
    coin_ids = list(set(p["coin_id"] for p in positions if p["coin_id"] in SUPPORTED_COINS))
    
    prices = {}
    if coin_ids:
        try:
            prices = await fetch_coingecko_prices(coin_ids)
        except Exception as e:
            logger.error(f"Error fetching prices for portfolio: {e}")
    
    enriched_positions = []
    total_value = 0
    total_invested = 0
    
    for pos in positions:
        enriched = await enrich_position_with_prices(pos, prices)
        enriched_positions.append(enriched)
        
        if enriched.current_value:
            total_value += enriched.current_value
        if enriched.buy_price:
            total_invested += enriched.buy_price * enriched.amount
    
    total_profit_loss = total_value - total_invested
    total_profit_loss_percent = 0
    if total_invested > 0:
        total_profit_loss_percent = (total_profit_loss / total_invested) * 100
    
    return PortfolioSummary(
        total_value=total_value,
        total_invested=total_invested,
        total_profit_loss=total_profit_loss,
        total_profit_loss_percent=total_profit_loss_percent,
        positions_count=len(enriched_positions),
        positions=enriched_positions,
    )


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    position_data: PortfolioCreate,
    current_user: dict = Depends(get_current_user),
):
    now = datetime.utcnow()
    position_doc = {
        "user_telegram_id": current_user["telegram_id"],
        "coin_id": position_data.coin_id.lower(),
        "coin_symbol": position_data.coin_symbol.upper(),
        "coin_name": position_data.coin_name,
        "amount": position_data.amount,
        "buy_price": position_data.buy_price,
        "buy_date": position_data.buy_date,
        "notes": position_data.notes,
        "created_at": now,
        "updated_at": now,
    }
    
    result = await mongodb.portfolio.insert_one(position_doc)
    position_doc["_id"] = result.inserted_id
    
    await mongodb.db.activity_logs.insert_one({
        "user_telegram_id": current_user["telegram_id"],
        "action": "position_created",
        "details": {
            "coin_symbol": position_data.coin_symbol,
            "amount": position_data.amount,
        },
        "created_at": now,
    })
    
    logger.info(f"Position created for user {current_user['telegram_id']}: {position_data.coin_symbol}")
    
    prices = {}
    if position_data.coin_id in SUPPORTED_COINS:
        try:
            prices = await fetch_coingecko_prices([position_data.coin_id])
        except:
            pass
    
    return await enrich_position_with_prices(position_doc, prices)


@router.put("/{position_id}", response_model=PortfolioResponse)
async def update_position(
    position_id: str,
    position_update: PortfolioUpdate,
    current_user: dict = Depends(get_current_user),
):
    if not ObjectId.is_valid(position_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid position ID",
        )
    
    position = await mongodb.portfolio.find_one({
        "_id": ObjectId(position_id),
        "user_telegram_id": current_user["telegram_id"],
    })
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    
    update_data = {k: v for k, v in position_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await mongodb.portfolio.update_one(
        {"_id": ObjectId(position_id)},
        {"$set": update_data}
    )
    
    updated_position = await mongodb.portfolio.find_one({"_id": ObjectId(position_id)})
    
    prices = {}
    if updated_position["coin_id"] in SUPPORTED_COINS:
        try:
            prices = await fetch_coingecko_prices([updated_position["coin_id"]])
        except:
            pass
    
    return await enrich_position_with_prices(updated_position, prices)


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: str,
    current_user: dict = Depends(get_current_user),
):
    if not ObjectId.is_valid(position_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid position ID",
        )
    
    result = await mongodb.portfolio.delete_one({
        "_id": ObjectId(position_id),
        "user_telegram_id": current_user["telegram_id"],
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )
    
    await mongodb.db.activity_logs.insert_one({
        "user_telegram_id": current_user["telegram_id"],
        "action": "position_deleted",
        "details": {"position_id": position_id},
        "created_at": datetime.utcnow(),
    })
