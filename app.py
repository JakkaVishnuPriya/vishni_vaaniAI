import time
import streamlit as st
from src.config import get_settings
from src.paper_loader import ensure_papers
from src.document_parser import parse_papers
from src.stair_retriever import StairRetriever
from src.vector_retriever import VectorRetriever
from src.pipeline import answer_question

st.set_page_config(page_title="The Relay", page_icon="📚", layout="wide")
st.title("📚 The Relay")
st.caption("A research-paper assistant with structure-aware retrieval, citations, and latency tracking.")

with st.sidebar:
    st.header("Configuration")
    try:
        configured_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        configured_key = ""
    api_key = st.text_input("Groq API key", type="password", value=configured_key)
    model = st.text_input("Groq model", value="openai/gpt-oss-20b")
    retrieval_mode = st.selectbox("Retrieval strategy", [
        "STAIR-inspired hierarchy", "TF-IDF baseline", "BM25 keyword baseline"
    ])
    top_k = st.slider("Passages to retrieve", 1, 8, 4)
    st.caption("For deployment, add GROQ_API_KEY in Streamlit Cloud → Settings → Secrets.")

@st.cache_resource(show_spinner="Loading the three required research papers...")
def load_corpus():
    settings = get_settings()
    paths = ensure_papers(settings.paper_dir)
    docs = parse_papers(paths)
    return docs

try:
    documents = load_corpus()
    st.success(f"Research library ready: {len(documents)} papers.")
except Exception as exc:
    st.error(f"Could not prepare the paper library: {exc}")
    st.info("Check internet access and the arXiv PDF URLs, then restart the app.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Retrieved evidence"):
                for item in msg["sources"]:
                    st.markdown(f"**{item['paper']} — {item['section']} (PDF page {item['page']})**")
                    st.write(item["text"])

question = st.chat_input("Ask a question answerable from the three research papers...")
if question:
    if not api_key:
        st.warning("Enter your Groq API key in the sidebar or configure GROQ_API_KEY in Streamlit Secrets.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        status = st.status("Retrieving evidence and generating a cited answer...", expanded=True)
        try:
            start = time.perf_counter()
            if retrieval_mode == "STAIR-inspired hierarchy":
                retriever = StairRetriever(documents)
            else:
                retriever = VectorRetriever(documents, mode="keyword" if retrieval_mode == "BM25 keyword baseline" else "vector")
            result = answer_question(
                question=question,
                retriever=retriever,
                api_key=api_key,
                model=model,
                top_k=top_k,
            )
            elapsed = (time.perf_counter() - start) * 1000
            status.update(label="Answer generated", state="complete")
            st.markdown(result["answer"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total latency", f"{elapsed:.0f} ms")
            c2.metric("Input tokens", result.get("tokens_in", "—"))
            c3.metric("Output tokens", result.get("tokens_out", "—"))
            with st.expander("Retrieved evidence", expanded=True):
                for item in result["sources"]:
                    st.markdown(f"**{item['paper']} — {item['section']} (PDF page {item['page']})**")
                    st.write(item["text"])
            st.session_state.messages.append({
                "role": "assistant", "content": result["answer"], "sources": result["sources"]
            })
        except Exception as exc:
            status.update(label="Request failed", state="error")
            st.error(str(exc))

with st.sidebar:
    st.divider()
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()
