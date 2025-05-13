import random

from utils import get_api
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message
from database import requests as rq
from keyboards import kitchen as kitchen_kb
from keyboards import user as user_kb
from utils import KITCHEN_CHAT

user = Router()


@user.message(Command('start'))
async def cmd_start(message: Message) -> None:
    photo = FSInputFile('img/banner.webp')
    await message.answer_photo(photo=photo,
                               caption=f"Здравствуйте {message.from_user.first_name.title()}!\nВы попали в ресторан 'Волга' — <b>место, где рыба на тарелке свежее, чем утро на берегу реки</b>.\nЧем порадуем сегодня?",
                               parse_mode='html', reply_markup=await user_kb.main(message.from_user.id))
    await rq.set_user(message.from_user.id)

@user.callback_query(F.data == 'menu')
async def cmd_menu(callback: CallbackQuery) -> None:
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), caption='Выберите категорию товара')
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.catalog())


@user.callback_query(F.data.startswith('user_category_'))
async def open_catalog(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), caption=f'Вы выбрали категорию {await get_api(f'user/name_category/{id}')}')
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.items(id))


@user.callback_query(F.data.startswith('user_item_'))
async def open_item(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'],
                            caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\n <b>Цена</b>:\n {item['price']} RUB',
                            parse_mode='html')
    await callback.message.edit_media(photo, reply_markup=await user_kb.kb_items(id))


@user.callback_query(F.data.startswith('add_busket_'))
async def add_busket(callback: CallbackQuery):
    item_id = callback.data.split('_')[-1]
    await rq.add_busket(callback.from_user.id, item_id)
    await callback.answer(
        f'Товар успешно добавлен в корзину, количество штук в корзине - {await rq.is_item_in_basket(callback.from_user.id, item_id)}')


@user.callback_query(F.data.startswith('delete_busket_'))
async def delete_busket(callback: CallbackQuery):
    item_id = callback.data.split('_')[-1]
    await rq.delete_busket(callback.from_user.id, item_id)
    await callback.answer(
        f'Товар успешно удален из корзины, количество штук в корзине - {await rq.is_item_in_basket(callback.from_user.id, item_id)}')


@user.callback_query(F.data.startswith('back_basket_'))
async def open_catalog(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'),
                            caption=f'Вы выбрали категорию {await rq.get_name_category(id)}')
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.items(id))


@user.callback_query(F.data == 'main')
async def cmd_start(callback: CallbackQuery) -> None:
    photo = InputMediaPhoto(media=FSInputFile('img/banner.webp'),
                            caption=f"Здравствуйте {callback.message.from_user.first_name.title()}!\nВы попали в ресторан 'Волга' — <b>место, где рыба на тарелке свежее, чем утро на берегу реки</b>.\nЧем порадуем сегодня?",
                            parse_mode='html')
    await callback.message.edit_media(media=photo, reply_markup=user_kb.main)
    await callback.answer('')


@user.callback_query(F.data == 'basket')
async def mybasket(callback: CallbackQuery):
    my_items = await rq.get_my_basket(callback.from_user.id)
    items_data = []
    items_id = []
    for myitem in my_items:
        item = await rq.get_item(myitem.item)
        items_data.append([item.name, item.price * myitem.count, myitem.count])
        items_id.append(item.id)

    items = []
    total_price = 0
    for data in items_data:
        name, price, count = data
        items.append(f"{name}: {price} ({count} шт) RUB")
        total_price += price

    items.append(f"\nОбщая сумма: {total_price} RUB")
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), caption='\n'.join(items))
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.items_id(items_id))
    await callback.answer('')


@user.callback_query(F.data.startswith('basket_user_item_'))
async def open_item(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    item = await rq.get_item(id)
    photo = InputMediaPhoto(media=item.img,
                            caption=f'<b>Название:</b>\n\t{item.name}\n <b>Описание:</b>\n\t{item.description}\n <b>Цена</b>:\n {item.price} RUB',
                            parse_mode='html')
    await callback.message.edit_media(photo, reply_markup=await user_kb.kb_items_basket(id))


@user.callback_query(F.data.startswith('order'))
async def order(callback: CallbackQuery):
    my_items = await rq.get_my_basket(callback.from_user.id)
    items_data = []
    items_id = []
    for myitem in my_items:
        item = await rq.get_item(myitem.item)
        items_data.append([item.name, item.price * myitem.count, myitem.count, item.cost_price])
        items_id.append(item.id)

    items = []
    total_price = 0
    total_revenue = 0
    for data in items_data:
        name, price, count, cost_price = data
        items.append(f"{name}: ({count} шт)")
        total_revenue += price - (count * cost_price)
        total_price += price
    if items_data:
        await rq.add_order(callback.from_user.id, '\n'.join(items), total_price, total_revenue)
        order = await rq.get_my_order(callback.from_user.id)
        await callback.bot.send_message(chat_id=KITCHEN_CHAT, text='\n'.join(items) + f'\n#Заказ{order.id}',
                                        reply_markup=await kitchen_kb.ready_order(order.id))
        await rq.clear_basket(callback.from_user.id)
        await callback.message.answer('Ваш заказ уже готовится⌛\n Скоро вам придёт уведомление о готовности заказа',
                                      reply_markup=await user_kb.main_button())
        await callback.answer('')
    else:
        await callback.answer('Корзина пуста!', show_alert=True)



@user.callback_query(F.data == 'user_orders')
async def orders_user(callback: CallbackQuery):
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), caption='Вот ваши заказы:')
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.order_user(callback.from_user.id))
    await callback.answer('')

@user.callback_query(F.data.startswith('user_orders_'))
async def open_order(callback: CallbackQuery):
    order_id = callback.data.split('_')[-1]
    await callback.message.edit_text(text=f'Номер заказа - {order_id}\nСодержание заказа: {await rq.items_in_order(order_id)}\nСтатус заказа - {await rq.status_order(order_id)}\nСекретный код - {await rq.secret_code(order_id)}\nЦена - {await rq.price_order(order_id)}\nДата выдачи - {int(await rq.day_order(order_id)):02}:{int(await rq.month_order(order_id)):02}:{int(await rq.year_order(order_id))}', reply_markup=await user_kb.back_orders())
