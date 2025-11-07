# app/tts/chunker.py
import re
from typing import List

_SPLIT_RE = re.compile(r'(?<=[\.\!\?])\s+|, ')

def split_text(text: str) -> List[str]:
    """
    Split text into short clauses to reduce first-audio latency.
    Keeps punctuation-based boundaries and comma pauses.
    """
    parts = _SPLIT_RE.split(text or "")
    return [p.strip() for p in parts if p and p.strip()]