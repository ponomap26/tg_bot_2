import aiohttp
import asyncio
import pandas as pd
import time
from tqdm import tqdm


async def fetch_total_pages(session):
    """Получаем общее количество страниц с группами"""
    url = "https://esi.evetech.net/latest/universe/groups/?datasource=tranquility"
    async with session.get(url) as response:
        if "X-Pages" in response.headers:
            return int(response.headers["X-Pages"])
        return 1


async def fetch_group_ids(session, page):
    """Получаем список ID групп для указанной страницы"""
    url = f"https://esi.evetech.net/latest/universe/groups/?datasource=tranquility&page={page}"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        return []


async def fetch_group_details(session, group_id, pbar, retries=3):
    """Получаем детальную информацию о группе с обработкой ошибок"""
    url = f"https://esi.evetech.net/latest/universe/groups/{group_id}/?datasource=tranquility&language=ru"

    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    pbar.update(1)
                    return {
                        "group_id": data.get("group_id", group_id),
                        "name": data.get("name", "N/A"),
                        "category_id": data.get("category_id", "N/A"),
                        "published": data.get("published", False),
                        "types_count": len(data.get("types", [])),
                    }
                elif response.status == 404:
                    pbar.update(1)
                    return None
                elif response.status == 420:  # Ошибка ограничения скорости
                    wait = int(response.headers.get("Retry-After", 10))
                    await asyncio.sleep(wait)
                    continue
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < retries - 1:
                await asyncio.sleep(2**attempt)  # экспоненциальная задержка
            else:
                print(f"\nОшибка получения group_id {group_id}: {str(e)}")
                pbar.update(1)
                return None

    pbar.update(1)
    return None


async def main():
    print("Начало загрузки данных о группах EVE Online...")
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        # Шаг 1: Определение общего количества страниц
        print("Определение общего количества страниц...")
        total_pages = await fetch_total_pages(session)
        print(f"Всего страниц для обработки: {total_pages}")

        # Шаг 2: Получение всех ID групп
        print("\nЗагрузка ID групп...")
        all_group_ids = []

        # Создаем задачи для всех страниц
        tasks = [fetch_group_ids(session, page) for page in range(1, total_pages + 1)]

        with tqdm(total=total_pages, desc="Страницы с ID групп") as pbar:
            for task in asyncio.as_completed(tasks):
                group_ids = await task
                if group_ids:
                    all_group_ids.extend(group_ids)
                pbar.update(1)

        total_groups = len(all_group_ids)
        print(f"\nВсего групп для загрузки: {total_groups}")

        # Шаг 3: Получение детальной информации о группах
        print("\nЗагрузка детальной информации о группах...")
        detail_tasks = []

        with tqdm(total=total_groups, desc="Группы", unit="group") as pbar:
            for group_id in all_group_ids:
                task = fetch_group_details(session, group_id, pbar)
                detail_tasks.append(task)

            group_details = await asyncio.gather(*detail_tasks)

        # Фильтрация и сохранение данных
        valid_data = [data for data in group_details if data is not None]
        success_rate = len(valid_data) / total_groups * 100

        # Создаем DataFrame и сохраняем в Excel
        df = pd.DataFrame(valid_data)
        output_file = "eve_groups.xlsx"
        df.to_excel(output_file, index=False)

        # Статистика выполнения
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 60)
        print(
            f"Успешно загружено: {len(valid_data)}/{total_groups} групп ({success_rate:.1f}%)"
        )
        print(f"Общее время выполнения: {elapsed_time:.2f} секунд")
        print(f"Средняя скорость: {total_groups/elapsed_time:.2f} запросов/сек")
        print(f"Результаты сохранены в файл: {output_file}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
