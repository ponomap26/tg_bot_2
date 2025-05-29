from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Старт"),
        ],
        [KeyboardButton(text="Выбор товара")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует",
)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


# Создание клавиатуры для старта
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Старт"),
        ],
        [KeyboardButton(text="Выбор товара")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует",
)


# Создание клавиатуры для старта с тремя кнопками
start_kb3 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="о нас"),
        ],
        [KeyboardButton(text="Выбор товара")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует",
)


# Удаление клавиатуры
del_kb = ReplyKeyboardRemove()


# Создание клавиатуры с типами
types_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="PLEX"), KeyboardButton(text="Skill Extractor")],
        [KeyboardButton(text="Large Skill Injector"), KeyboardButton(text="News EVE")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует",
)

start_kb3 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="о нас"),
        ],
        [KeyboardButton(text="Выбор товара")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует",
)
del_kb = ReplyKeyboardRemove()

# start_kb2 = ReplyKeyboardBuilder()
# start_kb2.add(
#     KeyboardButton(text='О нас'),
#     KeyboardButton(text='Выбор товара'),
# )
#
# start_kb3 = ReplyKeyboardBuilder()
# start_kb3.attach(start_kb2)

types_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="PLEX"), KeyboardButton(text="Skill Extractor")],
        [KeyboardButton(text="Large Skill Injector"), KeyboardButton(text="News EVE")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Что вас интересует",
)
