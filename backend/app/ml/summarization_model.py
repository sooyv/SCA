import pymongo
import psycopg2
import pandas as pd
from backend.app.db import mongoDB
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

# AI model 불러오기
class SummarizerModel:
    def __init__(self):
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained("digit82/kobart-summarization")
        self.model = BartForConditionalGeneration.from_pretrained("digit82/kobart-summarization")

    def summarize(self, text): # 뉴스 기사 요약
        inputs = self.tokenizer([text], return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = self.model.generate(inputs["input_ids"], max_length=128, num_beams=4, early_stopping=True)
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)


# mongoDB 데이터 꺼내오기
def load_mongo_data():
    collection = mongoDB.db_connect() # DB 연결(mongoDB)
    data = list(
        collection.find(
            {},  # 조건 없이 전체에서
            {"_id": 1, "title": 1, "content": 1, "keyword": 1, "pubDate": 1, "link": 1}  # 필드 지정
        )
        .sort("pubDate", -1)  # pubDate 기준 내림차순 (최신순)
        .limit(10)  # 상위 10개만 가져오기
    )
    # data = list(collection.find({}, {"_id": '687f45024f646a235ae0ba67', "title": 1, "content": 1
    #                                  ,"keyword": 1, "pubDate": 1, "link": 1}))  # raw data 불러오기
    return pd.DataFrame(data) # dataFrame 으로 변환


def main():
    df = load_mongo_data()
    df["full_text"] = df["title"].fillna("") + " " + df["content"].fillna("")
    summarizer = SummarizerModel()
    df["summary"] = df["full_text"].apply(summarizer.summarize)
    print(df['summary'])

if __name__ == "__main__":
    main()