from aiogram.fsm.state import StatesGroup, State


class UserFactory(StatesGroup):
    fio = State()
    promo_code = State()
    top_up_balance = State()


class BidFactory(StatesGroup):
    author = State()
    content = State()


