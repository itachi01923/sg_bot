from aiohttp import ClientSession
from config.config import settings


class CMCHTTPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.api_key = settings.CMC_API_KEY

    async def get_currency(self, symbol: str):
        async with ClientSession(
                base_url=self.base_url,
                headers={
                    'X-CMC_PRO_API_KEY': self.api_key,
                }
        ) as session:
            async with session.get(
                    url="/v2/cryptocurrency/quotes/latest",
                    params={"symbol": symbol, 'convert': 'RUB'}
            ) as resp:
                result = await resp.json()

                return result["data"][symbol][0]["quote"]["RUB"]["price"]
