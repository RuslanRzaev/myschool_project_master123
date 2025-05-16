from aiogram import F, Router
from aiogram.types import CallbackQuery
from custom_filters.admin import KitchenProtect
from keyboards import cassir as cassir_kb
from keyboards import user as user_kb
from utils import *

kitchen = Router()
kitchen.message.filter(KitchenProtect())


@kitchen.callback_query(F.data.startswith('ready_'))
async def send_user_and_officiant(callback: CallbackQuery):
    order_id = callback.data.split('_')[-1]
    await callback.message.delete()
    if await get_api(f'user/ready_order_bool/{order_id}'):
        await get_api(f'kitchen/ready_order/{order_id}')
        await callback.bot.send_message(chat_id=await get_api(f'user/user_id_order/{order_id}'),
                                        text=f'Ваш заказ №{order_id} готов, вот его содержимое:\n{await get_api(f'user/items_in_order/{order_id}')}\nВаш секретный код(для получения заказа) - <b>{await get_api(f'user/secret_code/{order_id}')}</b>', reply_markup=await user_kb.button_order(order_id), parse_mode='html')
        await callback.bot.send_message(chat_id=CASSIR_CHAT, text=f'Заказ № {order_id} готов, вот его содержимое\nt{await get_api(f'user/items_in_order/{order_id}')}\nСекретный код - <b>{await get_api(f'user/secret_code/{order_id}')}</b>', reply_markup=await cassir_kb.order_close(order_id), parse_mode='html')
        await post_api('cashier/new_order/', json={"id": order_id, "items": await get_api(f'user/items_in_order/{order_id}')})
        await callback.answer('')

@kitchen.callback_query(F.data.startswith('kitch_order_close_'))
async def order_close(callback: CallbackQuery):
    order_id = callback.data.split('_')[-1]
    if await get_api(f'user/issued_order_bool/{order_id}'):
        await callback.message.edit_text(f'Заказ № {order_id} готов, вот его содержимое\nt{await get_api(f'user/items_in_order/{order_id}')}\nСекретный код - <b>{await get_api(f'user/secret_code/{order_id}')}</b>\n Выдан', parse_mode='html')
        await get_api(f'kitchen/close_order/{order_id}')
        await callback.answer('')