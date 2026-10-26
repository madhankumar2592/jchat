from __future__ import annotations

import hashlib
import math
import re
from collections import defaultdict
from collections.abc import Sequence

from .domain import ChatMessage, DocumentChunk, RetrievedChunk


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]{2,}", text.lower())


class InMemoryRetriever:
    """Dependency-free lexical vector store for the POC.

    Replace this adapter with OpenSearch Serverless or Milvus without changing
    the application service or Streamlit UI.
    """

    def __init__(self, dimensions: int = 512):
        self.dimensions = dimensions
        self._items: list[tuple[DocumentChunk, dict[int, float], float]] = []

    def _vector(self, text: str) -> dict[int, float]:
        counts: dict[int, float] = defaultdict(float)
        for token in _tokens(text):
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            index = int.from_bytes(digest, "big") % self.dimensions
            counts[index] += 1.0
        norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
        return {index: value / norm for index, value in counts.items()}

    @staticmethod
    def _cosine(left: dict[int, float], right: dict[int, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(index, 0.0) for index, value in left.items())

    def add(self, chunks: Sequence[DocumentChunk]) -> None:
        self._items.extend((chunk, vector, norm) for chunk, vector, norm in ((c, self._vector(c.text), 1.0) for c in chunks))

    def search(self, query: str, limit: int) -> list[RetrievedChunk]:
        query_vector = self._vector(query)
        ranked = sorted(
            ((self._cosine(query_vector, vector), chunk) for chunk, vector, _ in self._items),
            key=lambda pair: pair[0],
            reverse=True,
        )
        return [RetrievedChunk(chunk, score) for score, chunk in ranked[:limit] if score > 0]

    def clear(self) -> None:
        self._items.clear()

    def count(self) -> int:
        return len(self._items)


class InMemoryConversationMemory:
    def __init__(self):
        self._messages: dict[str, list[ChatMessage]] = defaultdict(list)

    def get(self, session_id: str, limit: int) -> list[ChatMessage]:
        return self._messages[session_id][-limit:]

    def append(self, session_id: str, message: ChatMessage) -> None:
        self._messages[session_id].append(message)

    def clear(self, session_id: str) -> None:
        self._messages.pop(session_id, None)


class MockChatModel:
    """Deterministic provider for UI demos and local development."""

    def answer(self, messages: Sequence[ChatMessage], context: Sequence[RetrievedChunk]) -> str:
        question = messages[-1].content if messages else "your question"
        if not context:
            return (
                f"[Mock mode] I received: “{question}”. Upload a jewelry PDF and I’ll ground "
                "the answer in its product details."
            )
        references = ", ".join(
            f"{item.chunk.document_name} p.{item.chunk.page_number}" for item in context[:3]
        )
        excerpt = context[0].chunk.text[:240].rstrip()
        return (
            f"[Mock mode] For “{question}”, the most relevant product information is: "
            f"{excerpt}…\n\nSources: {references}"
        )

