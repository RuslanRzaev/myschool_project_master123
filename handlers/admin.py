import keyboards.admin as kb_admin
from utils import get_api, post_api, patch_api, delete_api
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, FSInputFile, InputMediaPhoto,
                           Message, ReplyKeyboardRemove)
from custom_filters.admin import AdminProtectMessage, AdminProtectCallback
from FSM.admin import AddCategory, AddProduct, EditCategory, EditProduct, Spam

admin = Router()
admin.message.filter(AdminProtectMessage())
admin.callback_query.filter(AdminProtectCallback())


@admin.callback_query(F.data == 'root')
@admin.callback_query(F.data == 'back_to_root')
async def cmd_start(callback: CallbackQuery):
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html',
                            caption=f'Здравствуйте, {callback.message.from_user.username.title()}\n <b>Краткая статистика</b>:\nКоличество заказов за сутки - {await get_api('admin/count_orders_day')}\nКоличество заказов за календарный месяц - {await get_api('admin/count_orders_month')}\nОборот за сутки - {await get_api('admin/turnover_orders_day')}\nОборот за месяц - {await get_api('admin/turnover_orders_month')}\n Дневная выручка составляет - {await get_api('admin/revenue_orders_day')}\nМесячная выручка - {await get_api('admin/revenue_orders_month')}\nСредний чек за сутки - {await get_api('admin/average_bill_today')}\nСредний чек за месяц - {await get_api('admin/average_bill_month')}')
    await callback.message.edit_media(media=photo,
                                      reply_markup=kb_admin.start_kb)
    await get_api(f'user/login/{callback.from_user.id}')


@admin.callback_query(F.data == 'edit_menu')
async def edit_menu(callback: CallbackQuery, message=None):
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html',
                            caption=f'Выберите нужную вам категорию:⬇️')
    photo.caption = message if message else photo.caption
    await callback.message.edit_media(media=photo, reply_markup=await kb_admin.catalog())


@admin.callback_query(F.data == 'add_category')
async def add_category(callback: CallbackQuery, state: FSMContext):
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html',
                            caption='Введите наименование категории:⬇️')
    await callback.message.edit_media(media=photo,
                                      reply_markup=kb_admin.cancel_add_product_fsm, parse_mode='html')
    await state.set_state(AddCategory.name)


