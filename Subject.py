import typing


class Subject:
    name: str
    people: int = 0
    cur_queue: typing.List[str] = []
    group: str