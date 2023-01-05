import MyBot
import Group
import Subject
import User
import MyDataBase
import additional_functions

import types
import typing

from Config import Config

from aiogram import types, executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from Forms import *

my_bot = MyBot.MyBot()
my_database = MyDataBase.MyDataBase()
my_id = int(Config.config["ID"]["my_id"])


class EnvironmentVariables:
    user: User.User
    subject: Subject.Subject = Subject.Subject()
    group: Group.Group = Group.Group()


@my_bot.dp.callback_query_handler(my_bot.cb.filter())
async def pressed_button(call: types.CallbackQuery, callback_data: dict) -> None:
    action, msg = callback_data['msg_text'].split('|')
    if msg in my_database.get_list_of_groups():
        info = call.from_user
        if action == 'choose':
            await my_bot.bot.send_message(chat_id=info.id, text='Введите пароль группы')
            await LogginGroup.password.set()
            EnvironmentVariables.user = User.User(tg_id=info.id, name=info.first_name, group=msg)
        elif action == 'del':
            my_database.del_group(msg)
            await my_bot.bot.send_message(chat_id=info.id, text=f'Вы удалили группу {msg}')
    if msg in my_database.get_list_of_subjects(my_database.get_user_group(call.from_user.id)):
        EnvironmentVariables.subject.name = msg
        EnvironmentVariables.subject.group = my_database.get_user_group(call.from_user.id)
        my_database.del_subject(EnvironmentVariables.subject)
        await my_bot.bot.send_message(chat_id=call.from_user.id,
                                      text=f'Вы удалили предмет {msg}')


@my_bot.dp.message_handler(commands=['start'])
async def start_handler(message: types.Message) -> None:
    text = f'Привет, {message.from_user.first_name}, выбери свою группу'
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = additional_functions.form_buttons_with_groups(my_bot, my_database, 'choose')
    markup.add(*buttons)
    await my_bot.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@my_bot.dp.message_handler(state=LogginGroup.password)
async def process_name(message: types.Message, state: FSMContext):
    password = my_database.db.groups.find_one({"_id": EnvironmentVariables.user.group})["password"]
    if message.text == password:
        my_database.add_user(EnvironmentVariables.user)
        await message.reply(text="Поздравляю! Вы ввели правильный пароль")
        if message.from_user.id == my_id:
            await set_commands_in_menu(additional_functions.set_main_commands())
        elif message.from_user.id == my_database.db.groups.find_one({"root_id": EnvironmentVariables.user.group}):
            await set_commands_in_menu(additional_functions.set_commands_for_root())
        else:
            await set_commands_in_menu(None)
        await state.finish()
    else:
        await message.reply(text="Вы ввели неправильный пароль")


@my_bot.dp.message_handler(state=FormForGroup.name_of_group)
async def process_name(message: types.Message, state: FSMContext):
    if not my_database.is_exist_collection(message.text):
        EnvironmentVariables.user = User.User.name
        EnvironmentVariables.group.name = message.text
        await FormForGroup.next()
        await message.reply(
            f"Введите id человека, который будет старостой в группе {EnvironmentVariables.group.name}")
    else:
        await message.reply(f"Группа с таким названием уже существует")


@my_bot.dp.message_handler(state=FormForGroup.root_id)
async def process_name(message: types.Message, state: FSMContext):
    EnvironmentVariables.group.root_id = int(message.text)
    await FormForGroup.next()
    await message.reply(
        f"Вы создали группу {EnvironmentVariables.group.name} и назначили старостой {EnvironmentVariables.group.root_id}."
        " Теперь необходимо назначить пароль для группы")


@my_bot.dp.message_handler(state=FormForGroup.password)
async def process_name(message: types.Message, state: FSMContext):
    EnvironmentVariables.group.password = message.text
    await message.reply(f"Все прошло успешно!")
    await state.finish()
    my_database.add_group(EnvironmentVariables.group)


@my_bot.dp.message_handler(commands=['add_group'])
async def add_group_with_command(message: types.Message) -> None:
    await FormForGroup.name_of_group.set()
    await my_bot.bot.send_message(chat_id=message.from_user.id,
                                  text='Напишите название группы или /cancel, чтобы отменить операцию')


@my_bot.dp.message_handler(commands=['del_group'])
async def del_group_with_command(message: types.Message) -> None:
    buttons = additional_functions.form_buttons_with_groups(my_bot, my_database, 'del')
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*buttons)
    await my_bot.bot.send_message(chat_id=message.from_user.id, text='Выберите группу, которую вы хотите удалить',
                                  reply_markup=markup)


@my_bot.dp.message_handler(state=FormForAddSubject.name_of_subject)
async def process_name(message: types.Message, state: FSMContext):
    comm = await state.get_data()
    print(state.get_data())
    if comm.get("comm") == "add":
        EnvironmentVariables.subject.name = message.text
        await FormForAddSubject.next()
        await message.reply(text='Укажите число людей в группе')


@my_bot.dp.message_handler(state=FormForAddSubject.quantity_of_people)
async def process_name(message: types.Message, state: FSMContext):
    EnvironmentVariables.subject.quantity_of_person = int(message.text)
    await message.reply(text=f"Вы добавили предмет {EnvironmentVariables.subject.name}"
                             f" с количеством учистников: {EnvironmentVariables.subject.quantity_of_person}")
    my_database.add_subject(EnvironmentVariables.subject)
    await state.finish()


@my_bot.dp.message_handler(commands=['add_subject'])
async def add_subject_with_command(message: types.Message, state: FSMContext) -> None:
    EnvironmentVariables.subject.group = my_database.find_group(message.from_user.id)
    await my_bot.bot.send_message(chat_id=message.from_user.id,
                                  text="Укажите название предмета, который вы хотите добавить")
    await state.set_data({"comm": "add"})
    await FormForAddSubject.name_of_subject.set()


@my_bot.dp.message_handler(commands=['del_subject'])
async def del_subject_with_command(message: types.Message) -> None:
    buttons = additional_functions.form_buttons_with_subjects(my_bot, my_database, my_database.get_user_group(
        message.from_user.id), "")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*buttons)
    await my_bot.bot.send_message(chat_id=message.from_user.id,
                                  text="Укажите название предмета, который вы хотите удалить", reply_markup=markup)


@my_bot.dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Cancelled.')


async def set_commands_in_menu(my_commands):
    if my_commands is not None:
        list_of_commands = [types.BotCommand(command[0], command[1]) for command in my_commands.items()]
        await my_bot.dp.bot.set_my_commands(list_of_commands)


def main():
    executor.start_polling(my_bot.dp)


if __name__ == '__main__':
    main()
