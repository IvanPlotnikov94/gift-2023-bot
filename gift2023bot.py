from aiogram import executor
from create_bot import dispatcher
from handlers import admin as admin_handlers, user as user_handlers
from commands import admin as admin_commands, user as user_commands

admin_commands.register_admin_commands(dispatcher)
user_commands.register_user_commands(dispatcher)
user_handlers.register_user_handlers(dispatcher)

executor.start_polling(dispatcher)
