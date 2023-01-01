import Subject

import typing

cur_group = '05'

class Group:
    url: str = None
    root: str = None
    subjects: typing.List[Subject.Subject] = []
