"""Retrieval smoke test; extend with manually annotated gold passages and timing."""
import json
from src.paper_loader import ensure_papers
from src.document_parser import parse_papers
from src.stair_retriever import StairRetriever
from src.vector_retriever import VectorRetriever

QUERIES = [
    "How does multi-head attention work?",
    "How does the model support real-time speech dialogue?",
    "What is dynamic chunking and why is it useful?",
]

def main():
    docs = parse_papers(ensure_papers(__import__("pathlib").Path("data/papers")))
    retrievers = {
        "keyword": VectorRetriever(docs, mode="keyword"),
        "vector_tfidf": VectorRetriever(docs, mode="vector"),
        "stair_inspired": StairRetriever(docs),
    }
    rows = []
    for q in QUERIES:
        for name, retriever in retrievers.items():
            rows.append({"query": q, "setting": name,
                         "results": retriever.retrieve(q, top_k=4)})
    with open("results/retrieval_smoke.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print("Wrote results/retrieval_smoke.json. Manually grade evidence before reporting quality.")

if __name__ == "__main__":
    main()
