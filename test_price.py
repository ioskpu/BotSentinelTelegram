
import asyncio
import sys
import os

# Añadir el directorio raíz al path para poder importar src
sys.path.append(os.getcwd())

from src.services.price_monitor import PriceMonitor
from src.config.settings import settings

async def test_price_fetching():
    print("🚀 Probando PriceMonitor...")
    monitor = PriceMonitor()
    await monitor.start()
    
    # Probar obtener precio de SOL
    print("\n🔍 Obteniendo precio de SOL (por símbolo)...")
    price_sol = await monitor.get_price_by_symbol('SOL')
    if price_sol:
        print(f"✅ Precio de SOL: ${price_sol:,.4f}")
    else:
        print("❌ No se pudo obtener el precio de SOL")

    # Probar obtener precio de XLM
    print("\n🔍 Obteniendo precio de XLM (por símbolo)...")
    price_xlm = await monitor.get_price_by_symbol('XLM')
    if price_xlm:
        print(f"✅ Precio de XLM: ${price_xlm:,.4f}")
    else:
        print("❌ No se pudo obtener el precio de XLM")

    # Probar obtener múltiples precios
    print("\n🔍 Obteniendo múltiples precios...")
    prices = await monitor.get_multiple_prices(['bitcoin', 'ethereum', 'solana'])
    for coin, price in prices.items():
        if price:
            print(f"✅ {coin.capitalize()}: ${price:,.2f}")
        else:
            print(f"❌ No se pudo obtener el precio de {coin}")

    await monitor.stop()
    print("\n🏁 Prueba finalizada.")

if __name__ == "__main__":
    asyncio.run(test_price_fetching())
