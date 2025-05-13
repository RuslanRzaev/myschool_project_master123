import random
import string
from datetime import datetime

from database.models import Basket, Category, Item, Order, User, async_session
from pydantic import with_config
from sqlalchemy import select


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_users():
    async with async_session() as session:
        users = await session.scalars(select(User.tg_id))
        users = users.all()
        return users


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def add_category(data):
    async with async_session() as session:
        session.add(Category(name=data['name']))
        await session.commit()


async def get_name_category(category_id):
    async with async_session() as session:
        result = await session.scalars(select(Category.name).where(Category.id == category_id))
        return result.one_or_none()


async def get_items(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == category_id))


async def get_items_id(ids):
    async with async_session() as session:
        query = select(Item).where(Item.id.in_(ids))
        result = await session.execute(query)
        return result.scalars().all()


async def add_items(data):
    async with async_session() as session:
        item = Item(
            name=data['name'],
            description=data['description'],
            cost_price=data['cost_price'],
            price=data['price'],
            category=data['category_id'],
            img=data['img']
        )
        session.add(item)
        await session.commit()


async def get_item(id):
    async with async_session() as session:
        item = await session.execute(select(Item).where(Item.id == id))
        return item.scalar_one_or_none()


async def edit_category(id, name):
    async with async_session() as session:
        query = select(Category).where(Category.id == id)
        result = await session.execute(query)
        category = result.scalar_one_or_none()
        category.name = name
        await session.commit()


async def edit_items(id, col, row):
    async with async_session() as session:
        query = select(Item).where(Item.id == id)
        result = await session.execute(query)
        item = result.scalar_one_or_none()
        setattr(item, col, row)
        await session.commit()


async def delete_category(id):
    async with async_session() as session:
        query = select(Category).where(Category.id == id)
        result = await session.execute(query)
        category = result.scalar_one_or_none()
        await session.delete(category)
        await session.commit()

async def delete_items(id):
    async with async_session() as session:
        query = select(Item).where(Item.id == id)
        result = await session.execute(query)
        item = result.scalar_one_or_none()
        await session.delete(item)
        await session.commit()


async def is_item_in_basket(user_id, item_id):
    async with async_session() as session:
        test = select(Basket).where(Basket.user == user_id, Basket.item == item_id)
        result = await session.execute(test)
        test = result.scalars().first()
        if test:
            return test.count
        return 0


async def add_busket(user_id, item_id):
    async with async_session() as session:
        test = select(Basket).where(Basket.user == user_id, Basket.item == item_id)
        result = await session.execute(test)
        test = result.scalars().first()
        if test:
            test.count += 1
        else:
            basket = Basket(
                user=user_id,
                item=item_id,
                count=1
            )
            session.add(basket)
        await session.commit()


async def delete_busket(user_id, item_id):
    async with async_session() as session:
        query = select(Basket).where(Basket.user == user_id, Basket.item == item_id)
        result = await session.execute(query)
        basket = result.scalars().first()
        if not basket:
            return
        if basket.count == 1:
            await session.delete(basket)
        else:
            basket.count -= 1
        await session.commit()


async def get_my_basket(tg_id):
    async with async_session() as session:
        basket_items = await session.scalars(select(Basket).where(Basket.user == tg_id))
        return basket_items


async def add_order(user_id, items, price, revenue):
    async with async_session() as session:
        datatime = datetime.now()
        order = Order(
            user_id=user_id,
            items=items,
            status='Готовится⌛',
            log_status='Готовится⌛' + str(datatime),
            secret_code=str(random.randint(1000, 10000)) + ''.join(random.choices(string.ascii_lowercase, k=3)),
            price=price,
            revenue=revenue,
            year=(str(datatime).split())[0].split('-')[0],
            month=(str(datatime).split())[0].split('-')[1],
            day=(str(datatime).split())[0].split('-')[2]
        )
        session.add(order)
        await session.commit()


async def get_my_order(user_id):
    async with async_session() as session:
        query = select(Order).where(Order.user_id == user_id).order_by(Order.id.desc()).limit(1)
        result = await session.execute(query)
        return result.scalars().first()


