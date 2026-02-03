import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, List
from loguru import logger
from src.config.settings import settings

class PriceMonitor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PriceMonitor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, float] = {}
        self.volume_cache: Dict[str, float] = {}
        self.last_update: Dict[str, datetime] = {}
        self.global_last_update: Optional[datetime] = None
        self.update_interval = 60  # Segundos entre actualizaciones globales
        self._initialized = True
        self.symbol_to_id = {
            # Monedas principales
            'SOL': 'solana',
            'SOLANA': 'solana',
            'XLM': 'stellar',
            'STELLAR': 'stellar',
            'BTC': 'bitcoin',
            'BITCOIN': 'bitcoin',
            'ETH': 'ethereum',
            'ETHEREUM': 'ethereum',
            
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
            'TETHER': 'tether',
            'USDC': 'usd-coin',
            'DAI': 'dai',
            
            # Otras
            'XRP': 'ripple',
            'LTC': 'litecoin',
            'BNB': 'binancecoin',
            'ACU': 'acurast',
            'ACURAST': 'acurast',
        }
        
    async def start(self):
        """Inicia la sesión HTTP con headers adecuados"""
        if self.session and not self.session.closed:
            return
            
        timeout = aiohttp.ClientTimeout(total=15)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        logger.info("✅ Sesión de PriceMonitor iniciada")
    
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
    
    async def get_price_by_symbol(self, symbol: str) -> Optional[float]:
        """Alias para get_price (mantenido por compatibilidad)"""
        return await self.get_price(symbol)
    
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
        """Obtiene precio de CoinGecko con sistema de cache inteligente"""
        if not self.session or self.session.closed:
            await self.start()
        
        coin_id = coin_id.lower().strip()
        now = datetime.now()

        # 1. Verificar si tenemos el precio en cache y si es reciente (< 60s)
        if coin_id in self.cache:
            last_upd = self.last_update.get(coin_id)
            if last_upd and (now - last_upd).total_seconds() < self.update_interval:
                logger.debug(f"Serving {coin_id} from cache (age: {(now - last_upd).total_seconds():.1f}s)")
                return self.cache[coin_id]

        # 2. Si no es reciente, intentar una actualización global si no se ha hecho recientemente
        if not self.global_last_update or (now - self.global_last_update).total_seconds() > self.update_interval:
            # Marcamos como actualizado incluso antes de empezar para evitar peticiones concurrentes duplicadas
            self.global_last_update = now
            logger.info(f"Cache expired or missing. Triggering global price refresh...")
            all_ids = list(set(self.symbol_to_id.values()))
            await self.get_multiple_prices(all_ids)
            
            # Si después de la actualización global tenemos el precio, devolverlo
            if coin_id in self.cache:
                return self.cache[coin_id]

        # 3. Si por alguna razón no está en la actualización global (ID nuevo), pedirlo individualmente
        # pero con cuidado de no saturar
        try:
            url = f"{settings.COINGECKO_API_URL}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true'
            }
            
            logger.debug(f"Fallback request for single coin {coin_id}")
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if coin_id in data and 'usd' in data[coin_id]:
                        price = float(data[coin_id]['usd'])
                        self.cache[coin_id] = price
                        if 'usd_24h_vol' in data[coin_id]:
                            self.volume_cache[coin_id] = float(data[coin_id]['usd_24h_vol'])
                        self.last_update[coin_id] = now
                        return price
                elif response.status == 429:
                    logger.warning(f"Rate limit hit in fallback for {coin_id}")
                
            return self.cache.get(coin_id)
        except Exception as e:
            logger.error(f"Error in fallback price fetch for {coin_id}: {e}")
            return self.cache.get(coin_id)

    async def get_multiple_prices(self, coin_ids: List[str] = None) -> Dict[str, Optional[float]]:
        """Obtiene múltiples precios en una sola llamada y actualiza el cache"""
        if not coin_ids:
            coin_ids = list(set(self.symbol_to_id.values()))
        
        if not self.session or self.session.closed:
            await self.start()
        
        now = datetime.now()
        try:
            # Dividir en grupos de 50 (límite razonable para CoinGecko simple/price)
            chunk_size = 50
            for i in range(0, len(coin_ids), chunk_size):
                chunk = coin_ids[i:i + chunk_size]
                url = f"{settings.COINGECKO_API_URL}/simple/price"
                params = {
                    'ids': ','.join(chunk),
                    'vs_currencies': 'usd',
                    'include_24hr_vol': 'true'
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        for cid in chunk:
                            if cid in data and 'usd' in data[cid]:
                                price = float(data[cid]['usd'])
                                self.cache[cid] = price
                                if 'usd_24h_vol' in data[cid]:
                                    self.volume_cache[cid] = float(data[cid]['usd_24h_vol'])
                                self.last_update[cid] = now
                        logger.info(f"Updated {len(data)} prices and volumes from CoinGecko")
                    elif response.status == 429:
                        logger.warning("Rate limit hit during multiple price fetch")
                        break
                    else:
                        logger.error(f"Error fetching multiple prices: {response.status}")
            
            self.global_last_update = now
            return {cid: self.cache.get(cid) for cid in coin_ids}
        except Exception as e:
            logger.error(f"Exception in multiple price fetch: {e}")
            return {cid: self.cache.get(cid) for cid in coin_ids}

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
