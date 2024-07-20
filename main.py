import asyncio
import logging
import os


from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv

from heandler.user_private import user_private_router

load_dotenv(find_dotenv())

TOKEN = os.getenv("TOKEN")
ALLOWED_UPDATE = ["message", "edited_message"]
bot = Bot(token=TOKEN)

dp = Dispatcher()

dp.include_router(user_private_router)

logging.debug("Это сообщение для отладки программы")
logging.info("Информационное сообщение")


def setup_logger():

    logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    setup_logger()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        allowed_updates=ALLOWED_UPDATE,
    )


if __name__ == "__main__":

    try:
        print("Бот запущен")

        asyncio.run(main())

    except KeyboardInterrupt:
        print("Бот остановлен")
