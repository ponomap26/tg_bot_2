import sqlite3
import aiohttp
import asyncio
from aiohttp import ClientResponseError

# Конфигурация регионов
region_list = [10000002, 10000030, 10000042, 10000043, 10000032]
regionMap = {
    "Jita": 10000002,
    "Rens": 10000030,
    "Hek": 10000042,
    "Amarr": 10000043,
    "Dodixie": 10000032,
}


def get_item_id(item_name: str) -> int:
    """Ищет ID предмета по названию в базе данных (регистронезависимо)"""
    conn = sqlite3.connect("eve_online.db")
    cursor = conn.cursor()

    # Регистронезависимый поиск
    cursor.execute(
        """
        SELECT item_id 
        FROM eve_items 
        WHERE LOWER(item_name) = LOWER(?)
    """,
        (item_name,),
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


async def get_item_prices(item_id: int) -> dict:
    """Получает цены на предмет по его ID во всех регионах"""
    price_info = {}
    async with aiohttp.ClientSession() as session:
        for region_id in region_list:
            region_name = next(
                name for name, rid in regionMap.items() if rid == region_id
            )

            try:
                # Получаем ордера на продажу
                async with session.get(
                    f"https://esi.evetech.net/dev/markets/{region_id}/orders/",
                    params={
                        "datasource": "tranquility",
                        "order_type": "sell",
                        "page": 1,
                        "type_id": item_id,
                    },
                ) as response:
                    if response.status == 200:
                        data_sell = await response.json()
                        sell_price = (
                            min([o["price"] for o in data_sell]) if data_sell else None
                        )
                    else:
                        sell_price = None

                # Получаем ордера на покупку
                async with session.get(
                    f"https://esi.evetech.net/dev/markets/{region_id}/orders/",
                    params={
                        "datasource": "tranquility",
                        "order_type": "buy",
                        "page": 1,
                        "type_id": item_id,
                    },
                ) as response:
                    if response.status == 200:
                        data_buy = await response.json()
                        buy_price = (
                            max([o["price"] for o in data_buy]) if data_buy else None
                        )
                    else:
                        buy_price = None

                price_info[region_name] = {"sell": sell_price, "buy": buy_price}

            except (ClientResponseError, ValueError, KeyError) as e:
                print(f"Ошибка при получении цен для региона {region_name}: {e}")
                price_info[region_name] = {"sell": None, "buy": None}

    return price_info


async def get_item_price_by_name(item_name: str) -> dict:
    """Основная функция для получения цен по названию предмета"""
    # Ищем ID предмета в базе
    item_id = get_item_id(item_name)

    if not item_id:
        return {"error": f"Предмет '{item_name}' не найден в базе данных"}

    # Получаем цены по найденному ID
    return await get_item_prices(item_id)
