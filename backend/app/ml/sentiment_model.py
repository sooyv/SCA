from backend.app.db import mongoDB
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import pandas as pd
import config

class SentimentAnalyzer: # 감정 분석기
    # 감정 분석 예측 모델 load
    def __init__(self, model_name="nlp04/korean-sentiment-kobert"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

    def predict(self, text):
        if not text.strip():
            return -1, [0.0, 0.0, 0.0]
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=1).squeeze().tolist()
            label = torch.argmax(outputs.logits, dim=1).item()
        return label, probs

def load_mongo_data():
    collection = mongoDB.db_connect() # DB 연결(mongoDB)
    data = list(collection.find({}, {"_id": 0, "title": 1, "content": 1
                                     ,"keyword": 1, "pubDate": 1, "link": 1}))  # raw data 불러오기
    return pd.DataFrame(data) # dataFrame 으로 변환


def main():
    df = load_mongo_data()
    df["text"] = (df["title"] + " " + df["content"])

    analyzer = SentimentAnalyzer()
    df["sentiment_label"], df["sentiment_score"] = zip(*df["text"].apply(analyzer.predict))


if __name__ == "__main__":
    main()