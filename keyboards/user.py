from utils import get_api
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import get_items_id, orders_user
from custom_filters.admin import ADMINS


async def main(telegram_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Меню', callback_data='menu')],
        [InlineKeyboardButton(text='Заказы', callback_data='user_orders'),
         InlineKeyboardButton(text='Корзина', callback_data='basket')]
    ])
    if telegram_id in ADMINS:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text='Админ', callback_data='root')])
    return keyboard

async def catalog():
    response = await get_api('user/category')
    all_categories = response
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category['name'], callback_data=f'user_category_{category['id']}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='main'))
    return keyboard.adjust(1).as_markup()


async def items(category_id):
    all_items = await get_api(f'user/items/{category_id}')
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item['name'], callback_data=f'user_item_{item['id']}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='menu'))
    return keyboard.adjust(1).as_markup()


async def kb_items(id):
    kb_product = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить в корзину', callback_data=f'add_busket_{id}'),
         InlineKeyboardButton(text='Удалить из коризны', callback_data=f'delete_busket_{id}')],
        [InlineKeyboardButton(text='Назад',
                              callback_data=f'back_basket_{await get_api(f'user/category_id_by_product/{id}')}')]
    ])
    return kb_product


async def kb_items_basket(id):
    kb_product = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить в корзину', callback_data=f'add_busket_{id}'),
         InlineKeyboardButton(text='Удалить из коризны', callback_data=f'delete_busket_{id}')],
        [InlineKeyboardButton(text='Назад', callback_data=f'basket')]
    ])
    return kb_product


async def order_or_more():
    order_or_more = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Перейти к корзине', callback_data='basket'),
         InlineKeyboardButton(text='Перейти в меню', callback_data='menu')]
    ])
    return order_or_more


async def items_id(item_id):
    all_items = await get_items_id(item_id)
    keyboard = InlineKeyboardBuilder()
    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f'basket_user_item_{item.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='main'))
    keyboard.add(InlineKeyboardButton(text='Заказать', callback_data='order'))
    return keyboard.adjust(1).as_markup()


async def main_button():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🏠', callback_data='main')]
    ])
    return keyboard


async def order_user(user_id):
    all_orders = await orders_user(user_id)
    keyboard = InlineKeyboardBuilder()
    for order in all_orders:
        keyboard.add(InlineKeyboardButton(text=order.log_status[-26:-7], callback_data=f'user_orders_{order.id}'))
    keyboard.add(InlineKeyboardButton(text='🏠', callback_data='main'))
    return keyboard.adjust(1).as_markup()


async def back_orders():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='user_orders')]
    ])
    return keyboard
