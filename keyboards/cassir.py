from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def order_close(order_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Выдать заказ', callback_data=f'kitch_order_close_{order_id}')]
    ])
    return keyboard