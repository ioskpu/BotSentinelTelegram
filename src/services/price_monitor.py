import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, List
from loguru import logger
from src.config.settings import settings

class PriceMonitor:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, float] = {}
        self.symbol_to_id = {
            # Monedas principales
            'SOL': 'solana',
            'XLM': 'stellar',
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            
            # Layer 1
            'AVAX': 'avalanche-2',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'MATIC': 'matic-network',
            'ATOM': 'cosmos',
            
            # Meme coins
            'DOGE': 'dogecoin',
            'SHIB': 'shiba-inu',
            'PEPE': 'pepe',
            
            # DeFi
            'UNI': 'uniswap',
            'LINK': 'chainlink',
            'AAVE': 'aave',
            
            # Stablecoins
            'USDT': 'tether',
            'USDC': 'usd-coin',
            'DAI': 'dai',
            
            # Otras
            'XRP': 'ripple',
            'LTC': 'litecoin',
            'BNB': 'binancecoin',
            'ACU': 'acurast',
        }
        
    async def start(self):
        """Inicia la sesión HTTP"""
        self.session = aiohttp.ClientSession()
    
    async def stop(self):
        """Cierra la sesión HTTP"""
        if self.session:
            await self.session.close()
    
    async def get_solana_price(self) -> Optional[float]:
        """Obtiene el precio actual de Solana"""
        return await self.get_price_by_id('solana')
    
    async def get_stellar_price(self) -> Optional[float]:
        """Obtiene el precio actual de Stellar"""
        return await self.get_price_by_id('stellar')
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Obtiene el precio actual de una moneda por su símbolo"""
        coin_id = self.symbol_to_id.get(symbol.upper())
        if not coin_id:
            logger.warning(f"Symbol {symbol} not found in mapping")
            return None
            
        return await self.get_price_by_id(coin_id)
    
    async def get_historical_data(self, coin_id: str, days: int = 2) -> List[Dict]:
        """Obtiene datos históricos de precios desde CoinGecko"""
        if not self.session:
            await self.start()
            
        try:
            url = f"{settings.COINGECKO_API_URL}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': str(days),
                'interval': 'hourly'
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = data.get('prices', [])
                    
                    history = []
                    for p in prices:
                        # p[0] is timestamp in ms, p[1] is price
                        history.append({
                            'coin_id': coin_id,
                            'price': p[1],
                            'timestamp': datetime.fromtimestamp(p[0] / 1000, tz=timezone.utc).replace(tzinfo=None)
                        })
                    return history
                else:
                    logger.warning(f"CoinGecko Market Chart API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching historical data for {coin_id}: {e}")
            return []
    
    async def get_price_by_id(self, coin_id: str) -> Optional[float]:
        """Obtiene precio de CoinGecko"""
        if not self.session:
            await self.start()
        
        try:
            url = f"{settings.COINGECKO_API_URL}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            
            logger.debug(f"Fetching price for {coin_id} from {url}")
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"API Response for {coin_id}: {data}")
                    price = data.get(coin_id, {}).get('usd')
                    if price is not None:
                        self.cache[coin_id] = price
                        return price
                    else:
                        logger.warning(f"Price for {coin_id} not found in response: {data}")
                else:
                    logger.warning(f"CoinGecko API error: {response.status} for {coin_id}")
                    # Si falla, intentar recuperar de cache
                    return self.cache.get(coin_id)
        except Exception as e:
            logger.error(f"Error fetching price for {coin_id}: {e}")
            return self.cache.get(coin_id)
        
        return None
    
    async def get_multiple_prices(self, coin_ids: List[str] = None) -> Dict[str, Optional[float]]:
        """Obtiene múltiples precios en una sola llamada"""
        if not coin_ids:
            # Monedas por defecto si no se especifican
            coin_ids = ['solana', 'stellar', 'bitcoin', 'ethereum', 
                       'cardano', 'polkadot', 'avalanche-2']
        
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

    async def get_trending_coins(self) -> List[Dict]:
        """Obtiene monedas en tendencia"""
        try:
            if not self.session:
                await self.start()
                
            url = f"{settings.COINGECKO_API_URL}/search/trending"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    trending = []
                    
                    for item in data.get('coins', [])[:10]:  # Top 10
                        coin_data = item.get('item', {})
                        trending.append({
                            'name': coin_data.get('name'),
                            'symbol': coin_data.get('symbol', '').upper(),
                            'market_cap_rank': coin_data.get('market_cap_rank'),
                            'score': item.get('score', 0)
                        })
                    
                    return trending
                else:
                    logger.warning(f"CoinGecko Trending API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting trending coins: {e}")
            return []
