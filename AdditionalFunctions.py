import typing
from aiogram import types

import Group
import MyBot
import MyDataBase
import Subject
import User

ROW_SIZE: int = 5


def get_text_without_command(message: str) -> str:
    return message.split()[1]


def get_many_arg_from_command(message: str) -> list:
    return message.split()


def form_buttons_with_groups(my_bot: MyBot, my_database: MyDataBase, action: str) -> typing.List[
    types.InlineKeyboardButton]:
    buttons = [types.InlineKeyboardButton(text=group, callback_data=my_bot.cb.new(msg_text=f'{action}||{group}')) for
               group in my_database.get_list_of_groups()]
    return buttons


def form_buttons_with_subjects(my_bot: MyBot.MyBot, my_database: MyDataBase.MyDataBase, group: str,
                               action: str) -> typing.List[types.InlineKeyboardButton]:
    buttons = [types.InlineKeyboardButton(text=subject, callback_data=my_bot.cb.new(msg_text=f'{action}||{subject}'))
               for subject in my_database.get_list_of_subjects(group)]
    return buttons


def form_buttons_with_queue(my_bot: MyBot.MyBot, subject: Subject.Subject, user: User.User) -> \
        typing.Tuple[str, typing.List[types.InlineKeyboardButton]]:
    buttons: typing.List[types.InlineKeyboardButton] = []
    text: str = f'Очередь на предмет {subject.name}:\n'
    for i in range(subject.people):
        text += f'{i + 1})'
        if subject.cur_queue[i] is None:
            buttons.append(types.InlineKeyboardButton(text=f'{i + 1}✅',
                                                      callback_data=my_bot.cb.new(
                                                          msg_text=f'enroll|{subject.name}|{i + 1}')))
        else:
            text += f' {user.name}'
            buttons.append(types.InlineKeyboardButton(text=f'{i + 1}❌',
                                                      callback_data=my_bot.cb.new(
                                                          msg_text=f'check_out|{subject.name}|{i + 1}')))
        text += '\n'
    return text, buttons


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


def get_digits_of_number(number: int) -> int:
    i = 1
    while number > 0:
        number //= 10
        i += 1
    return i


async def enroll(my_bot: MyBot.MyBot, my_database: MyDataBase.MyDataBase, user: User.User, subject: Subject.Subject,
                 msg: types.Message, number: int) -> None:
    number -= 1
    subject.cur_queue = my_database.get_queue(user, subject)

    if user.tg_id in subject.cur_queue:
        await my_bot.bot.send_message(chat_id=user.tg_id, text='Нельзя записаться дважды(')
    elif subject.cur_queue[number] is None:
        subject.cur_queue[number] = user.tg_id
        text, buttons = form_buttons_with_queue(my_bot, subject, user)
        new_markup = types.InlineKeyboardMarkup(row_width=5)
        new_markup.add(*buttons)
        digits = get_digits_of_number(number)

        text = text[:text.find(f'{number + 1})') + digits] + f' {user.name}' + '\n' + text[text.find(
            f'{number + 2}'):]
        await msg.edit_text(text=text, reply_markup=new_markup)
        my_database.enroll(user, subject, number)
    else:
        await my_bot.bot.send_message(chat_id=user.tg_id, text='Извините, место занято')


async def check_out(my_bot: MyBot.MyBot, my_database: MyDataBase.MyDataBase, user: User.User, subject: Subject.Subject,
                    msg: types.Message, number: int) -> None:
    number -= 1
    subject.cur_queue[number] = None
    new_markup = types.InlineKeyboardMarkup(row_width=5)
    text, buttons = form_buttons_with_queue(my_bot, subject, user)
    new_markup.add(*buttons)
    digits = get_digits_of_number(number)
    if number + 1 == subject.people:
        text = text[:text.find(f'{number + 1}') + digits]
    else:
        text = text[:text.find(f'{number + 1})') + digits] + '\n' + text[text.find(f'{number + 2}'):]
    await msg.edit_text(text=text, reply_markup=new_markup)
    my_database.check_out(user, subject, number)


def change_for_all_members():
    pass
