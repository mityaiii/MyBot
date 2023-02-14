import MyBot
import Group
import Subject
import User
import MyDataBase
import AdditionalFunctions
import ChatGPT

from Config import Config

from aiogram import types, executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from Forms import *

my_bot = MyBot.MyBot()
my_database = MyDataBase.MyDataBase()
my_id = int(Config.config["ID"]["my_id"])


class EnvironmentVariables:
    user: User.User = User.User()
    subject: Subject.Subject = Subject.Subject()
    group: Group.Group = Group.Group()


@my_bot.dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Cancelled.')


@my_bot.dp.message_handler(Text(equals='Помощь'))
async def print_help(message: types.Message):
    text = (
        f"""
        Привет, {message.from_user.first_name}, это бот, который помогает организовать очередь.
        Мой исходный код вы можете найти по ссылке https://github.com/mityaiii/QueuePythonBot.git. Если есть желания помочь или доработать бота, то просьба добавлять все в ведку develop и делать pull request в main.
        Если вам понравилось приложение, нажмите кнопку stars
    Что я умею:
        1. Добавлять/Удалять группу (add_group/del_group).
        2. Добавлять/Удалять предмет (add_subject/del_subject).
        3. Исключать человека из очереди (del_person).
        4. Поддерживать очередь на предмет.
    Для того, чтобы записаться необходимо:
        1. Нажать на кнопку <Выбрать предмет>.
        2. Выбрать предмет из выпавшего списка.
        3. Нажать на кнопку с номером, которым вы хотите стать в очереди
        4. Если очередь занята, то кнопка будет иметь следующий вид: ❌, если запись доступна, то ✅ 
        """)
    await my_bot.bot.send_message(chat_id=message.from_user.id, text=text)


@my_bot.dp.message_handler(Text(equals='Выбрать предмет'))
async def choose_subject(message: types.Message):
    buttons = AdditionalFunctions.form_buttons_with_subjects(my_bot, my_database,
                                                             my_database.get_user_group(message.from_user.id),
                                                             "choose")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*buttons)
    await my_bot.bot.send_message(message.from_user.id, text='Выберите предмет, на который вы хотели бы записаться',
                                  reply_markup=markup)


@my_bot.dp.callback_query_handler(my_bot.cb.filter())
async def pressed_button(call: types.CallbackQuery, callback_data: dict) -> None:
    action, name_of_subject, msg = callback_data["msg_text"].split("|")
    info = call.from_user
    if msg in my_database.get_list_of_groups():
        if action == "choose":
            await my_bot.bot.send_message(chat_id=info.id, text='Введите пароль группы')
            await LoginGroup.password.set()
            EnvironmentVariables.user = User.User(tg_id=info.id, name=info.first_name, group=msg)
        elif action == "del":
            my_database.del_group(msg)
            await my_bot.bot.send_message(chat_id=info.id, text=f'Вы удалили группу {msg}')
    elif msg in my_database.get_list_of_subjects(my_database.get_user_group(info.id)):
        name_of_group = my_database.get_user_group(info.id)
        EnvironmentVariables.subject = my_database.get_subject(name_of_group, msg)
        EnvironmentVariables.user = my_database.get_user(info.id)
        if action == "choose":
            text, buttons = AdditionalFunctions.form_buttons_with_queue(my_bot, my_database,
                                                                        EnvironmentVariables.subject)

            markup = types.InlineKeyboardMarkup(row_width=5)
            markup.add(*buttons)
            _ = await my_bot.bot.send_message(chat_id=info.id, text=text, reply_markup=markup)

            number_of_old_msg = my_database.find_user_number(EnvironmentVariables.user,
                                                             EnvironmentVariables.subject)

            if number_of_old_msg is not None and \
                    EnvironmentVariables.subject.msg_ids[number_of_old_msg] is not None:
                id_of_new_msg = _["message_id"]

                # await my_bot.bot.delete_message(info.id,
                #                                 EnvironmentVariables.subject.msg_ids[number_of_old_msg])
                my_database.update_history_of_msg(EnvironmentVariables.user, EnvironmentVariables.subject,
                                                  id_of_new_msg, number_of_old_msg)

        elif action == "del":
            my_database.del_subject(name_of_group, EnvironmentVariables.subject)
            await my_bot.bot.send_message(chat_id=info.id, text=f'Вы удалили предмет {msg}')
        elif action == "del_person":
            text, buttons = AdditionalFunctions.form_buttons_with_queue(my_bot, my_database,
                                                                        EnvironmentVariables.subject)
            markup = types.InlineKeyboardMarkup(row_width=5)
            markup.add(*buttons)
            await my_bot.bot.send_message(chat_id=info.id, text=text, reply_markup=markup)
    elif msg.isdigit():
        name_of_group = my_database.get_user_group(info.id)
        EnvironmentVariables.subject = my_database.get_subject(name_of_group, name_of_subject)
        EnvironmentVariables.user = my_database.get_user(info.id)

        if action == "enroll":
            await AdditionalFunctions.enroll(my_bot, my_database, EnvironmentVariables.user,
                                             EnvironmentVariables.subject, call.message, int(msg))
        elif action == "check_out":
            await AdditionalFunctions.check_out(my_bot, my_database, EnvironmentVariables.user,
                                                EnvironmentVariables.subject, int(msg))
    await my_bot.bot.answer_callback_query(call.id)


@my_bot.dp.message_handler(commands=['start'])
async def start_handler(message: types.Message) -> None:
    text = f'Привет, {message.from_user.first_name}, выбери свою группу'
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = AdditionalFunctions.form_buttons_with_groups(my_bot, my_database, 'choose')
    markup.add(*buttons)
    await my_bot.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@my_bot.dp.message_handler(state=LoginGroup.password)
