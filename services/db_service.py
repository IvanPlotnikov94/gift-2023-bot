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


async def add_question(db: DbService, question, answer):
    # Добавляет загадку в БД
    db.questions.insert_one({
        "question": question,
        "answer": answer
    })


async def add_gift(db: DbService, gift):
    # Добавляет подарок в БД
    db.gifts.insert_one({
        "name": gift["name"],
        "photo_id": gift["photo_id"],
        "amount": gift["amount"],
        "userId": gift["user_id"]
    })
