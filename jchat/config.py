from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JChatSettings:
    provider: str = "mock"
    aws_region: str = "us-west-2"
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    max_results: int = 5
    chunk_size: int = 900
    chunk_overlap: int = 120
    memory_turns: int = 8

    @classmethod
    def from_env(cls) -> "JChatSettings":
        return cls(
            provider=os.getenv("JCHAT_PROVIDER", cls.provider).lower(),
            aws_region=os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", cls.aws_region)),
            bedrock_model_id=os.getenv("JCHAT_BEDROCK_MODEL_ID", cls.bedrock_model_id),
            max_results=int(os.getenv("JCHAT_MAX_RESULTS", cls.max_results)),
            chunk_size=int(os.getenv("JCHAT_CHUNK_SIZE", cls.chunk_size)),
            chunk_overlap=int(os.getenv("JCHAT_CHUNK_OVERLAP", cls.chunk_overlap)),
            memory_turns=int(os.getenv("JCHAT_MEMORY_TURNS", cls.memory_turns)),
        )

