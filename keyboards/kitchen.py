from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def ready_order(order_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅', callback_data=f'ready_{order_id}')]
    ])
    return keyboard
