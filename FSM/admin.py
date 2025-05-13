from aiogram.fsm.state import State, StatesGroup


class AddCategory(StatesGroup):
    name = State()


class AddProduct(StatesGroup):
    name = State()
    description = State()
    cost_price = State()
    category_id = State()
    price = State()
    img = State()


class EditCategory(StatesGroup):
    id = State()
    name = State()


class EditProduct(StatesGroup):
    id = State()
    name = State()
    description = State()
    cost_price = State()
    price = State()
    img = State()


class Spam(StatesGroup):
    text = State()
    status = State()
