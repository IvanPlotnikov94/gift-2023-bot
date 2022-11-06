from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import get_token

storage = MemoryStorage()

bot = Bot(get_token())
dispatcher = Dispatcher(bot, storage=storage)
