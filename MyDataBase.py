import typing

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

    def get_list_of_subjects(self, group: str) -> typing.List[str]:
        return [subject["_id"] for subject in self.db[group].find({})]

    def get_list_of_groups(self) -> typing.List[str]:
        groups = [group["name"] for group in self.db.list_collections()]
        groups.remove("users")
        groups.remove("groups")
        return groups

    def get_user_group(self, tg_id: int) -> str:
        return self.db.users.find_one({"_id": tg_id})["group"]

    def get_subject(self, group: str, name_of_subject: str) -> Subject.Subject:
        subject_from_db = self.db[group].find_one({"_id": f"{name_of_subject}"})
        subject = Subject.Subject()
        subject.name = subject_from_db["_id"]
        subject.people = subject_from_db["people"]
        subject.cur_queue = subject_from_db["cur_queue"]
        subject.msg_ids = subject_from_db["msg_history"]
        return subject

    def get_user(self, tg_id) -> User.User:
        user_from_db = self.db.users.find_one({"_id": tg_id})
        user = User.User(user_from_db["_id"], user_from_db["name"], user_from_db["group"])
        return user

    def add_user(self, user: User.User) -> bool:
        self.coll = self.db.users
        if self.is_exist_value("_id", user.tg_id):
            if self.db.groups.find_one({"_id": user.group})["root_id"] == user.tg_id:
                user.root = True
            self.coll.insert_one({"_id": user.tg_id, "name": user.name, "group": user.group, "root": user.root})
            return True
        return False

    def add_subject(self, subject) -> bool:
        self.coll = self.db[subject.group]
        if self.is_exist_value("_id", subject.name):
            subject.cur_queue = [None] * subject.people
            subject.msg_ids = [None] * subject.people
            self.coll.insert_one(
                {"_id": subject.name, "people": subject.people, "cur_queue": subject.cur_queue,
                 "msg_history": subject.msg_ids})
            return True
        return False

    def add_group(self, group: Group.Group) -> bool:
        if not self.is_exist_collection(group.name):
            self.db.create_collection(group.name)
            self.coll = self.db.groups
            self.coll.insert_one({"_id": group.name, "password": group.password, "root_id": group.root_id})
            return True
        return False

    def del_group(self, group: str) -> None:
        self.coll = self.db[group]
        self.coll.drop()
        self.db.groups.delete_one({"_id": group})

    def del_subject(self, group: str, subject: Subject.Subject) -> None:
        self.db[group].delete_one({"_id": subject.name})

    def find_group(self, root_id) -> str:
        return self.db.groups.find_one({"root_id": root_id})["_id"]

    def get_queue(self, user: User.User, subject: Subject.Subject) -> typing.List[int]:
        return self.db[user.group].find_one({"_id": subject.name})["cur_queue"]

    def get_msg_history(self, user: User.User, subject: Subject.Subject) -> typing.List[int]:
        return self.db[user.group].find_one({"_id": subject.name})["msg_history"]

    def enroll(self, user: User.User, subject: Subject.Subject, message_id: int, number: int) -> None:
        cur_queue = self.get_queue(user, subject)
        msg_history = self.get_msg_history(user, subject)
        if cur_queue[number] is None:
            cur_queue[number] = user.tg_id
            msg_history[number] = message_id
            self.db[user.group].update_one({"_id": subject.name}, {"$set": {"cur_queue": cur_queue}})
            self.db[user.group].update_one({"_id": subject.name}, {"$set": {"msg_history": msg_history}})

    def check_out(self, user: User.User, subject: Subject.Subject, number: int) -> None:
        cur_queue = self.get_queue(user, subject)
        msg_history = self.get_msg_history(user, subject)
        if cur_queue[number] is not None:
            cur_queue[number] = None
            msg_history[number] = None
            self.db[user.group].update_one({"_id": subject.name}, {"$set": {"cur_queue": cur_queue}})
            self.db[user.group].update_one({"_id": subject.name}, {"$set": {"msg_history": msg_history}})
