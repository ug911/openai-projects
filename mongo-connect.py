from pymongo.mongo_client import MongoClient
from datetime import datetime
from bson import ObjectId
import yaml


class MongoConnect:
    def __init__(self):
        with open("configs/config.yaml", "r") as f:
            cx = yaml.safe_load(f)
        self.uri = "mongodb+srv://utkgupta:LkIYOetsRhtfpEjE@cluster1.jfg2evg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"
        self.uri = "mongodb+srv://{uname}:{pwd}@{mongo_host}/?retryWrites=true&w=majority&appName=Cluster1".format(
            uname=cx['mongo_username'],
            pwd=cx['mongo_password'],
            mongo_host=cx['mongo_host']
        )
        self.client = MongoClient(self.uri)
        try:
            self.client.admin.command('ping')
        except Exception as e:
            print(e)
        self.db = self.client["openai-projects"]
        self.collection = self.db["interview-bot-chats"]
        self.object_id = None

    def create_new(self):
        new_data = {
            "createdat": datetime.now(),
            "updatedat": datetime.now()
        }
        x = self.collection.insert_one(new_data)
        self.object_id = str(x.inserted_id)
        return self.object_id

    def update(self, update_dict):
        filter_query = {"_id": ObjectId(self.object_id)}
        self.collection.update_one(filter_query, update_dict)
