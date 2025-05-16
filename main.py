import asyncio
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import get_api
from keyboards.user import button_order
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.admin import admin
from handlers.kitchen import kitchen
from handlers.user import user

scheduler = AsyncIOScheduler()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))


async def main():
    dp = Dispatcher()
    dp.include_router(user)
    dp.include_router(admin)
    dp.include_router(kitchen)
    scheduler.add_job(check_api, "interval", seconds=5)
    scheduler.start()
    await dp.start_polling(bot)


async def check_api():
    try:
        resp = await get_api('user/finished_orders')
        for dat in resp:
            order_id = dat['id']
            await bot.send_message(
                chat_id=int(dat['user_id']),
                text=f'Ваш заказ №{order_id} готов, вот его содержимое:\n{await get_api(f'user/items_in_order/{order_id}')}\nВаш секретный код(для получения заказа) - <b>{await get_api(f'user/secret_code/{order_id}')}</b>',
                reply_markup=await button_order(order_id), parse_mode='html')
            await get_api(f'user/change_send_to_true/{dat['id']}')
    except Exception as e:
        logging.error(f"API Error: {e}")


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
