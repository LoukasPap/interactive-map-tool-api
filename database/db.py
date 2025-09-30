import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

class MongoDBClientSingleton:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            uri = os.environ.get("MONGODB_URI")
            if not uri:
                raise RuntimeError("MONGODB_URI not set")
            cls._client = MongoClient(uri, server_api=ServerApi('1'))
        return cls._client

def get_db():
    db_name = os.environ.get("MONGODB_DB")
    if not db_name:
        raise RuntimeError("MONGODB_DB not set")
    client = MongoDBClientSingleton.get_client()
    return client[db_name]
