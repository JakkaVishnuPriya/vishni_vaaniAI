# The Relay

A Python + Streamlit research assistant for the three papers specified in The Relay assignment.

## Retrieval design

This repository includes three experimental retrieval paths:

1. **Keyword baseline** — BM25 over passage text.
2. **TF-IDF baseline** — unigram/bigram TF-IDF vectors with cosine similarity.
3. **STAIR-inspired hierarchy** — a lightweight adaptation that first ranks document sections using section titles and descriptions, then ranks passages inside selected sections.

This is **not a reproduction of the original STAIR model**. The original paper describes a Table-of-Contents-augmented generative retriever trained with a Differentiable Search Index. This project uses explicit hierarchical routing because it has only three papers and no trained DSI checkpoint.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-key"
```

Then run:

```bash
streamlit run app.py
```

Alternatively, enter the key in the app sidebar.

## Papers

The downloader uses these exact versions:

- https://arxiv.org/pdf/1706.03762v7
- https://arxiv.org/pdf/2410.00037v1
- https://arxiv.org/pdf/2507.07955v2

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a Streamlit Community Cloud app pointing to `app.py`.
3. In app Settings → Secrets, add `GROQ_API_KEY = "..."`.
4. Deploy.

Do not commit API keys, local secrets, or raw experiment results containing private information.

## Important assignment work still required

The interactive app is the demonstration interface, not the complete experiment harness. Before submission, run the real-service calibration, stand-in load tests, at least three retrieval configurations, and the 15+ question quality evaluation. Populate `results.csv` only with measured request records. Never invent measurements.

See `experiments/` for the initial experiment scripts and extend them as you calibrate the stand-in.
