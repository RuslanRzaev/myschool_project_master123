from utils import get_api, post_api, delete_api
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message, BufferedInputFile
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
    await post_api(f'user/login',
                   json={'telegram_id': str(message.from_user.id), 'first_name': str(message.from_user.first_name)})


@user.callback_query(F.data == 'menu')
async def cmd_menu(callback: CallbackQuery) -> None:
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), caption='Выберите категорию товара')
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.catalog())


@user.callback_query(F.data.startswith('user_category_'))
async def open_catalog(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'),
                            caption=f'Вы выбрали категорию {await get_api(f'user/name_category/{id}')}')
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.items(id))


@user.callback_query(F.data.startswith('user_item_'))
async def open_item(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'],
                            caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\n <b>Цена</b>:\n {item['price']} RUB',
                            parse_mode='html')
    await callback.message.edit_media(photo, reply_markup=await user_kb.kb_items(id))


@user.callback_query(F.data.startswith('add_bucket_'))
async def add_bucket(callback: CallbackQuery):
    item_id = callback.data.split('_')[-1]
    await get_api(f'user/add_bucket/{callback.from_user.id}/{item_id}')
    await callback.answer(
        f'Товар успешно добавлен в корзину, количество штук в корзине - {await get_api(f'user/is_item_in_basket/{callback.from_user.id}/{item_id}')}')


@user.callback_query(F.data.startswith('delete_bucket_'))
async def delete_bucket(callback: CallbackQuery):
    item_id = callback.data.split('_')[-1]
    await get_api(f'user/delete_bucket/{callback.from_user.id}/{item_id}')
    await callback.answer(
        f'Товар успешно удален из корзины, количество штук в корзине - {await get_api(f'user/is_item_in_basket/{callback.from_user.id}/{item_id}')}')


@user.callback_query(F.data.startswith('back_basket_'))
async def open_catalog(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'),
                            caption=f'Вы выбрали категорию {await get_api(f'user/name_category/{id}')}')
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.items(id))


@user.callback_query(F.data == 'main')
async def cmd_start(callback: CallbackQuery) -> None:
    photo = InputMediaPhoto(media=FSInputFile('img/banner.webp'),
                            caption=f"Здравствуйте {callback.message.from_user.first_name.title()}!\nВы попали в ресторан 'Волга' — <b>место, где рыба на тарелке свежее, чем утро на берегу реки</b>.\nЧем порадуем сегодня?",
                            parse_mode='html')
    await callback.message.edit_media(media=photo, reply_markup=await user_kb.main(callback.from_user.id))
    await callback.answer('')


@user.callback_query(F.data == 'basket')
async def mybasket(callback: CallbackQuery):
    my_items = await get_api(f'user/bucket/{callback.from_user.id}')
    items_data = []
    items_id = []
    for myitem in my_items:
        item = await get_api(f'user/item/{myitem['item']}')
        items_data.append([item['name'], item['price'] * myitem['count'], myitem['count']])
        items_id.append(item['id'])

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
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'],
                            caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\n <b>Цена</b>:\n {item['price']} RUB',
                            parse_mode='html')
    await callback.message.edit_media(photo, reply_markup=await user_kb.kb_items_basket(id))


@user.callback_query(F.data.startswith('qr_code_'))
async def qr_code(callback: CallbackQuery):
    order_id = callback.data.split('_')[-1]
    response = await get_api(f'user/order_qr_code/{order_id}', need_json=False)
    photo_bytes = response.read()
    await callback.message.answer_photo(photo=BufferedInputFile(file=photo_bytes, filename='123'),
                                        reply_markup=await user_kb.main_button(), caption=f'Заказ №{order_id}')
    await callback.answer('')


@user.callback_query(F.data.startswith('order'))
async def order(callback: CallbackQuery):
    my_items = await get_api(f'user/bucket/{callback.from_user.id}')
    items_data = []
    items_id = []
    for myitem in my_items:
        item = await get_api(f'user/item/{myitem['item']}')
        items_data.append([item['name'], item['price'] * myitem['count'], myitem['count'], item['cost_price']])
        items_id.append(item['id'])

    items = []
    total_price = 0
    total_revenue = 0
    for data in items_data:
        name, price, count, cost_price = data
        items.append(f"{name}: ({count} шт)")
        total_revenue += price - (count * cost_price)
        total_price += price
    if items_data:
        await post_api('user/order', json={'telegram_id': callback.from_user.id, 'items': '\n'.join(items),
                                           'total_price': total_price, 'total_revenue': total_revenue})
        order = await get_api(f'user/order/{callback.from_user.id}')
        await callback.bot.send_message(chat_id=KITCHEN_CHAT, text='\n'.join(items) + f'\n#Заказ{order['id']}',
                                        reply_markup=await kitchen_kb.ready_order(order['id']))
        await delete_api(f'user/order/{callback.from_user.id}')
        await post_api('kitchen/new_order/',
                       json={"id": order['id'], "items": await get_api(f'user/items_in_order/{order['id']}')})
        print(order['id'])
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
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'),
                            caption=f'Номер заказа - {order_id}\nСодержание заказа: {await get_api(f'user/items_in_order/{order_id}')}\nСтатус заказа - {await get_api(f'user/status_order/{order_id}')}\nСекретный код - {await get_api(f'user/secret_code/{order_id}')}\nЦена - {await get_api(f'user/price_order/{order_id}')}\nДата выдачи - {int(await get_api(f'user/day_order/{order_id}')):02}:{int(await get_api(f'user/month_order/{order_id}')):02}:{int(await get_api(f'user/year_order/{order_id}'))}')
    await callback.message.edit_media(
        media=photo,
        reply_markup=await user_kb.back_orders(order_id))
