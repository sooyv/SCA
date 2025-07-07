import re
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from config.loader import load_config


# mongoDB 연결
def db_connect():
    try:
        # mongoDB 정보가 담긴 yaml load
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
        # mongoDB 서버 응답 테스트
        # mongo_client.server_info()
        db = mongo_client[db_name]
        collection = db[collection_name]

        return collection
    except ServerSelectionTimeoutError as e:
        print("❌ MongoDB 서버에 연결할 수 없습니다.")
        print(e)
        return None


# mongoDB에 raw data insert(제목, URL, 게시글 등록 날짜)
def db_insert(collection, news_items, keyword):
    # n.news.naver.com 도메인만 허용(뉴스들의 UI가 다르므로 네이버 뉴스만 수집)
    naver_domain_pattern = re.compile(r"^https://n\.news\.naver\.com/")
    count = 0 # 수집된 뉴스 카운트
    for item in news_items:
        document = {
            "title": item["title"], # 제목
            "link": item["link"], # 뉴스 URL
            "pubDate": item["pubDate"], # 뉴스 등록 시간
            "keyword": keyword, # 수집 키워드
        }
        if re.match(naver_domain_pattern, item["link"]):# 정규표현식으로 네이버 뉴스만 포함
            if collection.count_documents({"link": item["link"]}, limit=1) == 0: # documents(데이터) 중복 제거
                collection.insert_one(document)
                count += 1
                # print(f"저장 완료: {item['link']}")
            # else:
                # print(f"이미 있음: {item['link']}")
    print(count)



def db_update(_id, update_fields):
    collection = db_connect()
    collection.update_one({"_id": _id}, {"$set": update_fields})