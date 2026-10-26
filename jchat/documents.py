from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


def read_pdf(data: bytes) -> list[str]:
    reader = PdfReader(BytesIO(data))
    return [page.extract_text() or "" for page in reader.pages]