@admin.message(AddCategory.name)
async def reg_category(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await post_api('admin/category', json=data)
    await state.clear()
    await message.answer(text=f'Категория {message.text} была успешно добавлена')
    await message.answer(text='Выберите нужную вам категорию⬇️', reply_markup=await kb_admin.catalog())


@admin.callback_query(F.data == 'add_product_cancel',
                      StateFilter(AddProduct, AddCategory, EditProduct, EditCategory, Spam))
async def cancel_FSM(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('Отмена произошла успешно✅', show_alert=True)
    await cmd_start(callback)


@admin.message(AddProduct.name)
async def reg_name(message: Message, state: FSMContext):
    if isinstance(message.text, str):
        await state.update_data(name=message.text)
        await state.set_state(AddProduct.description)
        await message.answer(
            text='Вам необходимо заполнить следующие данные по порядку:\n<b>Наименование товара✅\nОписание товара❌\nСебестоимость товара❌\nЦена товара❌\nИзображение товара❌</b>\n<b>ВВЕДИТЕ СЕБЕСТОИМОСТЬ ТОВАРА(Для подсчёта выручки):</b>\n',
            reply_markup=kb_admin.cancel_add_product_fsm, parse_mode='html')
    else:
        await message.answer('Наименование должно быть в строковом формате',
                             reply_markup=kb_admin.cancel_add_product_fsm)


@admin.message(AddProduct.description)
async def reg_description(message: Message, state: FSMContext):
    if isinstance(message.text, str):
        await state.update_data(description=message.text)
        await state.set_state(AddProduct.cost_price)
        await message.answer(
            'Вам необходимо заполнить следующие данные по порядку:\n<b>Наименование товара✅\nОписание товара✅\nСебестоимость товара❌\nЦена товара❌\nИзображение товара❌</b>\n<b>ВВЕДИТЕ СЕБЕСТОИМОСТЬ ТОВАРА(Для подсчёта выручки):</b>\n',
            reply_markup=kb_admin.cancel_add_product_fsm, parse_mode='html')
    else:
        await message.answer('Описание должно быть в строковом формате', reply_markup=kb_admin.cancel_add_product_fsm)


@admin.message(AddProduct.cost_price)
async def reg_cost_price(message: Message, state: FSMContext):
    try:
        price_item = int(message.text)
        await state.update_data(cost_price=price_item)
        await state.set_state(AddProduct.price)
        await message.answer(
            'Вам необходимо заполнить следующие данные по порядку:\n<b>Наименование товара✅\nОписание товара✅\nСебестоимость товара✅\nЦена товара❌\nИзображение товара❌</b>\n<b>ВВЕДИТЕ СТОИМОСТЬ ТОВАРА:</b>\n',
            reply_markup=kb_admin.cancel_add_product_fsm, parse_mode='html')
    except ValueError:
        await message.answer('Стоимость должна быть в числовом формате', reply_markup=kb_admin.cancel_add_product_fsm)


@admin.message(AddProduct.price)
async def reg_price(message: Message, state: FSMContext):
    try:
        price_item = int(message.text)
        await state.update_data(price=price_item)
        await state.set_state(AddProduct.img)
        await message.answer(
            'Вам необходимо заполнить следующие данные по порядку:\n<b>Наименование товара✅\nОписание товара✅\nСебестоимость товара✅\nЦена товара✅\nИзображение товара❌</b>\n<b>ОТПРАВЬТЕ ИЗОБРАЖЕНИЕ ТОВАРА:</b>\n',
            reply_markup=kb_admin.cancel_add_product_fsm, parse_mode='html')
    except ValueError:
        await message.answer('Стоимость должна быть в числовом формате', reply_markup=kb_admin.cancel_add_product_fsm)


@admin.message(AddProduct.img, F.photo)
async def reg_img(message: Message, state: FSMContext):
    await state.update_data(img=message.photo[-1].file_id)
    data = await state.get_data()
    await post_api('admin/items', json=data)
    await state.clear()
    await message.answer('Товар успешно добавлен', reply_markup=await kb_admin.back_catalogs())


@admin.message(AddProduct.img)
async def reg_img_not(message: Message):
    await message.answer('Отправьте изображение, а не другие типы данных', reply_markup=kb_admin.cancel_add_product_fsm)


@admin.callback_query(F.data.startswith('category_'))
async def open_catalog(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html',
                            caption=f'Вы выбрали категорию {await get_api(f'user/name_category/{id}')}')
    await callback.message.edit_media(media=photo,
                                      reply_markup=await kb_admin.items(id))


@admin.callback_query(F.data.startswith('add_category_'))
async def create_items(callback: CallbackQuery, state: FSMContext):
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html',
                            caption='Вам необходимо заполнить следующие данные по порядку:\n<b>Наименование товара❌\nОписание товара❌\nСебестоимость товара❌\nЦена товара❌\nИзображение товара❌</b>\n<b>ВВЕДИТЕ НАЗВАНИЕ ТОВАРА:</b>\n')
    await state.set_state(AddProduct.category_id)
    id = callback.data.split('_')[-1]
    await state.update_data(category_id=id)
    await callback.message.edit_media(
        media=photo,
        reply_markup=kb_admin.cancel_add_product_fsm, parse_mode='html')
    await state.set_state(AddProduct.name)


@admin.callback_query(F.data.startswith('item_'))
async def open_item(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'],
                            caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\n Цена: {item['price']} RUB',
                            parse_mode='html')
    await callback.message.edit_media(photo, reply_markup=await kb_admin.edit_items(id))


@admin.callback_query(F.data.startswith('edit_category_'))
async def edit_category(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/name_category/{id}')
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html',
                            caption=f'Что вы хотите сделать с категорией <b>{item}?</b>')
    await callback.message.edit_media(media=photo,
                                      reply_markup=await kb_admin.edit_catalog(id), parse_mode='html')


@admin.callback_query(F.data.startswith('edit_name_category_'))
async def edit_name_category(callback: CallbackQuery, state: FSMContext):
    id = callback.data.split('_')[-1]
    await state.set_state(EditCategory.id)
    await state.update_data(id=id)
    await state.set_state(EditCategory.name)
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html',
                            caption='Введите новое название категории')
    await callback.message.edit_media(media=photo, reply_markup=kb_admin.cancel_add_product_fsm)


