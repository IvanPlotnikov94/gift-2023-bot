import types
from weakref import proxy
from aiogram import Dispatcher, types
from create_bot import dispatcher, bot
from aiogram.dispatcher import FSMContext
from states.admin import FsmAdmin
from config import get_admin_ids
from aiogram.dispatcher.filters import Text
from services import db_service, db

ADMIN_ID = get_admin_ids()


async def register_new_quest(message: types.Message):
    # Команда "Зарегистрировать загадку"
    if message.chat.id in ADMIN_ID:
        await FsmAdmin.set_question.set()
        await message.reply("Введи текст загадки")


async def register_new_answer(message: types.Message, state=FSMContext):
    # Обработка ввода загадки
    if message.chat.id in ADMIN_ID:
        async with state.proxy() as quest:
            quest['text'] = message.text
        await FsmAdmin.set_answer.set()
        await message.reply("Теперь введи ответ на неё")


async def finish_register(message: types.Message, state=FSMContext):
    # Обработка ввода ответа на загадку
    if message.chat.id in ADMIN_ID:
        try:
            async with state.proxy() as quest:
                quest['answer'] = message.text

                # Добавление загадки с ответом в БД
                question_found = await db.questions.find_one({"question": quest['text']})
                if not question_found:
                    await db_service.add_question(db, quest['text'], quest['answer'])
                    await message.reply(f"Отлично, загадка зарегистрирована! Твоя загадка: {quest['text']}")
                else:
                    await bot.send_message(message.chat.id, "Упс, эта загадка уже существует! Попробуй зарегистрировать другую загадку.")

            await state.finish()  # Выход из машины состояний, очищение хранилища
        except Exception as ex:
            print(str(ex))


async def cancel(message: types.Message, state: FSMContext):
    # Handler выхода из конечного автомата
    if message.chat.id in ADMIN_ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply("Вышел из машины состояний")


def register_admin_commands(dispatcher: Dispatcher):
    dispatcher.register_message_handler(register_new_quest, commands=["register_new_quest"], state=None)
    dispatcher.register_message_handler(register_new_answer, state=FsmAdmin.set_question)
    dispatcher.register_message_handler(finish_register, state=FsmAdmin.set_answer)
    dispatcher.register_message_handler(cancel, state="*", commands="Отмена")
    dispatcher.register_message_handler(cancel, Text(equals="Отмена", ignore_case=True), state="*")
