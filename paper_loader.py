from pathlib import Path
import httpx

PAPERS = {
    "Attention Is All You Need": "https://arxiv.org/pdf/1706.03762v7",
    "Moshi: a speech-text foundation model for real-time dialogue": "https://arxiv.org/pdf/2410.00037v1",
    "Dynamic Chunking for End-to-End Hierarchical Sequence Modeling": "https://arxiv.org/pdf/2507.07955v2",
}

def ensure_papers(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    with httpx.Client(timeout=90, follow_redirects=True) as client:
        for title, url in PAPERS.items():
            slug = {
                "Attention Is All You Need": "attention_is_all_you_need_v7.pdf",
                "Moshi: a speech-text foundation model for real-time dialogue": "moshi_v1.pdf",
                "Dynamic Chunking for End-to-End Hierarchical Sequence Modeling": "dynamic_chunking_v2.pdf",
            }[title]
            path = output_dir / slug
            if not path.exists() or path.stat().st_size < 10_000:
                response = client.get(url)
                response.raise_for_status()
                if not response.content.startswith(b"%PDF"):
                    raise RuntimeError(f"arXiv did not return a PDF for {title}")
                path.write_bytes(response.content)
            paths[title] = path
    return paths