async def clear_basket(user_id):
    async with async_session() as session:
        query = select(Basket).where(Basket.user == user_id)
        result = await session.execute(query)
        basket = result.scalars().first()
        await session.delete(basket)
        await session.commit()


async def ready_order(order_id):
    async with async_session() as session:
        query = select(Order).where(Order.id == order_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        order.status = 'Готов✅'
        order.log_status += '\nГотов✅' + str(datetime.now())
        await session.commit()


async def close_order(order_id):
    async with async_session() as session:
        query = select(Order).where(Order.id == order_id)
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        order.status = 'Выдан🟨'
        order.log_status += '\nВыдан🟨' + str(datetime.now())
        await session.commit()


async def user_id_order(order_id) -> int:
    async with async_session() as session:
        user = await session.scalars(select(Order.user_id).where(Order.id == order_id))
        user_id = user.all()
        return int(''.join(str(i) for i in user_id))


async def secret_code(order_id) -> str:
    async with async_session() as session:
        order = await session.scalars(select(Order.secret_code).where(Order.id == order_id))
        order = order.all()
        return ''.join(order)


async def items_in_order(order_id) -> str:
    async with async_session() as session:
        order = await session.scalars(select(Order.items).where(Order.id == order_id))
        order = order.all()
        return ''.join(order)


async def status_order(order_id) -> str:
    async with async_session() as session:
        order = await session.scalars(select(Order.status).where(Order.id == order_id))
        order = order.all()
        return ''.join(order)


async def orders_user(user_id):
    async with async_session() as session:
        return await session.scalars(select(Order).where(Order.user_id == user_id))

async def all_orders_rq():
    async with async_session() as session:
        return await session.scalars(select(Order))


async def price_order(order_id) -> float:
    async with async_session() as session:
        order = await session.scalars(select(Order.price).where(Order.id == order_id))
        order = order.all()
        return float(''.join(str(i) for i in order))


async def year_order(order_id) -> float:
    async with async_session() as session:
        order = await session.scalars(select(Order.year).where(Order.id == order_id))
        order = order.all()
        return float(''.join(str(i) for i in order))


async def month_order(order_id) -> float:
    async with async_session() as session:
        order = await session.scalars(select(Order.month).where(Order.id == order_id))
        order = order.all()
        return float(''.join(str(i) for i in order))

async def id_user_order(order_id) -> int:
    async with async_session() as session:
        order = await session.scalars(select(Order.user_id).where(Order.id == order_id))
        order = order.all()
        return int(''.join(str(i) for i in order))


async def day_order(order_id) -> str:
    async with async_session() as session:
        order = await session.scalars(select(Order.day).where(Order.id == order_id))
        order = order.all()
        return float(''.join(str(i) for i in order))


async def count_orders_day():
    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.day == datetime.today().day, Order.year == datetime.today().year))
        orders = result.scalars().all()
        return len(orders)


async def count_orders_month():
    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.month == datetime.today().month, Order.year == datetime.today().year))
        orders = result.scalars().all()
        return len(orders)


async def revenue_orders_day():
    async with async_session() as session:
        result = await session.execute(
            select(Order.revenue).where(Order.day == datetime.today().day, Order.year == datetime.today().year))
        orders = result.scalars().all()
        return sum(orders)


async def revenue_orders_month():
    async with async_session() as session:
        result = await session.execute(
            select(Order.revenue).where(Order.month == datetime.today().month, Order.year == datetime.today().year))
        orders = result.scalars().all()
        return sum(orders)


async def turnover_orders_day():
    async with async_session() as session:
        result = await session.execute(
            select(Order.price).where(Order.day == datetime.today().day, Order.year == datetime.today().year))
        orders = result.scalars().all()
        return sum(orders)


async def turnover_orders_month():
    async with async_session() as session:
        result = await session.execute(
            select(Order.price).where(Order.month == datetime.today().month, Order.year == datetime.today().year))
        orders = result.scalars().all()
        return sum(orders)

async def get_category_id_by_product(item_id):
    async with async_session() as session:
        result = await session.execute(
            select(Item.category).where(Item.id == item_id)
        )
        category_id = result.scalar()

        return category_id
