"""Streaming JSONL reader for candidate data."""

import orjson
from pathlib import Path


def stream_candidates(path: str | Path):
    with open(path, "rb") as f:
        for line in f:
            if line.strip():
                yield orjson.loads(line)


def load_all_candidates(path: str | Path) -> list[dict]:
    return list(stream_candidates(path))


def load_jd_text(path: str | Path) -> str:
    from docx import Document
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
