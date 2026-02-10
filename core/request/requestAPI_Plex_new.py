import requests
import json
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


class EVEAPIClient:
    """
    Клиент для работы с EVE Online ESI API
    """

    def __init__(self):
        self.base_url = "https://esi.evetech.net/latest"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "PLEX-Price-Checker/1.0 (your-email@example.com)",
        }

    def get_regions(self) -> Optional[List[int]]:
        """
        Получает список всех регионов
        GET /universe/regions/
        """
        endpoint = f"{self.base_url}/universe/regions/"
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения регионов: {e}")
            return None

    def get_region_info(self, region_id: int) -> Optional[Dict]:
        """
        Получает информацию о регионе
        GET /universe/regions/{region_id}/
        """
        endpoint = f"{self.base_url}/universe/regions/{region_id}/"
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    def get_market_orders(
        self, region_id: int, type_id: int, order_type: str = "sell", page: int = 1
    ) -> Optional[List[Dict]]:
        """
        Получает ордера на рынке
        GET /markets/{region_id}/orders/
        """
        endpoint = f"{self.base_url}/markets/{region_id}/orders/"
        params = {"type_id": type_id, "order_type": order_type, "page": page}

        try:
            response = requests.get(
                endpoint, params=params, headers=self.headers, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    def get_all_market_orders(
        self, region_id: int, type_id: int, order_type: str = "sell"
    ) -> List[Dict]:
        """
        Получает все ордера с пагинацией
        """
        all_orders = []
        page = 1

        while True:
            orders = self.get_market_orders(region_id, type_id, order_type, page)
            if not orders:
                break

            # Добавляем region_id к каждому ордеру для идентификации
            for order in orders:
                order["region_id"] = region_id

            all_orders.extend(orders)

            if len(orders) < 1000:
                break

            page += 1
            if page > 20:  # Защита
                break

        return all_orders


def get_all_regions_plex_prices():
    """
    Получает PLEX цены во всех регионах и выводит топ-10 самых низких
    """
    PLEX_TYPE_ID = 44992

    client = EVEAPIClient()

    # Получаем список всех регионов
    print("Загрузка списка регионов...")
    regions = client.get_regions()

    if not regions:
        print("Не удалось получить список регионов")
        return

    print(f"Найдено регионов: {len(regions)}")
    print(
        "Загрузка sell-ордеров на PLEX из всех регионов (это может занять 1-2 минуты)..."
    )

    all_orders = []

    # Параллельная загрузка для ускорения
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_region = {
            executor.submit(
                client.get_all_market_orders, region_id, PLEX_TYPE_ID, "sell"
            ): region_id
            for region_id in regions
        }

        completed = 0
        for future in as_completed(future_to_region):
            region_id = future_to_region[future]
            completed += 1

            try:
                orders = future.result()
                if orders:
                    all_orders.extend(orders)

                # Прогресс
                if completed % 10 == 0 or completed == len(regions):
                    print(f"  Обработано {completed}/{len(regions)} регионов...")

            except Exception as e:
                print(f"  Ошибка в регионе {region_id}: {e}")

    if not all_orders:
        print("Не удалось получить данные")
        return

    # Сортируем по цене (от меньшей к большей)
    sorted_orders = sorted(all_orders, key=lambda x: x.get("price", float("inf")))

    # Берем топ-10
    top_10 = sorted_orders[:10]

    # Получаем названия регионов для топ-10
    print("\nЗагрузка названий регионов...")
    region_names = {}
    for order in top_10:
        region_id = order.get("region_id")
        if region_id not in region_names:
            info = client.get_region_info(region_id)
            region_names[region_id] = (
                info.get("name", f"Region {region_id}")
                if info
                else f"Region {region_id}"
            )

    # Вывод результатов
    print("\n" + "=" * 100)
    print("🏆 ТОП-10 САМЫХ НИЗКИХ ЦЕН НА PLEX ПО ВСЕЙ ВСЕЛЕННОЙ EVE")
    print(
        f"Всего проанализировано ордеров: {len(all_orders):,} из {len(regions)} регионов"
    )
    print("=" * 100)
    print(
        f"{'№':<4} {'Кол-во':<10} {'Цена за шт.':<22} {'Сумма ордера':<25} {'Регион':<25} {'Станция ID':<15}"
    )
    print("-" * 100)

    for i, order in enumerate(top_10, 1):
        volume = order.get("volume_remain", 0)
        price = order.get("price", 0.0)
        location_id = order.get("location_id", "N/A")
        region_id = order.get("region_id", 0)
        total = volume * price

        region_name = region_names.get(region_id, f"Region {region_id}")

        # Обрезаем длинные названия регионов
        region_display = region_name[:24]

        print(
            f"{i:<4} {volume:<10} {price:>18,.2f} ISK {total:>21,.2f} ISK {region_display:<25} {location_id:<15}"
        )

    print("=" * 100)

    # Статистика
    if len(sorted_orders) > 0:
        min_price = sorted_orders[0].get("price", 0)
        max_price = sorted_orders[-1].get("price", 0)

        # Находим среднюю цену первых 100 ордеров
        top_100 = sorted_orders[:100]
        avg_price = sum(o.get("price", 0) for o in top_100) / len(top_100)

        print(f"\n📊 СТАТИСТИКА:")
        print(
            f"   Минимальная цена:     {min_price:>18,.2f} ISK (регион: {region_names.get(top_10[0].get('region_id'), 'N/A')})"
        )
        print(f"   Средняя цена (топ100): {avg_price:>18,.2f} ISK")
        print(f"   Максимальная цена:    {max_price:>18,.2f} ISK")
        print(f"   Разброс цен:           {(max_price - min_price):>18,.2f} ISK")

    return top_10


# def get_cheapest_plex_fast():
#     """
#     Ускоренная версия - проверяет только основные торговые регионы
#     """
#     PLEX_TYPE_ID = 44992
#
#     # Основные торговые хабы и активные регионы
#     priority_regions = [
#         10000002,  # The Forge (Jita)
#         10000043,  # Domain (Amarr)
#         10000032,  # Sinq Laison (Dodixie)
#         10000030,  # Heimatar (Rens)
#         10000042,  # Metropolis (Hek)
#         10000016,  # Lonetrek
#         10000033,  # The Citadel
#         10000052,  # Kador
#         10000044,  # Kor-Azor
#         10000067,  # Genesis
#         10000020,  # Tash-Murkon
#         10000028,  # Molden Heath
#         10000055,  # Aridia
#         10000054,  # Black Rise
#         10000037,  # Everyshore
#     ]
#
#     client = EVEAPIClient()
#
#     print("Быстрая проверка основных торговых регионов...")
#     all_orders = []
#
#     for region_id in priority_regions:
#         orders = client.get_all_market_orders(region_id, PLEX_TYPE_ID, "sell")
#         if orders:
#             all_orders.extend(orders)
#             print(f"  ✓ Регион {region_id}: {len(orders)} ордеров")
#         else:
#             print(f"  ✗ Регион {region_id}: нет данных")
#
#     if not all_orders:
#         return
#
#     # Сортируем и выводим топ-10
#     sorted_orders = sorted(all_orders, key=lambda x: x.get("price", float("inf")))
#     top_10 = sorted_orders[:10]
#
#     # Получаем названия регионов
#     region_names = {}
#     for order in top_10:
#         region_id = order.get("region_id")
#         if region_id not in region_names:
#             info = client.get_region_info(region_id)
#             region_names[region_id] = (
#                 info.get("name", f"Region {region_id}")
#                 if info
#                 else f"Region {region_id}"
#             )
#
#     print("\n" + "=" * 95)
#     print("🚀 ТОП-10 САМЫХ ДЕШЕВЫХ PLEX (ОСНОВНЫЕ ТОРГОВЫЕ РЕГИОНЫ)")
#     print("=" * 95)
#     print(
#         f"{'№':<4} {'Кол-во':<10} {'Цена за шт.':<22} {'Сумма ордера':<25} {'Регион':<20} {'Станция ID':<15}"
#     )
#     print("-" * 95)
#
#     for i, order in enumerate(top_10, 1):
#         volume = order.get("volume_remain", 0)
#         price = order.get("price", 0.0)
#         location_id = order.get("location_id", "N/A")
#         region_id = order.get("region_id", 0)
#         total = volume * price
#
#         region_name = region_names.get(region_id, f"Region {region_id}")[:19]
#
#         print(
#             f"{i:<4} {volume:<10} {price:>18,.2f} ISK {total:>21,.2f} ISK {region_name:<20} {location_id:<15}"
#         )
#
#     print("=" * 95)
#
#     return top_10


if __name__ == "__main__":
    # Выберите режим:

    # 1. Полная проверка ВСЕХ регионов (медленнее, ~1-2 минуты)
    print("РЕЖИМ 1: ПОЛНАЯ ПРОВЕРКА ВСЕХ РЕГИОНОВ")
    print("=" * 50)
    get_all_regions_plex_prices()

    # 2. Быстрая проверка только основных торговых хабов (раскомментируйте)
    # print("\n\nРЕЖИМ 2: БЫСТРАЯ ПРОВЕРКА ОСНОВНЫХ ХАБОВ")
    # print("=" * 50)
    # get_cheapest_plex_fast()
