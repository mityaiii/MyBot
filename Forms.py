from aiogram.dispatcher.filters.state import State, StatesGroup


class FormForGroup(StatesGroup):
    name_of_group = State()
    root_id = State()
    password = State()
    data: dict = {}


class LogginGroup(StatesGroup):
    password = State()
    data: dict = {}
