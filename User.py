class User:
    tg_id: str = None
    name: str = None
    group: str = None
    root: bool = False

    def __init__(self, tg_id: str, name: str, group: str) -> None:
        self.tg_id = tg_id
        self.name = name
        self.group = group

