import types
from aiogram import Dispatcher, types


def get_admin_main_menu():
    # Возвращает главное меню админа
    admin_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_questions = types.KeyboardButton(text="Загадки")
    button_gifts = types.KeyboardButton(text="Подарки")
    admin_menu.row(button_questions, button_gifts)
    return admin_menu


def get_questions_menu():
    # Подменю "Загадки"
    questions_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_new_question = types.KeyboardButton(text="Зарегистрировать загадку")
    button_show_questions = types.KeyboardButton(text="Просмотреть загадки")
    button_back = types.KeyboardButton(text="Назад")
    questions_menu.row(button_new_question, button_show_questions)
    questions_menu.add(button_back)
    return questions_menu


def get_gifts_menu():
    # Подменю "Подарки"
    gifts_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_new_gift = types.KeyboardButton(text="Добавить подарок")
    button_show_gifts = types.KeyboardButton(text="Просмотреть пул подарков")
    button_back = types.KeyboardButton(text="Назад")
    gifts_menu.row(button_new_gift, button_show_gifts)
    gifts_menu.add(button_back)
    return gifts_menu


def back_to_menu():
    # Кнопка "В главное меню"
    back_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton(text="В главное меню")
    back_menu.add(button_back)
    return back_menu
