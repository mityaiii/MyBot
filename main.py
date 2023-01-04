import MyBot
import Group
import User
import MyDataBase
import additional_functions

import types
import pymongo
import typing

from Config import Config

from aiogram import types, executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from Forms import FormForGroup, LogginGroup

my_bot = MyBot.MyBot()
my_database = MyDataBase.MyDataBase()
god_id = Config.config["ID"]["my_id"]


class EnvironmentVariables:
    user: User.User


@my_bot.dp.callback_query_handler(my_bot.cb.filter())
async def pressed_button(call: types.CallbackQuery, callback_data: dict) -> None:
    if callback_data['msg_text'] in [group["name"] for group in my_database.db.list_collections()]:
        info = call.from_user
        await my_bot.bot.send_message(chat_id=info.id, text='Введите пароль группы')
        await FormForGroup.password.set()
        EnvironmentVariables.user = User.User(tg_id=info.id, name=info.first_name, group=callback_data['msg_text'])


@my_bot.dp.message_handler(commands=['start'])
async def start_handler(message: types.Message) -> None:
    text = f'Привет, {message.from_user.first_name}, выбери свою группу'
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = additional_functions.form_buttons_with_groups(my_bot, my_database)
    markup.add(*buttons)
    await my_bot.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@my_bot.dp.message_handler(state=LogginGroup.password)
async def process_name(message: types.Message, state: FSMContext):
    password = my_database.db.groups.find_one({"_id": EnvironmentVariables.user.group})
    if message.text == password:
        my_database.add_user(EnvironmentVariables.user)
        await message.reply(text="Все прошло успешно!")
        await state.finish()
    else:
        await message.reply(text="Вы ввели неправильный пароль")


@my_bot.dp.message_handler(state=FormForGroup.name_of_group)
async def process_name(message: types.Message, state: FSMContext):
    if not my_database.is_exist_collection(message.text):
        FormForGroup.data['name_of_group'] = message.text
        await FormForGroup.next()
        await message.reply(
            f"Введите id человека, который будет старостой в группе {FormForGroup.data['name_of_group']}")
    else:
        await message.reply(f"Группа с таким названием уже существует")


@my_bot.dp.message_handler(state=FormForGroup.root_id)
async def process_name(message: types.Message, state: FSMContext):
    FormForGroup.data['root_id'] = message.text
    await FormForGroup.next()
    await message.reply(
        f"Вы создали группу {FormForGroup.data['name_of_group']} и назначили старостой {FormForGroup.data['root_id']}."
        " Теперь неоюходимо назначить пароль для группы")


@my_bot.dp.message_handler(state=FormForGroup.password)
async def process_name(message: types.Message, state: FSMContext):
    FormForGroup.data['password'] = message.text
    await message.reply(f"Все прошло успешно!")
    await state.finish()
    my_database.add_group(
        Group.Group(FormForGroup.data["name_of_group"], FormForGroup.data["root_id"], FormForGroup.data["password"]))


@my_bot.dp.message_handler(commands=['add_group'])
async def add_group_with_command(message: types.Message) -> None:
    await FormForGroup.name_of_group.set()
    await my_bot.bot.send_message(chat_id=message.from_user.id,
                                  text='Напишите название группы или /cancel, чтобы отменить операцию')


@my_bot.dp.message_handler(commands=['del_group'])
async def del_group_with_command(message: types.Message) -> None:
    buttons = additional_functions.form_buttons_with_groups(my_bot, my_database)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*buttons)
    await my_bot.bot.send_message(chat_id=message.from_user.id, text='Выберите группу, которую вы хотите удалить',
                                  reply_markup=markup)


@my_bot.dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Cancelled.')


def main():
    executor.start_polling(my_bot.dp)


if __name__ == '__main__':
    main()
