import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup


def main():
    # 크롬드라이버 경로 지정 (본인 환경에 맞게 수정)
    driver_path = r'/data/chromedriver-win64/chromedriver.exe'  # 또는 절대 경로

    # 검색어: "AI"로 Naver 뉴스 검색 결과 URL 구성
    query = 'AI'
    url = f'https://search.naver.com/search.naver?where=news&query={query}'

    # Selenium으로 페이지 요청
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 창을 띄우지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(2)  # 페이지 로딩 대기

    # 페이지 소스 가져오기
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 뉴스 기사 정보 파싱
    news_items = soup.select('div.sds-comps-vertical-layout sds-comps-full-layout J99id_FmVoUQSFiLEpbw')  # 뉴스 영역 선택자
    for item in news_items:
        title_tag = item.select_one('a.news_tit')
        if title_tag:
            title = title_tag.text
            link = title_tag['href']
            print(f'제목: {title}')
            print(f'링크: {link}')
            print('-' * 50)

    driver.quit()


# def main():
#     print('소영이랑 저녁밥 먹기')


if __name__ == "__main__":
    main()