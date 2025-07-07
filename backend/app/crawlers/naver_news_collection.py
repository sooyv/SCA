import requests
from config.loader import load_config
from urllib.parse import quote
from backend.app.db import mongoDB
from bs4 import BeautifulSoup


def get_urls():
    collection = mongoDB.db_connect()
    return collection.find({}, {"_id": 1, "link": 1})


def crawl_news_urls():
    for item in get_urls():
        _id = item["_id"]
        url = item.get("link")
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            print(soup)
            # 기사제목
            # title = soup.select_one("h2#title_area").text

            #언론사
            press_tag = soup.select_one("span.media_end_head_top_logo_text").text

            # 본문
            content_tag = soup.select_one("article#dic_area")
            content = content_tag.get_text(separator="\n")
            content = content.replace('\xa0', ' ')  # &nbsp; 처리
            content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())

            update_fields = {"press": press_tag, "content": content}

            # 크롤링 데이터 추가 - 업데이트
            mongoDB.db_update(_id, update_fields)

        except requests.exceptions.RequestException as e:
            print(e)



# 뉴스 API 호출 및 mongoDB 저장
def fetch_naver_news(keyword, display=10):
    # API 인증 정보가 담긴 yaml 파일 load
    config = load_config()
    client_id = config["naver_API"]["client_id"]
    client_secret = config["naver_API"]["client_secret"]

    # 네이버 API 인증 정보
    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret
    # API header
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    collection = mongoDB.db_connect() # mongoDB 연결
    encoded_keyword = quote(keyword) # 수집 키워드
    # total_collected = 0 # 총 수집 개수
    all_items = []
    for start in range(1, 1001, 100):  # 시작 페이지 1 ~ 901(100씩 증가, 총 10회)
        url = (
            f"https://openapi.naver.com/v1/search/news.json"
            f"?query={encoded_keyword}&display=100&start={start}&sort=date"
        )
        # 네이버 API 호출
        response = requests.get(url, headers=headers)
        # 응답 정상(200)
        if response.status_code == 200:
            items = response.json().get("items", [])
            if not items:
                print(f"[{start}] 더 이상 뉴스가 없습니다.")
                break
            all_items.extend(items) # 전체 수집 데이터
            # total_collected += len(items)
            # print(f"[{start}] {len(items)}개 수집 완료 (총 {total_collected})")
        else:
            print("Error:", response.status_code)
            break

    if all_items:
        mongoDB.db_insert(collection, all_items, keyword) # mongoDB에 데이터 저장
    else:
        print("저장할 뉴스가 없습니다.")


# 실행
if __name__ == "__main__":
    search_keyword = "삼성전자"  # 검색 키워드
    # news_results = fetch_naver_news(search_keyword, display=100)
    crawl_news_urls()