async def process_name(message: types.Message, state: FSMContext):
    password = my_database.db.groups.find_one({"_id": EnvironmentVariables.user.group})["password"]
    if message.text == password:
        my_database.add_user(EnvironmentVariables.user)
        button_help = types.KeyboardButton(text='Помощь')
        button_subject = types.KeyboardButton(text='Выбрать предмет')
        markup = types.ReplyKeyboardMarkup(row_width=1)
        markup.add(button_subject, button_help)
        await message.reply(text="Поздравляю! Вы ввели правильный пароль", reply_markup=markup)

        if message.from_user.id == my_id:
            await set_commands_in_menu(AdditionalFunctions.set_main_commands())
        elif message.from_user.id == my_database.db.groups.find_one({"root_id": EnvironmentVariables.user.group}):
            await set_commands_in_menu(AdditionalFunctions.set_commands_for_root())
        else:
            await set_commands_in_menu(None)
        await state.finish()
    else:
        await message.reply(text="Вы ввели неправильный пароль")


@my_bot.dp.message_handler(state=FormForGroup.name_of_group)
async def process_name(message: types.Message):
    if not my_database.is_exist_collection(message.text):
        EnvironmentVariables.user = User.User.name
        EnvironmentVariables.group.name = message.text
        await FormForGroup.next()
        await message.reply(
            f"Введите id человека, который будет старостой в группе {EnvironmentVariables.group.name}")
    else:
        await message.reply(f"Группа с таким названием уже существует")


@my_bot.dp.message_handler(state=FormForGroup.root_id)
async def process_name(message: types.Message):
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
    if message.from_user.id == Config.config['ID']['my_id']:
        await FormForGroup.name_of_group.set()
        await my_bot.bot.send_message(chat_id=message.from_user.id,
                                      text='Напишите название группы или /cancel, чтобы отменить операцию')
    else:
        await my_bot.bot.send_message(message.from_user.id,
                                      text='Only one person can do it...')


@my_bot.dp.message_handler(commands=['del_group'])
async def del_group_with_command(message: types.Message) -> None:
    if my_database.is_root_id(message.from_user.id):
        buttons = AdditionalFunctions.form_buttons_with_groups(my_bot, my_database, 'del')
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*buttons)
        await my_bot.bot.send_message(chat_id=message.from_user.id, text='Выберите группу, которую вы хотите удалить',
                                      reply_markup=markup)
    else:
        await AdditionalFunctions.say_no(my_bot, message)


@my_bot.dp.message_handler(state=FormForAddSubject.name_of_subject)
async def process_name(message: types.Message, state: FSMContext):
    comm = await state.get_data()
    if comm.get("comm") == "add":
        EnvironmentVariables.subject.name = message.text
        await FormForAddSubject.next()
        await message.reply(text='Укажите число людей в группе')


@my_bot.dp.message_handler(state=FormForAddSubject.quantity_of_people)
async def process_name(message: types.Message, state: FSMContext):
    EnvironmentVariables.subject.people = int(message.text)
    await message.reply(text=f"Вы добавили предмет {EnvironmentVariables.subject.name}"
                             f" с количеством участников: {EnvironmentVariables.subject.people}")
    my_database.add_subject(EnvironmentVariables.subject)
    await state.finish()


@my_bot.dp.message_handler(commands=['add_subject'])
async def add_subject_with_command(message: types.Message, state: FSMContext) -> None:
    EnvironmentVariables.subject.group = my_database.find_group(message.from_user.id)
    _ = await my_bot.bot.send_message(chat_id=message.from_user.id,
                                  text="Укажите название предмета, который вы хотите добавить")
    await state.set_data({"comm": "add"})
    await FormForAddSubject.name_of_subject.set()


@my_bot.dp.message_handler(commands=['del_subject'])
async def del_subject_with_command(message: types.Message) -> None:
    if my_database.is_root_id(message.from_user.id):
        buttons = AdditionalFunctions.form_buttons_with_subjects(my_bot, my_database, my_database.get_user_group(
            message.from_user.id), "del")
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*buttons)
        await my_bot.bot.send_message(chat_id=message.from_user.id,
                                      text="Укажите название предмета, который вы хотите удалить", reply_markup=markup)
    else:
        await AdditionalFunctions.say_no(my_bot, message)


@my_bot.dp.message_handler(commands=['del_person'])
async def del_person_with_command(message: types.Message) -> None:
    if my_database.is_root_id(message.from_user.id):
        await my_bot.bot.send_message(chat_id=message.from_user.id,
                                      text="Вы можете отписать одного человека, нажав ❌ в том, где он записан")
        EnvironmentVariables.user = my_database.get_user(message.from_user.id)
        my_database.swap_editor_status(EnvironmentVariables.user)
    else:
        await AdditionalFunctions.say_no(my_bot, message)


@my_bot.dp.message_handler(content_types="text")
async def answer_chatgpt(message: types.Message):
    if not (message.text in ChatGPT.ChatGPT.phrases_for_ignore):
        answer = ChatGPT.ChatGPT.get_answer(message.text)
        await my_bot.bot.send_message(chat_id=message.from_user.id, text=answer)


async def set_commands_in_menu(my_commands) -> None:
    if my_commands is not None:
        list_of_commands = [types.BotCommand(command[0], command[1]) for command in my_commands.items()]
        await my_bot.dp.bot.set_my_commands(list_of_commands)


def main():
    executor.start_polling(my_bot.dp)


if __name__ == '__main__':
    main()
