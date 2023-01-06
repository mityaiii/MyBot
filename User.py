class User:
    tg_id: int = None
    name: str = None
    group: str = None
    root: bool = False

    def __init__(self, tg_id:int = 1, name: str = '1', group: str = '1') -> None:
        self.tg_id = tg_id
        self.name = name
        self.group = group



