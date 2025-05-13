from aiogram import F, Router
from aiogram.types import CallbackQuery
from custom_filters.admin import KitchenProtect
from database import requests as rq
from keyboards import cassir as cassir_kb
from keyboards import kitchen as kitchen_kb
from keyboards import user as user_kb
from utils import *

kitchen = Router()
kitchen.message.filter(KitchenProtect())


@kitchen.callback_query(F.data.startswith('ready_'))
async def send_user_and_officiant(callback: CallbackQuery):
    order_id = callback.data.split('_')[-1]
    await callback.message.reply('Заказ готов')
    await rq.ready_order(order_id)
    await callback.bot.send_message(chat_id=await rq.user_id_order(order_id),
                                    text=f'Ваш заказ №{order_id} готов, вот его содержимое:\n{await rq.items_in_order(order_id)}\nВаш секретный код(для получения заказа) - <b>{await rq.secret_code(order_id)}</b>', reply_markup=await user_kb.main_button(), parse_mode='html')
    await callback.bot.send_message(chat_id=CASSIR_CHAT, text=f'Заказ № {order_id} готов, вот его содержимое\nt{await rq.items_in_order(order_id)}\nСекретный код - <b>{await rq.secret_code(order_id)}</b>', reply_markup=await cassir_kb.order_close(order_id), parse_mode='html')
    await callback.answer('')

@kitchen.callback_query(F.data.startswith('kitch_order_close_'))
async def order_close(callback: CallbackQuery):
    order_id = callback.data.split('_')[-1]
    await callback.message.reply('Заказ выдан')
    await rq.close_order(order_id)
    await callback.answer('')