@admin.message(EditCategory.name)
async def edit_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await patch_api(f'admin/category/{data['id']}', json={'name': message.text})
    await state.clear()
    await message.answer(f'Категория была успешно изменена')
    await message.answer(text=f'Вы выбрали категорию {await get_api(f'user/name_category/{data["id"]}')}',
                         reply_markup=await kb_admin.items(data["id"]))


@admin.callback_query(F.data.startswith('edit_name_items_'))
async def edit_name_items_(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'], parse_mode='html', caption=f'Введите название товара')
    await state.update_data(id=id)
    await callback.message.edit_media(
        media=photo, reply_markup=kb_admin.cancel_add_product_fsm)
    await state.set_state(EditProduct.name)


@admin.message(EditProduct.name)
async def reg_edit_name_items(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await patch_api(f'admin/items/{data['id']}', json={'name': data['name']})
    await state.clear()
    id = data['id']
    item = await get_api(f'user/item/{id}')
    await message.answer_photo(photo=item['img'],
                               caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\nCебестоимость:\n\t{item['cost_price']}\nЦена: {item['price']} RUB',
                               parse_mode='html', reply_markup=await kb_admin.edit_items(data['id']))


@admin.callback_query(F.data.startswith('edit_description_items_'))
async def edit_description_items_(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'], parse_mode='html', caption=f'Введите описание товара')
    await state.update_data(id=id)
    await callback.message.edit_media(
        media=photo, reply_markup=kb_admin.cancel_add_product_fsm)
    await state.set_state(EditProduct.description)


@admin.message(EditProduct.description)
async def reg_edit_description_items(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await patch_api(f'admin/items/{data['id']}', json={'description': data['description']})
    await state.clear()
    await message.answer('Товар успешно изменён')
    id = data['id']
    item = await get_api(f'user/item/{id}')
    await message.answer_photo(photo=item['img'],
                               caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\nCебестоимость:\n\t{item['cost_price']}\nЦена: {item['price']} RUB',
                               parse_mode='html', reply_markup=await kb_admin.edit_items(data['id']))


@admin.callback_query(F.data.startswith('edit_cost_price_'))
async def edit_count_price_items(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'], parse_mode='html', caption=f'Введите себестоимость товара')
    await state.update_data(id=id)
    await callback.message.edit_media(
        media=photo, reply_markup=kb_admin.cancel_add_product_fsm)
    await state.set_state(EditProduct.cost_price)


@admin.message(EditProduct.cost_price)
async def reg_edit_count_price_items(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(cost_price=message.text)
        data = await state.get_data()
        await patch_api(f'admin/items/{data['id']}', json={'cost_price': data['cost_price']})
        await state.clear()
        await message.answer('Товар успешно изменён')
        id = data['id']
        item = await get_api(f'user/item/{id}')
        await message.answer_photo(photo=item['img'],
                                   caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\nCебестоимость:\n\t{item['cost_price']}\nЦена: {item['price']} RUB',
                                   parse_mode='html', reply_markup=await kb_admin.edit_items(data['id']))
    except ValueError:
        await message.reply('Цена нужна в виде числа')


@admin.callback_query(F.data.startswith('edit_price_items_'))
async def edit_price_items(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'], parse_mode='html', caption=f'Введите цену товара')
    await state.update_data(id=id)
    await callback.message.edit_media(
        media=photo, reply_markup=kb_admin.cancel_add_product_fsm)
    await state.set_state(EditProduct.price)


@admin.message(EditProduct.price)
async def reg_edit_price_items(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        data = await state.get_data()
        await patch_api(f'admin/items/{data['id']}', json={'price': data['price']})
        await state.clear()
        await message.answer('Товар успешно изменён')
        id = data['id']
        item = await get_api(f'user/item/{id}')
        await message.answer_photo(photo=item['img'],
                                   caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\nCебестоимость:\n\t{item['cost_price']}\nЦена: {item['price']} RUB',
                                   parse_mode='html', reply_markup=await kb_admin.edit_items(data['id']))
    except ValueError:
        await message.reply('Цена нужна в виде числа')


@admin.callback_query(F.data.startswith('edit_img_items_'))
async def edit_img_items_(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    id = callback.data.split('_')[-1]
    item = await get_api(f'user/item/{id}')
    photo = InputMediaPhoto(media=item['img'], parse_mode='html', caption=f'Введите изображение товара')
    await state.update_data(id=id)
    await callback.message.edit_media(
        media=photo, reply_markup=kb_admin.cancel_add_product_fsm)
    await state.set_state(EditProduct.img)


@admin.message(EditProduct.img, F.photo)
async def reg_edit_img_items(message: Message, state: FSMContext):
    await state.update_data(img=message.photo[-1].file_id)
    data = await state.get_data()
    await patch_api(f'admin/items/{data['id']}', json={'img': data['img']})
    await state.clear()
    await message.answer('Товар успешно изменён')
    id = data['id']
    item = await get_api(f'user/item/{id}')
    await message.answer_photo(photo=item['img'],
                               caption=f'<b>Название:</b>\n\t{item['name']}\n <b>Описание:</b>\n\t{item['description']}\nCебестоимость:\n\t{item['cost_price']}\nЦена: {item['price']} RUB',
                               parse_mode='html', reply_markup=await kb_admin.edit_items(data['id']))


@admin.message(EditProduct.img, F.photo)
async def error_edit_img(message: Message):
    await message.reply('Отправьте именно фотографию', reply_markup=kb_admin.cancel_add_product_fsm)


@admin.callback_query(F.data == 'spam')
async def spam(callback: CallbackQuery, state: FSMContext):
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html',
                            caption='Введите текст который вы хотите отправить')

    await state.set_state(Spam.text)
    await callback.message.edit_media(media=photo,
                                      reply_markup=kb_admin.cancel_add_product_fsm)
    await callback.answer('')


@admin.message(Spam.text)
async def spam_text(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(text=text)
    await state.set_state(Spam.status)
    await message.answer(f'Вы уверены что хотите отправить всем текст {text}?', parse_mode='html',
                         reply_markup=kb_admin.yes_or_no)


@admin.message(Spam.status)
async def spam_status(message: Message, state: FSMContext):
    if message.text == '✅':
        data = await state.get_data()
        await state.clear()
        for tg_id in await get_api('admin/get_users'):
            await message.bot.send_message(chat_id=tg_id, text=data['text'])
        await message.answer('Текст отправился', reply_markup=ReplyKeyboardRemove())
    else:
        await state.clear()
        await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())


@admin.callback_query(F.data.startswith('delete_items_'))
async def delete_items(callback: CallbackQuery):
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html', caption='Товар успешно удален')
    item_id = callback.data.split('_')[-1]
    category_id = await get_api(f'user/category_id_by_product/{item_id}')
    await delete_api(f'admin/items/{item_id}')
    await callback.message.edit_media(media=photo, reply_markup=await kb_admin.back_items(category_id))


@admin.callback_query(F.data.startswith('delete_category_'))
async def delete_category(callback: CallbackQuery):
    category_id = callback.data.split('_')[-1]
    await delete_api(f'admin/category/{category_id}')
    await edit_menu(callback, 'Категория успешно удалена')


@admin.callback_query(F.data == 'admin_order')
async def order_admin(callback: CallbackQuery):
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html', caption='Все заказы:')
    await callback.message.edit_media(media=photo, reply_markup=await kb_admin.all_orders_func())


@admin.callback_query(F.data.startswith('all_orders_'))
async def open_orders(callback: CallbackQuery):
    order_id = callback.data.split('_')[-1]
    photo = InputMediaPhoto(media=FSInputFile('img/banner_menu.png'), parse_mode='html', caption=f'Номер заказа - {order_id}\nСодержание заказа: {await get_api(f'user/items_in_order/{order_id}')}\nСтатус заказа - {await get_api(f'user/status_order/{order_id}')}\nСекретный код - {await get_api(f'user/secret_code/{order_id}')}\nЦена - {await get_api(f'user/price_order/{order_id}')}\nДата выдачи - {int(await get_api(f'user/day_order/{order_id}')):02}:{int(await get_api(f'user/month_order/{order_id}')):02}:{int(await get_api(f'user/year_order/{order_id}'))}\n ID пользователя - {await get_api(f'user/id_user_order/{order_id}')}')
    await callback.message.edit_media(
        media=photo,
        reply_markup=await kb_admin.back_orders())
