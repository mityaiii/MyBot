class Group:
    name: str = None
    root_id: str = None
    password: str = None

    def __init__(self, name: str, root_id: str, password: str):
        self.name = name
        self.root_id = root_id
        self.password = password
