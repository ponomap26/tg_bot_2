import sqlite3
import pandas as pd
from tqdm import tqdm


def create_database():
    # Подключаемся к базе данных
    conn = sqlite3.connect("eve_db.db")
    cursor = conn.cursor()

    # Создаем основную таблицу с требуемыми столбцами
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS eve_items (
        item_id INTEGER PRIMARY KEY,
        item_name TEXT NOT NULL,
        description TEXT,
        group_id INTEGER NOT NULL,
        group_name TEXT NOT NULL,
        category_name TEXT NOT NULL
    )
    """
    )

    # Загружаем данные из Excel файлов
    print("Загрузка данных о категориях...")
    categories_df = pd.read_excel("eve_categories.xlsx")

    print("Загрузка данных о группах...")
    groups_df = pd.read_excel("eve_groups.xlsx")

    print("Загрузка данных о типах...")
    items_df = pd.read_excel("eve_types.xlsx")

    # Создаем словари для быстрого поиска имен
    print("Создание словарей имен...")
    # Словарь категорий: {category_id: category_name}
    category_dict = {
        row["category_id"]: row["name"] for _, row in categories_df.iterrows()
    }

    # Словарь групп: {group_id: {'name': group_name, 'category_id': category_id}}
    group_dict = {}
    for _, row in groups_df.iterrows():
        group_dict[row["group_id"]] = {
            "name": row["name"],
            "category_id": row["category_id"],
        }

    # Заполняем базу данных
    print("\nФормирование и запись данных...")
    inserted_count = 0

    for _, row in tqdm(items_df.iterrows(), total=len(items_df)):
        item_id = row["type_id"]
        item_name = row.get("name", "N/A")
        description = row.get("description", "")  # Получаем описание
        group_id = row.get("group_id", None)

        # Если нет group_id, пропускаем запись
        if not group_id:
            continue

        # Получаем данные о группе
        group_data = group_dict.get(group_id)

        if group_data:
            group_name = group_data["name"]
            category_id = group_data["category_id"]
            category_name = category_dict.get(category_id, "N/A")
        else:
            group_name = "N/A"
            category_name = "N/A"

        # Вставляем данные в таблицу
        cursor.execute(
            """
        INSERT OR IGNORE INTO eve_items 
        (item_id, item_name, description, group_id, group_name, category_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                item_id,
                item_name,
                description,  # Добавляем описание
                group_id,
                group_name,
                category_name,
            ),
        )

        inserted_count += 1

    # Сохраняем изменения
    conn.commit()

    # Создаем индексы для ускорения поиска
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_id ON eve_items(item_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_name ON eve_items(item_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_id ON eve_items(group_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_group_name ON eve_items(group_name)")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_category_name ON eve_items(category_name)"
    )

    # Проверяем количество записей
    cursor.execute("SELECT COUNT(*) FROM eve_items")
    total_rows = cursor.fetchone()[0]

    conn.close()

    print("\nБаза данных успешно создана: eve_online.db")
    print(f"Всего обработано предметов: {inserted_count}")
    print(f"Записей в базе данных: {total_rows}")
    print("Структура таблицы:")
    print("  item_id      - ID предмета")
    print("  item_name    - Название предмета")
    print("  description  - Описание предмета")
    print("  group_id     - ID группы")
    print("  group_name   - Название группы")
    print("  category_name - Название категории")


if __name__ == "__main__":
    create_database()
