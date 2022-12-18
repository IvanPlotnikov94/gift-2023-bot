from aiogram import Dispatcher, executor
import motor.motor_asyncio as m_as
from config import read_config_for_db
from datetime import datetime


class DbService:
    def __init__(self, bot):
        self.dispatcher = Dispatcher(bot)
        self.config = read_config_for_db()
        self.cluster = m_as.AsyncIOMotorClient(
            "mongodb+srv://gift2023bot:Ub1pak7m@tgbot.ll7mc1z.mongodb.net/gift2023_db?retryWrites=true&w=majority")

        # Коллекция с пользователями (users)
        self.users = self.cluster[f"{self.config['db_name']}"][f"{self.config['users_collection']}"]

        # Коллекция с вопросами (questions)
        self.questions = self.cluster[f"{self.config['db_name']}"][f"{self.config['questions_collection']}"]

        # Коллекция с подарками (gifts)
        self.gifts = self.cluster[f"{self.config['db_name']}"][f"{self.config['gifts_collection']}"]


async def add_user(db: DbService, user):
    # Добавляет пользователя в БД
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db.users.insert_one({
        "_id": user.id,
        "date": str(date),
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "bio": user.bio,
        "type": user.type,
        "title": user.title
    })


async def update_user_has_won(db: DbService, user_id):
    # Проставляет отметку в БД о том, что пользователь выиграл подарок
    db.users.update_one({"_id": user_id},
                        {"$set": {"has_won": "True"}})


async def check_if_user_already_won(db: DbService, user_id):
    # Проверяет, побеждал ли пользователь ранее
    return await db.users.find({"has_won": "True"}).to_list(None)


async def add_question(db: DbService, question, answer):
    # Добавляет загадку в БД
    db.questions.insert_one({
        "question": question,
        "answer": answer
    })


async def get_available_questions(db: DbService, user_id):
    # Получение вопросов, которых пользователь ещё не видел
    available_questions = await db.questions.find({"got_user_id": {"$nin": [user_id]}}).to_list(None)
    return available_questions


async def update_question(db: DbService, question_id, user_id):
    # Проставляет отметку, что пользователю был задан этот вопрос
    db.questions.update_one({"_id": question_id},
                            {"$push": {"got_user_id": user_id}})


async def add_gift(db: DbService, gift):
    # Добавляет подарок в БД
    db.gifts.insert_one({
        "name": gift["name"],
        "photo_id": gift["photo_id"],
        "amount": gift["amount"],
        "userId": gift["user_id"]
    })


async def subtract_gift_amount(db: DbService, gift):
    # Фиксирует факт вручения подарка - уменьшает количество данного подарка в БД на 1
    db.gifts.update_one({"_id": gift["_id"]},
                        {"$set": {"amount": str(int(gift["amount"]) - 1)}})


async def mark_gift(db: DbService, gift, user_id):
    # Фиксирует, что данный пользователь забрал подарок
    db.gifts.update_one({"_id": gift["_id"]},
                        {"$push": {"won_user_id": user_id}})
