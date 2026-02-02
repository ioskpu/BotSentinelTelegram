
import asyncio
import sys
import os

# Añadir el directorio raíz al path para poder importar src
sys.path.append(os.getcwd())

from src.services.price_monitor import PriceMonitor
from src.config.settings import settings
from loguru import logger

async def test_monitor():
    monitor = PriceMonitor()
    await monitor.start()
    
    symbols = ['BTC', 'SOL', 'ACU', 'PEPE', 'BITCOIN']
    
    print(f"--- Testing PriceMonitor directly ---")
    for symbol in symbols:
        price = await monitor.get_price_by_symbol(symbol)
        coin_id = monitor.symbol_to_id.get(symbol.upper())
        print(f"Symbol: {symbol} | ID: {coin_id} | Price: {price}")
        
    await monitor.stop()

if __name__ == "__main__":
    asyncio.run(test_monitor())
