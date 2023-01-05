import typing


class Subject:
    name: str
    quantity_of_person: int = 0
    cur_queue: typing.List[str] = []
    group: str
