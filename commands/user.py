import types
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from create_bot import dispatcher, bot
from config import get_admin_ids
from states.user import FsmUser
from services import db_service, db


async def start(message, res=False):
    try:
        user = await db.users.find_one({"_id": message.chat.id})
        if not user:
            await db_service.add_user(db, message.chat)

        # Команда start
        if message.chat.id in get_admin_ids():
            await bot.send_message(message.chat.id, "Приветствую, админ! Чего желаешь? Сделаю всё, что в моих силах!")
        else:
            # Проверка пользователя на повторное участие. Поле 'hasWon' в коллекции 'users'
            hasWon = False
            if (not hasWon):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton("1")
                item2 = types.KeyboardButton("2")
                item3 = types.KeyboardButton("3")
                item4 = types.KeyboardButton("4")
                markup.add(item1)
                markup.add(item2)
                markup.add(item3)
                markup.add(item4)
                await FsmUser.choose_question.set()
                await bot.send_message(message.chat.id, 'Доброго времени суток, выбирайте загадку!',  reply_markup=markup)
            else:
                # ToDo: протестировать этот кейс. В конце ';)' сделать в виде эмодзи
                await bot.send_message(message.chat.id, 'Вижу, Вы уже поучаствовали в розыгрыше! Давайте дадим шанс другим клиентам ;)')
    except Exception as ex:
        await bot.send_message(message.chat.id, "Произошла ошибка. Пожалуйста, обратитесь к администратору.")


async def help(message, res=False):
    # Команда help
    await bot.send_message(message.chat.id, "Раздел с помощью в разработке, попробуйте позже!")


async def choose_question(message: types.Message, state=FSMContext):
    # if message.chat.id not in ADMIN_ID:
    # Поиск выбранной загадки по message.text
    # Сначала считать все загадки, составить список из questions.number, затем проверить
    # принадлежность message.text этому списку. Если да, то выдаем текст выбранной загадки.
    # chosen_question = db.questions.findOne({"number":{message.text}}) #Проверить, мб надо f-строку
    # Можно еще сохранять в proxy (локал.хранилище) ответ сразу, чтобы не лезть в БД
    async with state.proxy() as quest:
        # quest['question'] = chosen_question["text"] #text - имя поля в коллекции (может поменяю позже)
        # quest['answer'] = chosen_question["answer"] # тут будет массив правильных ответов!
        await FsmUser.write_answer.set()
        # await message.reply(f"Текст выбранной загадки: {chosen_question["text"]}. Тщательно подумай и напиши свой ответ!")


async def write_answer(message: types.Message, state=FSMContext):
    # Проверка введенного ответа
    async with state.proxy() as quest:
        # Проверка по массиву правильных ответов
        if (message.text.lower() in [item.lower() for item in quest['answer']]):
            # Ответ правильный! Протестить работу lower() для всех элементов массива
            await message.reply("Верно! У меня для Вас есть подарок, готовы получить?")
            await FsmUser.finish.set()
    # await state.finish() # Выход из машины состояний, очищение хранилища


async def get_prize(message: types.Message, state=FSMContext):
    # Проверка введенного ответа. Возможные шаблоны утвердительного ответа: да, да!, yes, yes!, y
    # Лучше сделать в виде кнопок!
    if (message.text.lower() in ["да", "да!", "yes", "yes!", "y"]):
        # Рандомный выбор подарка из оставшихся.
        prize = "prizeName"  # Заменить
        await bot.send_message(message.chat.id, f'Поздравляю, Вы выиграли {prize}! С наступающим Новым Годом!')
        await state.finish()
    elif (message.text.lower() in ["нет", "нет!", "no", "no!", "n"]):
        await bot.send_message(message.chat.id, 'Серьезно? Не верю! Кто отказывается от подарка? Попробуйте еще раз!')
    else:
        await bot.send_message(message.chat.id, 'Я Вас не понял. Напишите "Да", если хотите получить приз!')


def register_user_commands(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start, commands=["start"], state=None)
    dispatcher.register_message_handler(help, commands=["help"])
    dispatcher.register_message_handler(choose_question, state=FsmUser.choose_question)
    dispatcher.register_message_handler(write_answer, state=FsmUser.write_answer)
    dispatcher.register_message_handler(get_prize, state=FsmUser.finish)
