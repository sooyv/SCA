import yaml
from pymongo import MongoClient


def db_connect():
    with open(r"/config/application.yaml", "r") as file:
        config = yaml.safe_load(file)
        mongodb_uri = config["mongodb"]["uri"]
        cluster = config["mongodb"]["cluster"]
        db_name = config["mongodb"]["db_name"]
        collection_name = config["mongodb"]["collection"]

    # MongoDB Atlas 연결
    ATLAS_URI = mongodb_uri
    DB_NAME = db_name
    COLLECTION_NAME = collection_name

    mongo_client = MongoClient(ATLAS_URI)
    db = mongo_client[DB_NAME]
    collection = db[COLLECTION_NAME]


def db_insert(collection, news_items):
    for item in news_items:
        document = {
            "title": item["title"],
            "link": item["link"],
            "pubDate": item["pubDate"]
        }
        if collection.count_documents({"link": item["link"]}, limit=1) == 0:
            collection.insert_one(document)
            print(f"저장됨: {item['link']}")
        else:
            print(f"이미 있음: {item['link']}")