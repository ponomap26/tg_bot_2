import aiohttp
from aiohttp import ClientResponse
import asyncio
import json

region_map = {
    10000002: "Jita",
    10000030: "Rens",
    10000042: "Hek",
    10000043: "Amarr",
    10000032: "Dodixie",
}

async def get_price_skill():
    price_skill = {}

    async with aiohttp.ClientSession() as session:
        for regionId in region_map:
            regionName = region_map[regionId]

            try:
                async with session.get(f'https://esi.evetech.net/dev/markets/{regionId}/orders/?datasource=tranquility&order_type=sell&page=1&type_id=40519') as response:
                    data_sell = await response.json()
                    if data_sell:
                        data_price_sell = min(data_sell, key=lambda x: x['price'])['price']
                    else:
                        data_price_sell = "нет данных"

                async with session.get(f'https://esi.evetech.net/dev/markets/{regionId}/orders/?datasource=tranquility&order_type=buy&page=1&type_id=40519') as response:
                    data_buy = await response.json()
                    if data_buy:
                        data_price_buy = max(data_buy, key=lambda x: x['price'])['price']
                    else:
                        data_price_buy = "нет данных"

                price_skill[regionName] = f'продажа :{data_price_sell},  покупка: {data_price_buy}'
            except (ClientResponseError, ValueError) as e:
                print(f"Ошибка при получении данных о ценах: {e}")

        return price_skill
