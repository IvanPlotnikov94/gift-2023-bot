from aiogram.dispatcher.filters.state import State, StatesGroup


class FsmAdmin(StatesGroup):
    questions = State()
    set_question = State()
    set_answer = State()
    finish = State()

    gifts = State()
    set_gift_name = State()
    set_gift_amount = State()
