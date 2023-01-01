from aiogram import types
from aiogram.dispatcher.filters import Text

import typing

import Group
import MyBot
import command_helper

my_bot = MyBot.MyBot()
groups: typing.Dict[str, Group.Group] = {}


@my_bot.dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    text = f'Привет, {message.from_user.first_name}, выбери один из пунктов'
    btn_help = types.KeyboardButton(text='Помощь')
    btn_action = types.KeyboardButton(text='Выбрать предмет')
    markup = types.ReplyKeyboardMarkup()
    markup.add(btn_help, btn_action)
    await my_bot.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@my_bot.dp.message_handler(Text(equals='Помощь'))
async def print_help():
    pass


@my_bot.dp.message_handler(Text(equals='Выбрать предмет'))
async def choose_subject(message: types.Message):
    text = 'Выбери предмет, по которому ты хочешь посмотреть очередь'
    subjects = groups['05'].subjects
    buttons = [types.InlineKeyboardMarkup(text=subject, callback_data=my_bot.cb.new(msg_text=subject)) for subject in
               subjects]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*buttons)
    await my_bot.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@my_bot.dp.message_handler(content_types=['text'])
async def accept_text(message: types.Message) -> None:
    text_from_msg: str = message.text
    if text_from_msg in


@my_bot.dp.message_handler()
def main():
    groups[Group.cur_group] = Group.Group()
    groups[Group.cur_group].subjects.append('Алгоритмы')
    groups[Group.cur_group].subjects.append('ОП')
    MyBot.executor.start_polling(my_bot.dp)


if __name__ == '__main__':
    main()
