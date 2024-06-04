from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Старт'),
        ],
        [
            KeyboardButton(text='Выбор товара')
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует'
)


start_kb3 = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='о нас'),
        ],
        [
            KeyboardButton(text='Выбор товара')
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует'
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
        [KeyboardButton(text='PLEX'), KeyboardButton(text='Skill Extractor')],
        [KeyboardButton(text='Large Skill Injector'), KeyboardButton(text='News EVE')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует'
)

