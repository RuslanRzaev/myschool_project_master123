import os
from datetime import date

from dotenv import load_dotenv
from sqlalchemy import BigInteger, Date, Float, ForeignKey, Integer, Text
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL'),
                             echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    promotion: Mapped[int] = mapped_column(Integer, default=0)


class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    cost_price: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    img: Mapped[int] = mapped_column(Text)


class Basket(Base):
    __tablename__ = 'basket'
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    item: Mapped[int] = mapped_column(ForeignKey('items.id'))
    count: Mapped[int] = mapped_column(Integer)

class Order(Base):
    __tablename__ = 'Order'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    items: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    revenue: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(Text)
    log_status: Mapped[str] = mapped_column(Text)
    secret_code: Mapped[str] = mapped_column(Text)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    day: Mapped[int] = mapped_column(Integer)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
