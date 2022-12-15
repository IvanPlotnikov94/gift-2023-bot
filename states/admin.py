from aiogram.dispatcher.filters.state import State, StatesGroup


class FsmAdmin(StatesGroup):
    set_question = State()
    set_answer = State()
    finish = State()

    set_gift_name = State()
    set_gift_amount = State()
