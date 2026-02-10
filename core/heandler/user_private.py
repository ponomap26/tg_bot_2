from typing import List, Dict

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

from core.kbds.reply import types_kb, start_kb3
from core.parser.parsNews import parser
from core.request.requestApi_Plex import get_price
from core.request.requestApi_Skill import get_price_skill
from core.request.requestApiLargSkill import get_price_Larg_skill


user_private_router = Router()


def format_news(news_list: List[Dict], limit: int = 5) -> str:
    """Форматирует список новостей для отправки в Telegram"""
    if not news_list:
        return "Новости не найдены."

    formatted = ["📰 <b>Последние новости EVE Online:</b>\n"]

    for i, news in enumerate(news_list[:limit], 1):
        title = news.get("title", "Без заголовка")
        date = news.get("date", "Дата неизвестна")
        author = news.get("author", "Автор неизвестен")
        link = news.get("link", "")
        description = news.get("description", "")

        # Обрезаем описание если оно слишком длинное
        if description and len(description) > 200:
            description = description[:200] + "..."

        news_text = f"\n{i}. <b>{title}</b>\n"
        news_text += f"📅 {date} | ✍️ {author}\n"
        if description:
            news_text += f"📝 {description}\n"
        if link:
            news_text += f"🔗 <a href='{link}'>Читать полностью</a>\n"

        formatted.append(news_text)

    return "\n".join(formatted)


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        "Приветствую в боте для игры Eve Online!\n"
        "Бот позволяет отслеживать цены на товары в игре Eve Online.",
        reply_markup=start_kb3,
    )


@user_private_router.message(F.text.lower() == "о нас")
async def tags_add(message: types.Message):
    await message.answer(
        "Если интересен бот Можете помочь исками в игре\n игровой ник Sword Adoudel"
    )


@user_private_router.message(Command("tags"))
async def tags_add(message: types.Message):
    await message.answer("Выбор позиции", reply_markup=types_kb)


@user_private_router.message(F.text.lower() == "выбор товара")
async def tags_add(message: types.Message):
    await message.answer("Выбор позиции", reply_markup=types_kb)


@user_private_router.message(F.text.lower() == "plex")
async def plex_age(message: types.Message):

    # Отображаем сообщение "Загружаю..."
    await message.answer("Загружаю данные...")

    # Получаем данные о PLEX
    prise = await get_price()  # Предполагается, что get_price() возвращает словарь

    # Проверяем, что данные были получены
    try:
        result = "\n".join(f"{k}={v}" for k, v in prise.items())
        await message.answer(f"Полученные данные по PLEX:\n {result}")
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
        result = "\n".join(f"{k}={v}" for k, v in prise.items())

        await message.answer(f"Полученные данные по SKILL:\n" f"{result}")
    except Exception:
        await message.answer(
            "К сожалению, данные о skill extractor недоступны в данный момент."
        )


@user_private_router.message(F.text.lower() == "large skill injector")
async def larg_skill_age(message: types.Message):
    await message.answer("Загружаю данные...")
    prise = await get_price_Larg_skill()
    try:
        result = "\n".join(f"{k}={v}" for k, v in prise.items())

        await message.answer(f"Полученные данные по Skill injector: \n {result}")
    except Exception:
        await message.answer(
            "К сожалению, данные о large skill injector недоступны в данный момент."
        )


@user_private_router.message(F.text.lower() == "news eve")
async def news_eve(message: types.Message):
    await message.answer("⏳ Загружаю данные...")

    try:
        # Получаем новости через парсер
        news = parser.parse_news_page()

        if news:
            formatted_news = format_news(news, limit=5)
            # Отправляем с parse_mode='HTML' для форматирования
            await message.answer(
                formatted_news, parse_mode="HTML", disable_web_page_preview=True
            )
        else:
            await message.answer("❌ Не удалось получить новости. Попробуйте позже.")

    except Exception as e:
        await message.answer(f"❌ Ошибка при получении новостей: {str(e)}")
