import random
import types
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from create_bot import dispatcher, bot
from config import get_admin_ids
from states.user import FsmUser
from services import db_service, db, logging
from keyboards import user_kb

ADMIN_ID = get_admin_ids()


async def choose_question(message: types.Message, state=FSMContext):
    if message.chat.id not in ADMIN_ID:
        try:
            logging.debug(f"Метод choose_question(). message.text: {message.text}")
            questions = await db_service.get_available_questions(db, message.chat.id)
            questions_text = [q['question'] for q in questions]
            questions_answer = [a['answer'] for a in questions]
            logging.debug(
                f"available questions: {questions}\nquestions_text: {questions_text}\nquestions_answer: {questions_answer}")

            if message.text.isdigit() and int(message.text) > 0 and int(message.text) <= len(questions_text):
                logging.debug(
                    f"message.text.isdigit(): {message.text.isdigit()}\nint(message.text): {int(message.text)}\nlen(questions_text): {len(questions_text)}")
                async with state.proxy() as quest:
                    quest['id'] = questions[int(message.text) - 1]['_id']
                    quest['question'] = questions_text[int(message.text) - 1]
                    quest['answer'] = questions_answer[int(message.text) - 1]
                # Отметка в БД, что пользователь получил этот вопрос
                logging.debug(str(quest))
                await db_service.update_question(db, quest['id'], message.chat.id)
                # Отправка вопроса пользователю
                await FsmUser.write_answer.set()
                await bot.send_message(message.chat.id, quest['question'], reply_markup=ReplyKeyboardRemove())
            else:
                questions = await db_service.get_available_questions(db, message.chat.id)
                markup = user_kb.choose_question_kb(str(len(questions)))
                await message.reply("Пожалуйста, воспользуйтесь кнопками для выбора загадки!", reply_markup=markup)
        except Exception as ex:
            logging.exception(Exception)
            await state.finish()
            await bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, обратитесь к администратору.", reply_markup=ReplyKeyboardRemove())
        # Поиск выбранной загадки по message.text
        # Сначала считать все загадки, составить список из questions.number, затем проверить
        # принадлежность message.text этому списку. Если да, то выдаем текст выбранной загадки.
        # chosen_question = db.questions.findOne({"number":{message.text}}) #Проверить, мб надо f-строку
        # Можно еще сохранять в proxy (локал.хранилище) ответ сразу, чтобы не лезть в БД
        # async with state.proxy() as quest:
            # quest['question'] = chosen_question["text"] #text - имя поля в коллекции (может поменяю позже)
            # quest['answer'] = chosen_question["answer"] # тут будет массив правильных ответов!
            # await FsmUser.write_answer.set()
            # await message.reply(f"Текст выбранной загадки: {chosen_question["text"]}. Тщательно подумай и напиши свой ответ!")


async def write_answer(message: types.Message, state=FSMContext):
    # Проверка введенного ответа
    if message.chat.id not in ADMIN_ID:
        try:
            logging.debug(f"Метод write_answer(). message.text: {message.text}")
            async with state.proxy() as quest:
                # Проверка по массиву правильных ответов
                # if (message.text.lower() in [item.lower() for item in quest['answer']]):
                if (message.text.lower() == quest['answer'].lower()):
                    # Ответ правильный! Протестить работу lower() для всех элементов массива
                    await message.reply("Верно! 👏 У меня для Вас есть подарок, готовы получить? 🎁", reply_markup=user_kb.right_answer_kb())
                    await FsmUser.get_prize.set()
                else:
                    await FsmUser.try_another.set()
                    await message.reply("Это неправильный ответ! Хотите попробовать другую загадку?", reply_markup=user_kb.try_another_kb())
        except Exception as ex:
            logging.exception(Exception)
            await state.finish()
            await bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, обратитесь к администратору.", reply_markup=ReplyKeyboardRemove())


async def try_another(message: types.Message, state=FSMContext):
    # Обработчик повторной попытки
    if message.chat.id not in ADMIN_ID:
        try:
            logging.debug(f"Метод try_another(). message.text: {message.text}")
            await FsmUser.choose_question.set()
            await choose_quest(message)
        except Exception as ex:
            logging.exception(Exception)
            await state.finish()
            await bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, обратитесь к администратору.", reply_markup=ReplyKeyboardRemove())


