from aiogram import types
from aiogram.filters import Filter

ADMINS = [905042750]
KITCHEN = (905042750,)


class AdminProtectMessage(Filter):
    def __init__(self):
        self.admins = ADMINS

    async def __call__(self, message: types.Message):
        return message.from_user.id in self.admins


class AdminProtectCallback(Filter):
    def __init__(self):
        self.admins = ADMINS

    async def __call__(self, callback: types.CallbackQuery):
        return callback.from_user.id in self.admins


class KitchenProtect(Filter):
    def __init__(self):
        self.kitchen = KITCHEN

    async def __call__(self, message: types.Message):
        return message.from_user.id in self.kitchen
