import types
from aiogram import Dispatcher, types
from create_bot import dispatcher, bot
from config import get_admin_ids
from states.user import FsmUser


async def start(message, res=False):
    # Команда start
    if message.chat.id in get_admin_ids():
        await bot.send_message(message.chat.id, "Приветствую, админ! Чего желаешь? Сделаю всё, что в моих силах!")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("1")
        item2 = types.KeyboardButton("2")
        item3 = types.KeyboardButton("3")
        item4 = types.KeyboardButton("4")
        markup.add(item1)
        markup.add(item2)
        markup.add(item3)
        markup.add(item4)
        await bot.send_message(message.chat.id, 'Привет, выбирай загадку!',  reply_markup=markup)


async def help(message, res=False):
    # Команда help
    await bot.send_message(message.chat.id, "Раздел с помощью в разработке, попробуй позже!")


def register_user_commands(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start, commands=["start"])
    dispatcher.register_message_handler(help, commands=["help"])
