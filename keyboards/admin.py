from utils import get_api
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Редактировать меню📝', callback_data='edit_menu')],
    [InlineKeyboardButton(text='Рассылка📬', callback_data='spam'),
     InlineKeyboardButton(text='Заказы📦', callback_data='admin_order')]
])

cancel_add_product_fsm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='add_product_cancel')]
])


async def catalog():
    all_categories = await get_api('user/category')
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category['name'], callback_data=f'category_{category['id']}'))
    keyboard.add(InlineKeyboardButton(text='Добавить категорию✅', callback_data='add_category'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_root'))
    return keyboard.adjust(1).as_markup()


async def items(category_id):
    all_items = await get_api(f'user/items/{category_id}')
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='Добавить товар в данную категорию✅', callback_data=f'add_category_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Редактировать категорию✏️', callback_data=f'edit_category_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад🔙', callback_data='edit_menu'))

    for item in all_items:
        keyboard.add(InlineKeyboardButton(text=item['name'], callback_data=f'item_{item['id']}'))

    return keyboard.adjust(1).as_markup()


async def edit_catalog(category_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Редактировать название✏️', callback_data=f'edit_name_category_{category_id}')],
        [InlineKeyboardButton(text='Удалить категорию❌', callback_data=f'delete_category_{category_id}')],
        [InlineKeyboardButton(text='Назад🔙', callback_data='back_category')]
    ])


async def edit_items(items_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Редактировать название✏️', callback_data=f'edit_name_items_{items_id}'),
         InlineKeyboardButton(text='Редактировать описание✉️', callback_data=f'edit_description_items_{items_id}')],
        [InlineKeyboardButton(text='Редактировать себестоимость', callback_data=f'edit_cost_price_{items_id}'),
        InlineKeyboardButton(text='Редактировать цену🏦', callback_data=f'edit_price_items_{items_id}'),
        InlineKeyboardButton(text='Редактировать изображение', callback_data=f'edit_img_items_{items_id}')],
        [InlineKeyboardButton(text='Удалить товар❌', callback_data=f'delete_items_{items_id}')],
        [InlineKeyboardButton(text='Назад🔙', callback_data='back_category')]
    ])

yes_or_no = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='✅'), KeyboardButton(text='❌')]
])

async def all_orders_func():
    all_orders = await get_api('admin/all_orders')
    keyboard = InlineKeyboardBuilder()
    for order in all_orders:
        keyboard.add(InlineKeyboardButton(text=order['log_status'][-26:-7], callback_data=f'all_orders_{order['id']}'))
    keyboard.add(InlineKeyboardButton(text='🏠', callback_data='back_to_root'))
    return keyboard.adjust(1).as_markup()

async def back_orders():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='admin_order')]
    ])
    return keyboard

async def back_catalogs():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='edit_menu')]
    ])
    return keyboard

async def back_items(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data=f'category_{category_id}')]
    ])
    return keyboard