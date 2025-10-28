import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class Connection:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MONGO_URI = os.environ.get(
        'MONGO_URI', 'mongodb://localhost:27017/velocity-knight-trainer-api')

    _db = None

    @classmethod
    def get_db(cls):
        if cls._db is None:
            try:
                client = MongoClient(cls.MONGO_URI, serverSelectionTimeoutMS=5000)
                # The ismaster command is cheap and does not require auth.
                client.admin.command('ismaster')
                cls._db = client.get_database()
                print("MongoDB connection successful.")
            except ConnectionFailure as e:
                print(f"Error connecting to MongoDB: {e}")
                raise
        return cls._db
