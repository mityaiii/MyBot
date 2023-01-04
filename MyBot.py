from Config import Config

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import configparser


class MyBot:
    __token = None
    bot = None
    dp = None
    cb = CallbackData('post', 'msg_text')

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(MyBot, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self.__token = Config.config['TELEGRAM']['token']
        self.bot = Bot(token=self.__token)
        self.dp = Dispatcher(bot=self.bot, storage=MemoryStorage())
