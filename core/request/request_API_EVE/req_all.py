import aiohttp
import asyncio
import pandas as pd
import time
from tqdm import tqdm


async def fetch_total_pages(session):
    """Получаем общее количество страниц с типами"""
    url = "https://esi.evetech.net/latest/universe/types/?datasource=tranquility&page=1"
    async with session.get(url) as response:
        if "X-Pages" in response.headers:
            return int(response.headers["X-Pages"])
    return 1


async def fetch_type_ids(session, page):
    """Получаем список ID типов для указанной страницы"""
    url = f"https://esi.evetech.net/latest/universe/types/?datasource=tranquility&page={page}"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        return []


async def fetch_type_details(session, type_id, pbar, retries=3):
    """Получаем детальную информацию о типе с обработкой ошибок"""
    url = f"https://esi.evetech.net/latest/universe/types/{type_id}/?datasource=tranquility&language=ru"

    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    pbar.update(1)
                    return {
                        "type_id": data.get("type_id", type_id),
                        "name": data.get("name", "N/A"),
                        "description": data.get("description", "")[
                            :500
                        ],  # ограничиваем длину
                        "group_id": data.get("group_id", "N/A"),
                        "market_group_id": data.get("market_group_id", "N/A"),
                        "mass": data.get("mass", 0),
                        "packaged_volume": data.get("packaged_volume", 0),
                        "portion_size": data.get("portion_size", 1),
                        "published": data.get("published", False),
                        "radius": data.get("radius", 0),
                        "volume": data.get("volume", 0),
                        "capacity": data.get("capacity", 0),
                        "graphic_id": data.get("graphic_id", "N/A"),
                        "icon_id": data.get("icon_id", "N/A"),
                    }
                elif response.status == 404:
                    pbar.update(1)
                    return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < retries - 1:
                await asyncio.sleep(2**attempt)  # экспоненциальная задержка
            else:
                print(f"\nОшибка получения type_id {type_id}: {str(e)}")
                pbar.update(1)
                return None

    pbar.update(1)
    return None


async def main():
    print("Начало загрузки данных о типах EVE Online...")
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        # Шаг 1: Определение общего количества страниц
        print("Определение общего количества страниц...")
        total_pages = await fetch_total_pages(session)
        print(f"Всего страниц для обработки: {total_pages}")

        # Шаг 2: Получение всех ID типов
        print("\nЗагрузка ID типов...")
        all_type_ids = []

        # Создаем задачи для всех страниц
        tasks = [fetch_type_ids(session, page) for page in range(1, total_pages + 1)]

        with tqdm(total=total_pages, desc="Страницы с ID типов") as pbar:
            for task in asyncio.as_completed(tasks):
                type_ids = await task
                if type_ids:
                    all_type_ids.extend(type_ids)
                pbar.update(1)

        total_types = len(all_type_ids)
        print(f"\nВсего типов для загрузки: {total_types}")

        # Шаг 3: Получение детальной информации о типах
        print("\nЗагрузка детальной информации о типах...")
        detail_tasks = []

        with tqdm(total=total_types, desc="Типы", unit="type") as pbar:
            for type_id in all_type_ids:
                task = fetch_type_details(session, type_id, pbar)
                detail_tasks.append(task)

            type_details = await asyncio.gather(*detail_tasks)

        # Фильтрация и сохранение данных
        valid_data = [data for data in type_details if data is not None]
        success_rate = len(valid_data) / total_types * 100

        # Создаем DataFrame и сохраняем в Excel
        df = pd.DataFrame(valid_data)
        output_file = "eve_types.xlsx"
        df.to_excel(output_file, index=False)

        # Статистика выполнения
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 60)
        print(
            f"Успешно загружено: {len(valid_data)}/{total_types} типов ({success_rate:.1f}%)"
        )
        print(f"Общее время выполнения: {elapsed_time:.2f} секунд")
        print(f"Средняя скорость: {total_types/elapsed_time:.2f} запросов/сек")
        print(f"Размер данных: {len(df)} строк, {len(df.columns)} столбцов")
        print(f"Результаты сохранены в файл: {output_file}")
        print("=" * 60)


if __name__ == "__main__":
    # Увеличиваем лимит на количество одновременных соединений
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
