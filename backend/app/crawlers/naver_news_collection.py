import requests
from config.loader import load_config
from urllib.parse import quote
from backend.app.db import mongoDB


# 뉴스 검색 함수
def fetch_naver_news(query, display=10):
    config = load_config()
    client_id = config["naver_API"]["client_id"]
    client_secret = config["naver_API"]["client_secret"]

    # 1. 네이버 API 인증 정보
    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret

    url = f"https://openapi.naver.com/v1/search/news.json?query={quote(query)}&display={display}"

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json()["items"]
        # return items
    else:
        print("Error:", response.status_code)
        # return []

    collection = mongoDB.db_connect()
    mongoDB.db_insert(collection, items)

# 4. MongoDB 저장 함수
# def save_urls_to_mongo(news_items):
#     for item in news_items:
#         document = {
#             "title": item["title"],
#             "link": item["link"],
#             "pubDate": item["pubDate"]
#         }
#         if collection.count_documents({"link": item["link"]}, limit=1) == 0:
#             collection.insert_one(document)
#             print(f"저장됨: {item['link']}")
#         else:
#             print(f"이미 있음: {item['link']}")

# 5. 실행
if __name__ == "__main__":
    search_query = "삼성전자"  # 검색 키워드
    news_results = fetch_naver_news(search_query, display=100)
    # save_urls_to_mongo(news_results)
