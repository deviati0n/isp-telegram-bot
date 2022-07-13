from aiogram import types
from create_bot import dp


@dp.message_handler()
async def echo(message: types.Message):
    """
    Sends a echo message
    :param message: message from telegram chat
    """
    await message.answer(message.text)


