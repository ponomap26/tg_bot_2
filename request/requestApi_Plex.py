import requests
import asyncio
import aiohttp

region_list = [10000002, 10000030, 10000042, 10000043, 10000032]
regionMap = {
    "Jita": {
        "regionId": 10000002,
    },
    "Rens": {
        "regionId": 10000030,
    },
    "Hek": {
        "regionId": 10000042,
    },
    "Amarr": {
        "regionId": 10000043,
    },
    "Dodixie": {
        "regionId": 10000032,
    },
}

async def get_price():
    price_list = {}

    async with aiohttp.ClientSession() as session:
        for regionId in region_list:
            regionName = [region for region, data in regionMap.items() if data['regionId'] == regionId][0]
            async with session.get(
                    f'https://esi.evetech.net/dev/markets/{regionId}/orders/?datasource=tranquility&order_type=sell&page=1&type_id=44992') as response:
                data_sell = await response.json()
                data_price_sell = min(data_sell, key=lambda x: x['price'])['price']


            async with session.get(
                    f'https://esi.evetech.net/dev/markets/{regionId}/orders/?datasource=tranquility&order_type=buy&page=1&type_id=44992') as response:
                data_buy = await response.json()
                data_price_buy = max(data_buy, key=lambda x: x['price'])['price']

                price_list[regionName] = f'продажа : {data_price_sell}, покупка: {data_price_buy}'

        return price_list

# get_price()
