
import asyncio
import aiohttp

async def test_all_coins():
    coins = {
        'BTC': 'bitcoin',
        'SOL': 'solana',
        'XLM': 'stellar',
        'ACU': 'acurast',
        'BNB': 'binancecoin',
        'LTC': 'litecoin',
        'PEPE': 'pepe',
        'USDT': 'tether',
        'USDC': 'usd-coin'
    }
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': ','.join(coins.values()),
        'vs_currencies': 'usd'
    }
    
    print(f"Testing all coins at once...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Data: {data}")
                    for symbol, coin_id in coins.items():
                        price = data.get(coin_id, {}).get('usd')
                        print(f"{symbol} ({coin_id}): {price}")
                else:
                    print(f"Error: {await response.text()}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_coins())
