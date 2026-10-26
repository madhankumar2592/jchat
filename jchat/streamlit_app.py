from __future__ import annotations

import uuid

import streamlit as st

from jchat.adapters import InMemoryConversationMemory, InMemoryRetriever, MockChatModel
from jchat.application import ChatApplication
from jchat.bedrock import BedrockChatModel
from jchat.config import JChatSettings
from jchat.documents import read_pdf


st.set_page_config(page_title="jChat · Jewelry Product Assistant", page_icon="💎", layout="wide")
settings = JChatSettings.from_env()


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
st.title("Jewelry Product Assistant")
st.write("Ask about materials, dimensions, care instructions, variants, or certifications in your PDFs.")
st.caption(f"Indexed chunks: {app.retriever.count()} · Provider: {provider.upper()} · Model: {model_id}")

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

