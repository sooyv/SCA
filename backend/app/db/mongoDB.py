from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from config.loader import load_config


# mongoDB 연결
def db_connect():
    try:
        config = load_config()
        mongodb_uri = config["mongodb"]["uri"]
        # MongoDB 서버
        cluster = config["mongodb"]["cluster"]
        # MongoDB 데이터베이스
        db_name = config["mongodb"]["db_name"]
        # MongoDB 컬렉션(테이블)
        collection_name = config["mongodb"]["collection"]

        # MongoDB 연결
        mongo_client = MongoClient(mongodb_uri)
        mongo_client.server_info()
        db = mongo_client[db_name]
        collection = db[collection_name]

        return collection
    except ServerSelectionTimeoutError as e:
        print("❌ MongoDB 서버에 연결할 수 없습니다.")
        print(e)
        return None


# mongoDB에 raw data insert(제목, URL, 게시글 등록 날짜)
def db_insert(collection, news_items):
    for item in news_items:
        document = {
            "title": item["title"],
            "link": item["link"],
            "pubDate": item["pubDate"]
        }
        # documents(데이터) 중복 제거
        if collection.count_documents({"link": item["link"]}, limit=1) == 0:
            collection.insert_one(document)
            print(f"저장됨: {item['link']}")
        else:
            print(f"이미 있음: {item['link']}")