import types
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from create_bot import dispatcher, bot
from config import get_admin_ids
from states.user import FsmUser
from services import db_service, db, logging
from keyboards import admin_kb
from handlers.user import choose_quest

ADMIN_ID = get_admin_ids()


async def start(message, state: FSMContext, res=False):
    try:
        logging.info(
            f"Пользователь id: {message.chat.id}; username: {message.chat.username}; first_name: {message.chat.last_name} запустил команду /start.")
        user = await db.users.find_one({"_id": message.chat.id})
        logging.debug(
            f"{user}")
        if not user:
            logging.info("Пользователь в БД не найден. Добавляем...")
            await db_service.add_user(db, message.chat)
            logging.info("Пользователь в БД добавлен.")

        # Команда start
        if message.chat.id in get_admin_ids():
            await bot.send_message(message.chat.id, "Приветствую, админ! Чего желаешь?", reply_markup=admin_kb.get_admin_main_menu())
        else:
            # Проверка пользователя на повторное участие
            hasWon = await db_service.check_if_user_already_won(db, message.chat.id)
            logging.info(f"hasWon: {hasWon}")
            if (not hasWon):
                await bot.send_message(message.chat.id, 'Доброго времени суток! Я - помощник Насти, и я помогу Вам получить подарок и хорошее настроение! ☺️ Нужно лишь отгадать загадку. Ну что, поехали! 💃')
                await choose_quest(message)
            else:
                await bot.send_message(message.chat.id, 'Вижу, Вы уже поучаствовали в розыгрыше! Давайте дадим шанс другим клиентам 😉', reply_markup=ReplyKeyboardRemove())
    except Exception as ex:
        logging.exception(Exception)
        await state.finish()
        await bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, обратитесь к администратору.", reply_markup=ReplyKeyboardRemove())


async def help(message, res=False):
    # Команда help
    await bot.send_message(message.chat.id, f"За помощью можно обратиться к:\nАдминистратор - Анастасия @shellacnastya\nРазработчик - Иван @Shad0w_Spark")


def register_user_commands(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start, commands=["start"], state=None)
    dispatcher.register_message_handler(help, commands=["help"])
