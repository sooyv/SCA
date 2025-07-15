import re
import requests
from backend.app.db import mongoDB
from bs4 import BeautifulSoup
from pymongo import UpdateOne


def get_urls():
    collection = mongoDB.db_connect()
    # return collection.find({}, {"_id": 1, "link": 1}) # mongoDB 전체 데이터 조회
    return collection.find({"content": {"$exists": False}}, {"_id": 1, "link": 1}) # mongoDB content 필드 없는 데이터만 조회

# 뉴스 본문 전처리(정규표현식)
def preprocess_content(text):
    # HTML 태그 및 엔티티 제거
    text = re.sub(r'<[^>]+>|&[a-z]+;', '', text)
    # 이메일 주소 제거
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
    # URL 제거
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # 기자 및 촬영/편집 정보 제거 ([영상취재 구본은] 등)
    text = re.sub(r'\[\s*(영상)?(취재|편집|기자)\s*[^\]]+?\]', '', text)
    # 해시태그 제거 (#환율 #코스피 등)
    text = re.sub(r'#\S+\s*', '', text)
    # 특정 언론사 기사문의 및 제보 정보 제거 (연합뉴스TV 등)
    text = re.sub(r'연합뉴스TV 기사문의 및 제보\s*:\s*(카톡|라인)\s*jebo23', '', text)
    # 괄호 안의 불필요한 섹션 제거 ((서울=연합뉴스), (사진=...) 등)
    text = re.sub(r'\([가-힣\s=]+[가-힣]+뉴스\s*\)|\([가-힣\s=]+\s*제공\s*\)|\([가-힣\s=]+\s*자료\s*\)|\(사진=\S+\)|\[사진=\S+\]|\(끝\)',
                  '', text)
    text = re.sub(r'\[\s*(사진|자료|도표|연합뉴스)\s*.*?\]', '', text)
    # 한글, 영어, 숫자, 기본 문장 부호(., ?!) 외 특수 문자 제거
    text = re.sub(r'[^가-힣a-zA-Z0-9.,?!]', ' ', text)
    # 연속된 공백을 단일 공백으로 치환
    text = re.sub(r'\s+', ' ', text)

    # 양쪽 끝 공백 제거
    text = text.strip()

    return text.strip()


def crawl_news_urls():
    updates = [] # document list
    for item in get_urls():
        _id = item["_id"]
        url = item.get("link")
        try:
            response = requests.get(url) # 기사 URL로 요청
            soup = BeautifulSoup(response.text, "html.parser") # HTML 파싱
            # 기사 제목
            # title = soup.select_one("h2#title_area").text
            # 언론사
            press_tag = soup.select_one("span.media_end_head_top_logo_text").text.strip()

            # 본문
            content_tag = soup.select_one("article#dic_area")
            if press_tag and content_tag:
                content = content_tag.get_text(separator="\n")
                content = content.replace('\xa0', ' ')  # &nbsp; 처리
                content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
                content = preprocess_content(content)

                updates.append(UpdateOne(
                    {"_id": _id},
                    {"$set": {"press": press_tag, "content": content}}
                ))

        except requests.exceptions.RequestException as e:
            print(e)
    # 수집 데이터 일괄 업데이트
    updated_count = mongoDB.db_bulk_update(updates)
    print(f"{updated_count} documents updated.")

if __name__ == "__main__":
    crawl_news_urls()