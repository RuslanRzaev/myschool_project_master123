import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from database.models import async_main
from dotenv import load_dotenv
from handlers.admin import admin
from handlers.kitchen import kitchen
from handlers.user import user


async def main():
    load_dotenv()

    await async_main()

    bot = Bot(os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(user)
    dp.include_router(admin)
    dp.include_router(kitchen)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')