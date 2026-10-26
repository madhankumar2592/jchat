from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    chunk_id: str
    document_name: str
    page_number: int
    text: str


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class ChatAnswer:
    text: str
    sources: tuple[RetrievedChunk, ...]

