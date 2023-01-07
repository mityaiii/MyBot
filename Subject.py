import typing


class Subject:
    name: str
    people: int = 0
    cur_queue: typing.List[int] = []
    msg_ids: typing.List[int] = []
    group: str
