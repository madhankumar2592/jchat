from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .domain import ChatAnswer, ChatMessage, DocumentChunk
from .ports import ChatModel, Memory, Retriever


@dataclass(slots=True)
class ChatApplication:
    model: ChatModel
    retriever: Retriever
    memory: Memory
    memory_turns: int = 8

    def ingest(self, document_name: str, pages: list[str], chunk_size: int, overlap: int) -> int:
        chunks: list[DocumentChunk] = []
        for page_number, page_text in enumerate(pages, start=1):
            text = " ".join(page_text.split())
            if not text:
                continue
            step = max(1, chunk_size - overlap)
            for offset in range(0, len(text), step):
                piece = text[offset : offset + chunk_size].strip()
                if piece:
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{document_name}:{page_number}:{offset}",
                            document_name=document_name,
                            page_number=page_number,
                            text=piece,
                        )
                    )
        self.retriever.add(chunks)
        return len(chunks)

    def ask(self, session_id: str, question: str, limit: int) -> ChatAnswer:
        history = self.memory.get(session_id, self.memory_turns)
        sources = self.retriever.search(question, limit)
        user_message = ChatMessage("user", question)
        answer = self.model.answer([*history, user_message], sources)
        self.memory.append(session_id, user_message)
        self.memory.append(session_id, ChatMessage("assistant", answer))
        return ChatAnswer(answer, tuple(sources))

