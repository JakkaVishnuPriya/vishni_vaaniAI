import re

def split_passages(records: list[dict], max_words: int = 180, overlap: int = 35) -> list[dict]:
    passages = []
    for record in records:
        words = re.findall(r"\S+", record["text"])
        if not words:
            continue
        step = max(1, max_words - overlap)
        for start in range(0, len(words), step):
            piece = " ".join(words[start:start + max_words]).strip()
            if len(piece.split()) < 12:
                continue
            passages.append({**record, "text": piece, "passage_id": len(passages)})
            if start + max_words >= len(words):
                break
    return passages
