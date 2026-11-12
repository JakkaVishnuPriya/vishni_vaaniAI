from src.groq_client import GroqModel
from src.verifier import validate_citations

SYSTEM = """You are The Relay, a research assistant restricted to the supplied paper excerpts.
Answer only using the excerpts. Do not use outside knowledge or memory.
If the excerpts do not establish the answer, say that the supplied papers do not provide enough information.
Cite every substantive factual claim using [1], [2], etc., matching the numbered excerpts.
Do not invent section names, page numbers, quotations, or experimental results.
Be concise but technically clear."""

def answer_question(question: str, retriever, api_key: str, model: str, top_k: int = 4) -> dict:
    sources = retriever.retrieve(question, top_k=top_k)
    if not sources:
        return {
            "answer": "I could not find relevant supporting passages in the three-paper library, so I cannot answer this reliably.",
            "sources": [], "tokens_in": 0, "tokens_out": 0,
        }
    evidence = []
    for i, item in enumerate(sources, 1):
        evidence.append(
            f"[{i}] Paper: {item['paper']}\nSection: {item['section']}\nPDF page: {item['page']}\nPassage: {item['text']}"
        )
    prompt = "QUESTION:\n" + question + "\n\nRETRIEVED EXCERPTS:\n" + "\n\n".join(evidence)
    client = GroqModel(api_key, model)
    result = client.complete([
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt},
    ])
    valid, issues = validate_citations(result["text"], sources)
    answer = result["text"]
    if not valid:
        answer += "\n\n**Citation check warning:** " + " ".join(issues)
    return {
        "answer": answer,
        "sources": sources,
        "tokens_in": result["tokens_in"],
        "tokens_out": result["tokens_out"],
        "model_latency_ms": result["elapsed_ms"],
    }
