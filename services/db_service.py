from aiogram import Dispatcher, executor
import motor.motor_asyncio as m_as
from config import read_config_for_db


class DbService:
    def __init__(self, bot):
        self.dispatcher = Dispatcher(bot)
        self.config = read_config_for_db()
        self.connection_string = f"mongodb+srv://{self.config['username']}:{self.config['password']}@{self.config['cluster_name']}.{self.config['domain_name']}/{self.config['db_name']}?retryWrites=true&w=majority"
        self.collection = self.cluster[f"{self.config['db_name']}"][f"{self.config['collection_name']}"]
