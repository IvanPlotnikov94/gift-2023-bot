import types
from aiogram import types


def choose_question_kb(count: str):
    # Клавиатура при выборе загадки
    if count.isdigit():
        choose_question_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for i in range(1, int(count) + 1):
            button = types.KeyboardButton(i)
            choose_question_markup.add(button)

        return choose_question_markup
    else:
        return None


def right_answer_kb():
    # Клавиатура при правильном ответе
    right_answer_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton("Да!")
    no_button = types.KeyboardButton("Нет")
    right_answer_markup.row(yes_button, no_button)
    return right_answer_markup


def try_another_kb():
    # Клавиатура при неправильном ответе. Предложение выбрать другую загадку
    try_another_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton("Да!")
    try_another_markup.add(yes_button)
    return try_another_markup
