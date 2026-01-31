import aiohttp
import asyncio
from typing import Dict, Optional, List
from loguru import logger
from src.config.settings import settings

class PriceMonitor:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, float] = {}
        
    async def start(self):
        """Inicia la sesión HTTP"""
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        """Cierra la sesión HTTP"""
        if self.session:
            await self.session.close()
    
    async def get_solana_price(self) -> Optional[float]:
        """Obtiene el precio actual de Solana"""
        return await self._get_price_by_id('solana')
    
    async def get_stellar_price(self) -> Optional[float]:
        """Obtiene el precio actual de Stellar"""
        return await self._get_price_by_id('stellar')
    
    async def get_price_by_symbol(self, symbol: str) -> Optional[float]:
        """Obtiene precio por símbolo (SOL, XLM)"""
        symbol_to_id = {
            'SOL': 'solana',
            'XLM': 'stellar',
            'BTC': 'bitcoin',
            'ETH': 'ethereum'
        }
        
        coin_id = symbol_to_id.get(symbol.upper())
        if coin_id:
            return await self._get_price_by_id(coin_id)
        return None
    
    async def _get_price_by_id(self, coin_id: str) -> Optional[float]:
        """Obtiene precio de CoinGecko"""
        if not self.session:
            await self.start()
        
        try:
            url = f"{settings.COINGECKO_API_URL}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    price = data.get(coin_id, {}).get('usd')
                    if price:
                        self.cache[coin_id] = price
                        return price
                else:
                    logger.warning(f"CoinGecko API error: {response.status}")
                    return self.cache.get(coin_id)
        except Exception as e:
            logger.error(f"Error fetching price for {coin_id}: {e}")
            return self.cache.get(coin_id)
        
        return None
    
    async def get_multiple_prices(self, coin_ids: List[str]) -> Dict[str, Optional[float]]:
        """Obtiene múltiples precios en una sola llamada"""
        if not coin_ids:
            return {}
        
        if not self.session:
            await self.start()
        
        try:
            url = f"{settings.COINGECKO_API_URL}/simple/price"
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd'
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    for coin_id in coin_ids:
                        price = data.get(coin_id, {}).get('usd')
                        if price:
                            self.cache[coin_id] = price
                        prices[coin_id] = price
                    return prices
        except Exception as e:
            logger.error(f"Error fetching multiple prices: {e}")
            return {coin_id: self.cache.get(coin_id) for coin_id in coin_ids}
        
        return {}