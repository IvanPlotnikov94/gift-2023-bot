from create_bot import bot
from services import db_service
import logging

db = db_service.DbService(bot)

logging.basicConfig(
    level=logging.DEBUG,
    filename="log/gift2023.log",
    format=u"%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S'
)
# logging._defaultFormatter = logging.Formatter(u"%(message)s")
