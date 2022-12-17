from aiogram.dispatcher.filters.state import State, StatesGroup


class FsmUser(StatesGroup):
    choose_question = State()
    write_answer = State()
    get_prize = State()

    try_another = State()
