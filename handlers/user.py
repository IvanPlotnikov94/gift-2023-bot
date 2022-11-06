from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardRemove
from create_bot import dispatcher, bot

QUESTS = [
    {
        'id': 1,
        'text': '''
Загадка 1
''',
        'answer': "Ответ 1"
    },
    {
        'id': 2,
        'text': '''
Загадка 2
''',
        'answer': "Ответ 2"
    },
    {
        'id': 3,
        'text': '''
Загадка 3
''',
        'answer': "Ответ 3"
    },
    {
        'id': 4,
        'text': '''
Загадка 4
''',
        'answer': "Ответ 4"
    },
]


async def handle_text(message: types.Message):
    # Получение любого текстового сообщения от пользователя
    please_choose = 'Пожалуйста, выбери одну из загадок!'
    match message.text:
        case "1":
            answer = get_question(1)
        case "2":
            answer = get_question(2)
        case "3":
            answer = get_question(3)
        case "4":
            answer = get_question(4)
        case _:
            answer = please_choose
    if answer != please_choose:
        await bot.send_message(message.chat.id, answer, reply_markup=ReplyKeyboardRemove())
    else:
        await bot.send_message(message.chat.id, answer)


def get_question(id):
    return list(filter(lambda x: x.get('id', '') == id, QUESTS))[0]['text']


def register_user_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(handle_text)
