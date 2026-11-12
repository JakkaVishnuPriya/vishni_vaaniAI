from src.chunking import split_passages

def test_split_passages_preserves_metadata():
    docs = [{"paper": "P", "section": "1 Intro", "heading": "1 Intro",
             "page": 2, "text": " ".join(["word"] * 250)}]
    chunks = split_passages(docs, max_words=100, overlap=20)
    assert len(chunks) >= 2
    assert all(c["paper"] == "P" and c["page"] == 2 for c in chunks)
