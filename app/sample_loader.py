from __future__ import annotations

import json
from pathlib import Path

from app.models import SearchDocument


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_documents.json"


def load_sample_documents() -> list[SearchDocument]:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return [SearchDocument(**item) for item in data]
