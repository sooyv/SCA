import requests
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


if __name__ == "__main__":
    crawl_news_urls()