from aiogram import types
from aiogram.filters import Filter
from utils import get_api


class AdminProtectMessage(Filter):

    async def __call__(self, message: types.Message):
        return get_api(f'user/check_admin/{message.from_user.id}')


class AdminProtectCallback(Filter):

    async def __call__(self, callback: types.CallbackQuery):
        return get_api(f'user/check_admin/{callback.from_user.id}')


class KitchenProtect(Filter):

    async def __call__(self, message: types.Message):
        return get_api(f'user/check_kitchen/{message.from_user.id}')
