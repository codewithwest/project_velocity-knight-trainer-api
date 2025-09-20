import os
from pymongo import MongoClient


class Connection:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MONGO_URI = os.environ.get(
        'MONGO_URI') or 'mongodb://localhost:27017/'
    MONGO_DATABASE_NAME = os.environ.get(
        'MONGO_DATABASE_NAME') or 'velocity-knight-trainer-api'
    config = {
        "host": "localhost",
        "port": 27017,
        "username": "",
        "password": ""

    }

    def __new__(cls):
        connection = MongoClient(**cls.config)

        return connection[cls.MONGO_DATABASE_NAME]
