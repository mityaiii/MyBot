from aiogram import types
import typing

roots = typing.Dict[str, str]


def get_text_without_command(message: str) -> str:
    message_without_command = message.split()
    return message_without_command[1]


def is_root_user(user_id: str) -> bool:
    if user_id in roots:
        return True
    return False