async def get_prize(message: types.Message, state=FSMContext):
    # Ответ верный; запрос согласия на получение подарка
    try:
        logging.debug(f"Метод get_prize(). message.text: {message.text}")
        if (message.text.lower() in ["да", "да!"]):
            prize = await get_random_gift()

            if (prize is not None):
                # Уменьшаем в БД количество оставшихся подарков на 1
                await db_service.subtract_gift_amount(db, prize)
                await bot.send_photo(message.chat.id, prize['photo_id'], f"Поздравляю, Вы выиграли {prize['name']}\nС наступающим Новым Годом!\nУвидимся в Новом Году на ноготочках 😉", reply_markup=ReplyKeyboardRemove())
            else:
                await bot.send_message(message.chat.id, f"Поздравляю, Вы выиграли подарок! 🎁\n А какой именно - уточните у Насти, пожалуйста, потому что у меня произошел непредвиденный сбой 😅\nС наступающим Новым Годом!\nУвидимся в Новом Году на ноготочках 😉", reply_markup=ReplyKeyboardRemove())
            # Перед завершением работы производим отметку в БД о том, что пользователь выиграл подарок
            await db_service.update_user_has_won(db, message.chat.id)
            await state.finish()
        elif (message.text.lower() in ["нет", "нет!"]):
            await bot.send_message(message.chat.id, 'Серьезно? Не верю! Кто отказывается от подарка? 😅 Попробуйте еще раз!')
            await bot.send_message(message.chat.id, "У меня для Вас есть подарок, готовы получить? 🎁", reply_markup=user_kb.right_answer_kb())
        else:
            await bot.send_message(message.chat.id, 'Я Вас не понял. Напишите "Да", если хотите получить подарок!', reply_markup=user_kb.right_answer_kb())
    except Exception as ex:
        logging.exception(Exception)
        await state.finish()
        await bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, обратитесь к администратору.", reply_markup=ReplyKeyboardRemove())


# region Вспомогательные методы


async def choose_quest(message):
    questions = await db_service.get_available_questions(db, message.chat.id)
    logging.debug(
        f"Метод choose_quest(). message.text: {message.text} [q['question'] for q in questions]: {[q['question'] for q in questions]}\nlen(questions): {len(questions)}")
    if (len(questions) > 0):
        markup = user_kb.choose_question_kb(str(len(questions)))

        if markup != None:
            await FsmUser.choose_question.set()
            await bot.send_message(message.chat.id, 'Пожалуйста, выбирайте загадку!',  reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, 'Извините, но конкурс сейчас закрыт!', reply_markup=ReplyKeyboardRemove())
    else:
        # Доступных загадок не осталось
        await FsmUser.get_prize.set()
        await bot.send_message(message.chat.id, "Ой, все загадки кончились! 😅\nНадеюсь, это будет самая большая неудача Вашего предстоящего года 🙏\nЗа Ваши настойчивость и усилия предлагаю утешительный приз! 💕", reply_markup=user_kb.right_answer_kb())


async def get_random_gift():
    # Рандомный выбор подарка из оставшихся
    logging.debug(f"Метод get_random_gift().")
    all_gifts = await db.gifts.find().to_list(None)
    logging.debug(f"all_gifts: {all_gifts}")
    gifts = [gift for gift in all_gifts if int(gift['amount']) > 0]  # Не учитываются подарки, которых уже нет в наличии
    logging.debug(f"Без учета подарков, у которых количество = 0. gifts: {gifts}")
    gifts_id = [g['_id'] for g in gifts]
    logging.debug(f"gifts_id: {gifts_id}")
    winner_id = random.choice(gifts_id)
    logging.debug(f"winner_id: {winner_id}")
    prize = next((gift for gift in gifts if gift['_id'] == winner_id), None)
    logging.debug(f"prize: {prize}")
    return prize

# endregion


def register_user_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(choose_question, state=FsmUser.choose_question)
    dispatcher.register_message_handler(write_answer, state=FsmUser.write_answer)
    dispatcher.register_message_handler(get_prize, state=FsmUser.get_prize)
    # lambda message: message.text.lower() in [
    #     u'да', u'да!', u'нет', u'нет!']
    dispatcher.register_message_handler(try_another, lambda message: message.text == u'Да!', state=FsmUser.try_another)
