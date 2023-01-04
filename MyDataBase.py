import User
import Subject
import Group

import pymongo

from Config import Config


class MyDataBase:
    __instance = None
    _client = None
    db = None
    coll = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(MyDataBase, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        self._client = pymongo.MongoClient(Config.config["DATABASE"]["url"])
        self.db = self._client.my_bot

    def is_exist_value(self, param: str, value) -> bool:
        return self.coll.find_one({param: value}) is None

    def is_exist_collection(self, name_of_collection) -> bool:
        return name_of_collection in [group["name"] for group in self.db.list_collections()]

    def add_user(self, user: User.User) -> bool:
        self.coll = self.db.users
        if not self.is_exist_value("_id", user.tg_id):
            self.coll.insert_one({"_id": user.tg_id, "name": user.name, "group": user.group, "root": user.root})
            return True
        return False

    def add_subject(self, subject) -> bool:
        self.coll = self.db[subject.group]
        if not self.is_exist_value("_id", subject.name):
            self.coll.insert_one({"_id": subject.name})
            return True
        return False

    def add_group(self, group: Group.Group) -> bool:
        if not self.is_exist_collection(group.name):
            self.db.create_collection(group.name)
            self.coll = self.db.groups
            self.coll.insert_one({"_id": group.name, "password": group.password, "root_id": group.root_id})
            return True
        return False

    def del_group(self, group: Group.Group):
        self.db[group.name].drop()
        self.db.groups.remove({"_id": group.name})

    def del_subject(self, subject: Subject.Subject):
        pass

    def find_group(self, root_id) -> str:
        return self.db.groups.find_one({"root_id": root_id})["_id"]
