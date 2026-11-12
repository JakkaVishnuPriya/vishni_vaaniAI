from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.chunking import split_passages

class StairRetriever:
    """
    STAIR-inspired hierarchical retrieval, not the original trained STAIR/DSI model.
    Stage 1: rank paper sections from their headings + sampled content.
    Stage 2: rank passages only inside the best sections.
    """
    def __init__(self, records: list[dict]):
        self.passages = split_passages(records, max_words=180, overlap=35)
        grouped = defaultdict(list)
        for p in self.passages:
            grouped[(p["paper"], p["section"])].append(p)
        self.sections = []
        for (paper, section), items in grouped.items():
            preview = " ".join(x["text"][:500] for x in items[:3])
            self.sections.append({
                "paper": paper, "section": section, "passages": items,
                "description": f"{paper}. {section}. {preview}"
            })
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        self.section_matrix = self.vectorizer.fit_transform([s["description"] for s in self.sections])

    def retrieve(self, query: str, top_k: int = 4) -> list[dict]:
        q = self.vectorizer.transform([query])
        section_scores = cosine_similarity(q, self.section_matrix).ravel()
        section_count = min(3, len(self.sections))
        chosen = np.argsort(section_scores)[::-1][:section_count]
        candidates = []
        for idx in chosen:
            section = self.sections[idx]
            texts = [p["text"] for p in section["passages"]]
            local_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            matrix = local_vectorizer.fit_transform(texts)
            passage_scores = cosine_similarity(local_vectorizer.transform([query]), matrix).ravel()
            for pidx in np.argsort(passage_scores)[::-1][:top_k]:
                p = section["passages"][pidx]
                candidates.append({**p, "score": float(passage_scores[pidx] + section_scores[idx])})
        candidates.sort(key=lambda x: x["score"], reverse=True)
        seen, output = set(), []
        for item in candidates:
            key = (item["paper"], item["page"], item["text"])
            if key not in seen:
                seen.add(key)
                output.append(item)
            if len(output) >= top_k:
                break
        return output
