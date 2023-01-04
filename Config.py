import configparser


class Config:
    config = configparser.ConfigParser()
    config.read('secret/config.ini')