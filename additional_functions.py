import typing
from aiogram import types


def get_text_without_command(message: str) -> str:
    return message.split()[1]


def get_many_arg_from_command(message: str) -> list:
    return message.split()


def form_buttons_with_groups(my_bot, my_database) -> typing.List[types.InlineKeyboardButton]:
    buttons = [types.InlineKeyboardButton(text=group["name"], callback_data=my_bot.cb.new(msg_text=group["name"])) for
               group in my_database.db.list_collections() if group["name"] != "users" and group["name"] != "groups"]
    return buttons
