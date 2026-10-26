from __future__ import annotations

from collections.abc import Sequence

import boto3

from .domain import ChatMessage, RetrievedChunk


class BedrockChatModel:
    def __init__(self, region_name: str, model_id: str):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    def answer(self, messages: Sequence[ChatMessage], context: Sequence[RetrievedChunk]) -> str:
        context_text = "\n\n".join(
            f"[{item.chunk.document_name}, page {item.chunk.page_number}]\n{item.chunk.text}"
            for item in context
        )
        system = (
            "You are JChat, a jewelry product specialist. Answer only from the supplied document "
            "context when the question concerns product facts. If the context is insufficient, say "
            "that clearly. Do not invent specifications, prices, certifications, or availability. "
            "Keep answers concise and cite source document names and page numbers."
        )
        payload_messages = [
            {"role": message.role, "content": [{"text": message.content}]} for message in messages
        ]
        payload_messages[-1]["content"][0]["text"] = (
            f"Document context:\n{context_text or '(no matching document context)'}\n\n"
            f"User question:\n{payload_messages[-1]['content'][0]['text']}"
        )
        response = self.client.converse(
            modelId=self.model_id,
            system=[{"text": system}],
            messages=payload_messages,
            inferenceConfig={"maxTokens": 700, "temperature": 0.1, "topP": 0.9},
        )
        return response["output"]["message"]["content"][0]["text"].strip()

