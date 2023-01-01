from aiogram import Bot
from aiogram import executor
from aiogram import Dispatcher
from aiogram.utils.callback_data import CallbackData

import configparser


class MyBot:
    token = None
    bot = None
    dp = None
    cb = CallbackData('post', 'msg_text')

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(MyBot, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('secret/config.ini')
        self.token = config['TELEGRAM']['token']
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher(bot=self.bot)
