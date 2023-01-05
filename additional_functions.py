import typing
from aiogram import types

import Group
import MyBot
import MyDataBase


def get_text_without_command(message: str) -> str:
    return message.split()[1]


def get_many_arg_from_command(message: str) -> list:
    return message.split()


def form_buttons_with_groups(my_bot: MyBot, my_database: MyDataBase, action: str) -> typing.List[
    types.InlineKeyboardButton]:
    buttons = [types.InlineKeyboardButton(text=group, callback_data=my_bot.cb.new(msg_text=action + '|' + group)) for
               group in my_database.get_list_of_groups()]
    return buttons


def form_buttons_with_subjects(my_bot: MyBot.MyBot, my_database: MyDataBase.MyDataBase, group: str,
                               action: str) -> typing.List[types.InlineKeyboardButton]:
    buttons = [types.InlineKeyboardButton(text=subject, callback_data=my_bot.cb.new(msg_text=action + '|' + subject))
               for subject in my_database.get_list_of_subjects(group)]
    return buttons


def set_commands_for_root() -> typing.Dict[str, str]:
    my_commands = {
        "add_subject": "Добавить предмет в свою группу",
        "del_subject": "Удалить предмет"

    }
    return my_commands


def set_main_commands() -> typing.Dict[str, str]:
    my_commands = set_commands_for_root()
    my_commands["add_group"] = "Добавить группу"
    my_commands["del_group"] = "Удалить группу"
    return my_commands


def find_root():
    pass
