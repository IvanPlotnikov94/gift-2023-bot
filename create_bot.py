from aiogram import Bot, Dispatcher
from config import get_token

bot = Bot(get_token())
dispatcher = Dispatcher(bot)