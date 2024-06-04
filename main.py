import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import find_dotenv, load_dotenv
import logging
from heandler.user_private import user_private_router

load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
ALLOWED_UPDATE = ['message', 'edited_message']
bot = Bot(token=TOKEN)

dp = Dispatcher()

dp.include_router(user_private_router)

logging.debug("Это сообщение для отладки программы")
logging.info("Информационное сообщение")



def log():
    log= logging.basicConfig(level=logging.DEBUG, filename="py_log.log",filemode="w")

    return log
async def main() -> None:

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATE)

if __name__ == '__main__':
    log()
    try:
        print("Бот запущен")

        asyncio.run(main())# запуск функции в отдельном потоке
        logging.info("Запуск программы")
    except KeyboardInterrupt:
        print("Бот остановлен")
        logging.info("Остановка программы")