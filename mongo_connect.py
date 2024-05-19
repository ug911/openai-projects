from pymongo.mongo_client import MongoClient
from datetime import datetime
from bson import ObjectId
import yaml


class MongoConnect:
    def __init__(self):
        with open("configs/config.yaml", "r") as f:
            cx = yaml.safe_load(f)
        self.uri = "mongodb+srv://{uname}:{pwd}@{mongo_host}/?retryWrites=true&w=majority&appName=Cluster1".format(
            uname=cx['mongo']['username'],
            pwd=cx['mongo']['password'],
            mongo_host=cx['mongo']['host']
        )
        self.client = MongoClient(self.uri)
        try:
            self.client.admin.command('ping')
        except Exception as e:
            print(e)
        self.db = self.client[cx['mongo']['database']]
        self.collection = self.db[cx['mongo']['collection']]
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
