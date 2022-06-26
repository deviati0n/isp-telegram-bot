import logging
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from project.project_context import ProjectContext

context = ProjectContext()

API_TOKEN = context.bot_config.token
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
