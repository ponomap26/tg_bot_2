import aiohttp
import asyncio
import pandas as pd
import time
from tqdm import tqdm  # Для отображения прогресса


async def fetch_category_ids(session, page):
    """Асинхронно получает список ID категорий для указанной страницы"""
    url = f"https://esi.evetech.net/latest/universe/categories/?datasource=tranquility&page={page}"
    async with session.get(url) as response:
        return await response.json()


async def fetch_category_details(session, category_id, pbar):
    """Асинхронно получает детальную информацию о категории"""
    url = f"https://esi.evetech.net/latest/universe/categories/{category_id}/?datasource=tranquility&language=ru"
    try:
        async with session.get(url) as response:
            data = await response.json()
            # Обновляем прогресс-бар после успешного получения данных
            pbar.update(1)
            return {
                "category_id": data.get("category_id", "N/A"),
                "groups": len(data.get("groups", [])),
                "name": data.get("name", "N/A"),
                "published": data.get("published", False),
            }
    except Exception as e:
        # Обновляем прогресс-бар даже при ошибке
        pbar.update(1)
        print(f"\nError fetching category {category_id}: {str(e)}")
        return None
    finally:
        # Имитация задержки для соблюдения лимитов API (100 запросов/сек)
        await asyncio.sleep(0.05)


async def main():
    print("Начало загрузки данных EVE Online...")
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        # Этап 1: Получаем все ID категорий
        print("Получение списка категорий...")
        id_tasks = []
        for page in range(1, 49):
            id_tasks.append(fetch_category_ids(session, page))

        # Отображаем прогресс загрузки ID
        pages_data = []
        with tqdm(total=48, desc="Страницы категорий") as pbar:
            for task in asyncio.as_completed(id_tasks):
                data = await task
                pages_data.append(data)
                pbar.update(1)

        # Объединяем все ID категорий
        all_ids = []
        for page_data in pages_data:
            all_ids.extend(page_data)
        total_categories = len(all_ids)
        print(f"\nНайдено категорий: {total_categories}")

        # Этап 2: Получаем детали для всех категорий
        print("\nЗагрузка детальной информации...")
        detail_tasks = []

        # Создаем прогресс-бар для детальной информации
        with tqdm(
            total=total_categories, desc="Обработка категорий", unit="cat"
        ) as pbar:
            for cid in all_ids:
                task = fetch_category_details(session, cid, pbar)
                detail_tasks.append(task)

            # Выполняем все задачи параллельно
            category_details = await asyncio.gather(*detail_tasks)

        # Фильтруем возможные ошибки
        valid_data = [data for data in category_details if data is not None]
        success_rate = len(valid_data) / total_categories * 100

        # Сохраняем в Excel
        df = pd.DataFrame(valid_data)
        df.to_excel("eve_categories.xlsx", index=False)

        # Выводим статистику
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 50)
        print(
            f"Успешно обработано: {len(valid_data)}/{total_categories} категорий ({success_rate:.1f}%)"
        )
        print(f"Общее время выполнения: {elapsed_time:.2f} секунд")
        print(f"Средняя скорость: {total_categories/elapsed_time:.1f} запросов/сек")
        print(f"Результаты сохранены в файл: eve_categories.xlsx")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
