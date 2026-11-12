from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from src.chunking import split_passages

class VectorRetriever:
    def __init__(self, records: list[dict], mode: str = "vector"):
        self.passages = split_passages(records)
        self.mode = mode
        self.texts = [p["text"] for p in self.passages]
        if mode == "keyword":
            self.bm25 = BM25Okapi([t.lower().split() for t in self.texts])
        else:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            self.matrix = self.vectorizer.fit_transform(self.texts)

    def retrieve(self, query: str, top_k: int = 4) -> list[dict]:
        if self.mode == "keyword":
            scores = self.bm25.get_scores(query.lower().split())
        else:
            q = self.vectorizer.transform([query])
            scores = cosine_similarity(q, self.matrix).ravel()
        ids = np.argsort(scores)[::-1][:top_k]
        return [{**self.passages[i], "score": float(scores[i])} for i in ids if scores[i] > 0]
