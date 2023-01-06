from aiogram.dispatcher.filters.state import State, StatesGroup


class FormForGroup(StatesGroup):
    name_of_group = State()
    root_id = State()
    password = State()


class LoginGroup(StatesGroup):
    password = State()


class FormForAddSubject(StatesGroup):
    name_of_subject = State()
    quantity_of_people = State()


class FormForDelSubject(StatesGroup):
    name_of_subject = State()
