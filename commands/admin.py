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

# region Команда "Зарегистрировать загадку"


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
            print(str(ex))  # ToDo: логирование

# endregion


async def show_quests(message: types.Message):
    # Команда "Просмотреть загадки"
    if message.chat.id in ADMIN_ID:
        try:
            questions = await db.questions.find().to_list(None)
            questions_text = [q['question'] for q in questions]
            questions_answer = [q['answer'] for q in questions]
            list_of_questions_and_answers = [
                f"Загадка:\n{q}\nОтвет: {a}" for q, a in zip(questions_text, questions_answer)]

            separator = "====="
            await bot.send_message(message.chat.id, f"\n\n{separator}\n\n".join(list_of_questions_and_answers))

        except Exception as ex:
            print(str(ex))  # ToDo: логирование

# region Команда "Добавить подарок"


async def add_gift(message: types.Message):
    # Команда "Зарегистрировать загадку"
    if message.chat.id in ADMIN_ID:
        await FsmAdmin.set_gift_name.set()
        await message.reply("Введи наименование подарка")


async def set_gift_name(message: types.Message, state=FSMContext):
    # Обработка ввода наименования подарка
    if message.chat.id in ADMIN_ID:
        try:
            async with state.proxy() as gift:
                gift['name'] = message.text
            await FsmAdmin.set_gift_amount.set()
            await message.reply("Введи количество")
        except Exception as ex:
            print(str(ex))  # ToDo: логирование
            await state.finish()
            await bot.send_message(message.chat.id, "Возникла ошибка. Пожалуйста, обратись к разработчику.")


async def set_gift_amount(message: types.Message, state=FSMContext):
    # Обработка ввода имеющегося количества данного подарка
    if message.chat.id in ADMIN_ID:
        try:
            async with state.proxy() as gift:
                gift['amount'] = message.text
            # Добавление подарка в БД
            gift_found = await db.gifts.find_one({"name": gift['name']})
            if not gift_found:
                await db_service.add_gift(db, {"name": gift['name'], "amount": gift['amount'], "user_id": ""})
                await message.reply(f"Готово! Твой подарок: '{gift['name']}' в количестве {gift['amount']} шт. добавлен в базу.")
            else:
                await bot.send_message(message.chat.id, "Этот подарок уже есть в базе! Попробуй добавить подарок с другим наименованием. А если хочешь изменить наименование/количество, воспользуйся отдельной кнопкой в меню.")

            await state.finish()
        except Exception as ex:
            print(str(ex))  # ToDo: логирование
            await state.finish()
            await bot.send_message(message.chat.id, "Возникла ошибка. Пожалуйста, обратись к разработчику.")
# endregion


async def show_gifts(message: types.Message):
    # Команда "Просмотреть подарки"
    if message.chat.id in ADMIN_ID:
        try:
            gifts = await db.gifts.find().to_list(None)
            gift_names = [g['name'] for g in gifts]
            gift_amounts = [g['amount'] for g in gifts]
            list_of_gifts = [
                f"{n}\nКоличество: {a} шт." for n, a in zip(gift_names, gift_amounts)]

            separator = "====="
            await bot.send_message(message.chat.id, f"\n\n{separator}\n\n".join(list_of_gifts))

        except Exception as ex:
            print(str(ex))  # ToDo: логирование
            await bot.send_message(message.chat.id, "Возникла ошибка. Пожалуйста, обратись к разработчику.")


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

    dispatcher.register_message_handler(show_quests, commands=["show_quests"], state=None)

    dispatcher.register_message_handler(add_gift, commands=["add_new_gift"], state=None)
    dispatcher.register_message_handler(set_gift_name, state=FsmAdmin.set_gift_name)
    dispatcher.register_message_handler(set_gift_amount, state=FsmAdmin.set_gift_amount)

    dispatcher.register_message_handler(show_gifts, commands=["show_gifts"], state=None)

    dispatcher.register_message_handler(cancel, state="*", commands="Отмена")
    dispatcher.register_message_handler(cancel, Text(equals="Отмена", ignore_case=True), state="*")
