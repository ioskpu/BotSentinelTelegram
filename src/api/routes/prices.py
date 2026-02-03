from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Query
from loguru import logger
import aiohttp

from src.config.settings import settings
from src.database.mongodb import mongodb
from src.api.schemas.prices import PriceResponse, PriceHistoryResponse, PriceHistoryPoint

router = APIRouter(prefix="/prices", tags=["prices"])

SUPPORTED_COINS = {
    "bitcoin": {"symbol": "BTC", "name": "Bitcoin"},
    "ethereum": {"symbol": "ETH", "name": "Ethereum"},
    "solana": {"symbol": "SOL", "name": "Solana"},
    "stellar": {"symbol": "XLM", "name": "Stellar"},
    "ripple": {"symbol": "XRP", "name": "XRP"},
    "cardano": {"symbol": "ADA", "name": "Cardano"},
    "polkadot": {"symbol": "DOT", "name": "Polkadot"},
    "avalanche-2": {"symbol": "AVAX", "name": "Avalanche"},
}


async def fetch_coingecko_prices(coin_ids: list[str]) -> dict:
    ids_param = ",".join(coin_ids)
    url = f"{settings.COINGECKO_API_URL}/simple/price"
    params = {
        "ids": ids_param,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_last_updated_at": "true",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                logger.error(f"CoinGecko API error: {response.status}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Price service temporarily unavailable",
                )
            return await response.json()


@router.get("/current", response_model=list[PriceResponse])
async def get_current_prices(
    coins: str | None = Query(None, description="Comma-separated coin IDs"),
):
    if coins:
        coin_ids = [c.strip().lower() for c in coins.split(",")]
        coin_ids = [c for c in coin_ids if c in SUPPORTED_COINS]
    else:
        coin_ids = list(SUPPORTED_COINS.keys())
    
    if not coin_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid coin IDs provided",
        )
    
    try:
        prices_data = await fetch_coingecko_prices(coin_ids)
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch current prices",
        )
    
    prices = []
    now = datetime.utcnow()
    
    for coin_id in coin_ids:
        if coin_id not in prices_data:
            continue
        
        coin_data = prices_data[coin_id]
        coin_info = SUPPORTED_COINS[coin_id]
        
        last_updated = coin_data.get("last_updated_at")
        if last_updated:
            last_updated = datetime.fromtimestamp(last_updated)
        else:
            last_updated = now
        
        prices.append(PriceResponse(
            coin_id=coin_id,
            symbol=coin_info["symbol"],
            name=coin_info["name"],
            current_price=coin_data.get("usd", 0),
            price_change_24h=coin_data.get("usd_24h_change"),
            price_change_percentage_24h=coin_data.get("usd_24h_change"),
            market_cap=coin_data.get("usd_market_cap"),
            volume_24h=coin_data.get("usd_24h_vol"),
            last_updated=last_updated,
        ))
    
    return prices


@router.get("/history/{symbol}", response_model=PriceHistoryResponse)
async def get_price_history(
    symbol: str,
    period: str = Query("24h", pattern="^(1h|24h|7d|30d)$"),
):
    symbol_upper = symbol.upper()
    coin_id = None
    
    for cid, info in SUPPORTED_COINS.items():
        if info["symbol"] == symbol_upper:
            coin_id = cid
            break
    
    if not coin_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coin with symbol {symbol} not found",
        )
    
    period_hours = {"1h": 1, "24h": 24, "7d": 168, "30d": 720}
    hours = period_hours[period]
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    cursor = mongodb.price_history.find({
        "coin_id": coin_id,
        "timestamp": {"$gte": start_time}
    }).sort("timestamp", 1)
    
    history_docs = await cursor.to_list(length=1000)
    
    if not history_docs:
        try:
            days = max(1, hours // 24)
            url = f"{settings.COINGECKO_API_URL}/coins/{coin_id}/market_chart"
            params = {"vs_currency": "usd", "days": days}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        history_points = [
                            PriceHistoryPoint(
                                timestamp=datetime.fromtimestamp(p[0] / 1000),
                                price=p[1]
                            )
                            for p in data.get("prices", [])
                        ]
                        return PriceHistoryResponse(
                            coin_id=coin_id,
                            symbol=symbol_upper,
                            history=history_points,
                            period=period,
                        )
        except Exception as e:
            logger.error(f"Error fetching price history from CoinGecko: {e}")
    
    history_points = [
        PriceHistoryPoint(
            timestamp=doc["timestamp"],
            price=doc["price"]
        )
        for doc in history_docs
    ]
    
    return PriceHistoryResponse(
        coin_id=coin_id,
        symbol=symbol_upper,
        history=history_points,
        period=period,
    )
