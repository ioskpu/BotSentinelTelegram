
import asyncio
import aiohttp
import sys

async def test_coingecko():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin,solana,stellar,acurast',
        'vs_currencies': 'usd'
    }
    
    print(f"Testing CoinGecko API: {url}")
    print(f"Params: {params}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15) as response:
                print(f"Status Code: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Response Data: {data}")
                else:
                    text = await response.text()
                    print(f"Error Response: {text}")
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_coingecko())
