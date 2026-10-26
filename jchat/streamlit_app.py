from __future__ import annotations

import uuid
import sys
from pathlib import Path

import streamlit as st

# Streamlit can execute this file by absolute path (with a different working
# directory). Add the repository root so the ``jchat`` package remains importable.
PACKAGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = PACKAGE_ROOT.parent
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from jchat.adapters import InMemoryConversationMemory, InMemoryRetriever, MockChatModel
from jchat.application import ChatApplication
from jchat.bedrock import BedrockChatModel
from jchat.config import JChatSettings
from jchat.documents import read_pdf


st.set_page_config(page_title="jChat · Jewelry Product Assistant", page_icon="💎", layout="wide")
settings = JChatSettings.from_env()

st.markdown(
    """
    <style>
    :root {
        --navy: #081a33;
        --navy-soft: #102b4d;
        --red: #d44747;
        --green: #20a36a;
        --ink: #172235;
        --muted: #667085;
        --line: #dfe6ef;
    }
    .stApp { background: #f5f7fb; color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(245,247,251,.9); }
    [data-testid="stSidebar"] { background: var(--navy); border-right: 1px solid #1e3b60; }
    [data-testid="stSidebar"] * { color: #eef5ff !important; }
    [data-testid="stSidebar"] .stCaption { color: #a9bfd8 !important; }
    .brand { display:flex; align-items:center; gap:.8rem; margin: .4rem 0 1.4rem; }
    .brand-mark { width:42px; height:42px; border-radius:12px; display:grid; place-items:center;
        background: linear-gradient(135deg, var(--red), #f18a55); color:white; font-size:22px;
        box-shadow: 0 8px 20px rgba(212,71,71,.28); }
    .brand h1 { margin:0; color:white; font-size:1.5rem; letter-spacing:.02em; }
    .brand p { margin:.15rem 0 0; color:#a9bfd8; font-size:.75rem; }
    .hero { background: linear-gradient(110deg, var(--navy), var(--navy-soft)); border-radius:18px;
        padding:1.35rem 1.6rem; color:white; margin: .4rem 0 1.2rem;
        box-shadow: 0 10px 28px rgba(8,26,51,.16); border-left: 5px solid var(--red); }
    .hero h2 { margin:0; font-size:1.8rem; }
    .hero p { margin:.35rem 0 0; color:#c2d2e5; }
    [data-testid="stChatMessage"] { border:1px solid var(--line); border-radius:14px; padding:.65rem .8rem; background:white; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { border-left:4px solid var(--red); }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) { border-left:4px solid var(--green); }
    [data-testid="stChatInput"] { border-color: var(--navy-soft); }
    .stButton > button { border-radius:9px; border:1px solid var(--navy-soft); font-weight:600; }
    .stButton > button:hover { border-color: var(--red); color: var(--red); }
    [data-testid="stMetric"] { background:white; border:1px solid var(--line); border-radius:12px; padding:.7rem; }
    footer { visibility:hidden; }
    </style>
    <div class="brand"><div class="brand-mark">💎</div><div><h1>jChat</h1><p>Enterprise jewelry intelligence</p></div></div>
    <div class="hero"><h2>Jewelry Product Assistant</h2><p>Search your product catalog and get grounded answers from your documents.</p></div>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def build_application(provider: str, region: str, model_id: str, memory_turns: int) -> ChatApplication:
    model = MockChatModel() if provider == "mock" else BedrockChatModel(region, model_id)
    return ChatApplication(
        model=model,
        retriever=InMemoryRetriever(),
        memory=InMemoryConversationMemory(),
        memory_turns=memory_turns,
    )


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat" not in st.session_state:
    st.session_state.chat = []

with st.sidebar:
    st.title("jChat")
    st.caption("AWS Bedrock · PDF RAG · jewelry catalog")
    provider = st.selectbox("Chat provider", ["mock", "aws"], index=0 if settings.provider == "mock" else 1)
    region = st.text_input("AWS Region", settings.aws_region)
    model_id = st.text_input("Bedrock model ID", settings.bedrock_model_id)
    if st.button("Clear conversation"):
        st.session_state.chat = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    st.divider()
    uploads = st.file_uploader("Add product PDFs", type=["pdf"], accept_multiple_files=True)

app = build_application(provider, region, model_id, settings.memory_turns)
st.caption(f"Ask about materials, dimensions, care instructions, variants, or certifications · {app.retriever.count()} indexed chunks · {provider.upper()} provider")

if uploads:
    for upload in uploads:
        marker = f"indexed:{upload.name}:{upload.size}"
        if marker not in st.session_state:
            count = app.ingest(upload.name, read_pdf(upload.getvalue()), settings.chunk_size, settings.chunk_overlap)
            st.session_state[marker] = count
            st.success(f"Indexed {count} chunks from {upload.name}")

for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.write(f"{source['document']} · page {source['page']} · score {source['score']:.2f}")

question = st.chat_input("Ask about your jewelry products")
if question:
    st.session_state.chat.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    try:
        with st.chat_message("assistant"):
            with st.spinner("Searching product documents and asking Bedrock…"):
                answer = app.ask(st.session_state.session_id, question, settings.max_results)
            st.markdown(answer.text)
            source_data = [
                {"document": item.chunk.document_name, "page": item.chunk.page_number, "score": item.score}
                for item in answer.sources
            ]
            with st.expander("Sources"):
                for source in source_data:
                    st.write(f"{source['document']} · page {source['page']} · score {source['score']:.2f}")
            st.session_state.chat.append({"role": "assistant", "content": answer.text, "sources": source_data})
    except Exception as exc:
        st.error(f"JChat could not answer: {type(exc).__name__}: {exc}")

