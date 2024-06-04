from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f
import asyncio

from kbds.reply import types_kb, start_kb3
from request.requestApi_Plex import get_price
from request.requestApi_Skill import get_price_skill
from request.requestApiLargSkill import get_price_Larg_skill
from parser.parser import get_news

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Приветствую в боте для игры Eve Online!\n"
                         "Бот позволяет отслеживать цены на товары в игре Eve Online.",
                         reply_markup=start_kb3)

@user_private_router.message(F.text.lower() == "о нас")
async def tags_add(message: types.Message):
    await message.answer('Если интересен бот Можете помочь исками в игре\n игровой ник Sword Adoudel')


@user_private_router.message(Command('tags'))
async def tags_add(message: types.Message):
    await message.answer('Выбор позиции', reply_markup=types_kb)


@user_private_router.message(F.text.lower() == "выбор товара")
async def tags_add(message: types.Message):
    await message.answer('Выбор позиции', reply_markup=types_kb)


@user_private_router.message(F.text.lower() == "plex")
async def plex_age(message: types.Message):

    # Отображаем сообщение "Загружаю..."
    await message.answer("Загружаю данные...")

    # Получаем данные о PLEX
    prise = await get_price()  # Предполагается, что get_price() возвращает словарь

    # Проверяем, что данные были получены
    try:
        result = '\n'.join(f'{k}={v}' for k, v in prise.items())
        await message.answer(f'Полученные данные по PLEX:\n {result}')
    except Exception:
        # Если данные не были получены, выводим соответствующее сообщение
        await message.answer("К сожалению, данные о PLEX недоступны в данный момент.")

# # Удаляем сообщение "Загружаю..."
#         await message.delete()
@user_private_router.message(F.text.lower() == "skill extractor")
async def skill_age(message: types.Message):
    await message.answer("Загружаю данные...")
    prise = await get_price_skill()
    try:
        result = '\n'.join(f'{k}={v}' for k, v in prise.items())

        await message.answer(f'Полученные данные по SKILL:\n' f'{result}')
    except Exception:
        await message.answer("К сожалению, данные о skill extractor недоступны в данный момент.")
@user_private_router.message(F.text.lower() == "large skill injector")
async def larg_skill_age(message: types.Message):
    await message.answer("Загружаю данные...")
    prise = await get_price_Larg_skill()
    try:
        result = '\n'.join(f'{k}={v}' for k, v in prise.items())

        await message.answer(f'Полученные данные по Skill injector: \n {result}')
    except Exception:
            await message.answer("К сожалению, данные о large skill injector недоступны в данный момент.")
@user_private_router.message(F.text.lower() == "news eve")
async def news_eve(message: types.Message):
    await message.answer("Загружаю данные...")
    news = get_news()  # Предполагается, что get_news() возвращает список новостей
    news_eve = '\n'.join(news)  # Преобразуем список новостей в строку, разделенную на строки
    await message.answer(f'Последние новости:\n \n {news_eve}')  # Отправляем строку новостей
