from aiogram.dispatcher.filters.state import State, StatesGroup

class FsmUser(StatesGroup):
    choose_question = State()
    write_answer = State()
    finish = State()