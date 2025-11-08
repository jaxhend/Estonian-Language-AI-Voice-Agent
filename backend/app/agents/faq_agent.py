from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, List, Optional, Tuple

from ..services import ranker, llm_client

_LOGGER = logging.getLogger(__name__)

# Prefer a top-level faq.json (project-level) if present; otherwise use packaged data/faq.json
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[2]  # backend/
_PREFERRED_FAQ = _PROJECT_ROOT / "faq.json"
_PACKAGED_FAQ = _THIS_FILE.parents[1] / "data" / "faq.json"  # app/data/faq.json

_FAQ_PATHS = [_PREFERRED_FAQ, _PACKAGED_FAQ]
_DEFAULT_NO_ANSWER = "Vabandust, vastust ei leidnud."


def _load_faq() -> Tuple[List[dict], List[str]]:
    """Load FAQ file from preferred locations and return (faq_entries, questions_list).

    Accepts either a top-level list or a dict with key 'faq' containing the list.
    """
    for p in _FAQ_PATHS:
        try:
            if not p.exists():
                continue
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Accept both { "faq": [...] } and [...]
                if isinstance(data, dict) and "faq" in data and isinstance(data["faq"], list):
                    faq_list = data["faq"]
                elif isinstance(data, list):
                    faq_list = data
                else:
                    _LOGGER.warning("FAQ file %s has unexpected shape: %s", p, type(data))
                    continue

                questions = [entry.get("question") or entry.get("q") or "" for entry in faq_list]
                _LOGGER.info("Loaded FAQ from %s with %d entries", p, len(faq_list))
                return faq_list, questions
        except Exception:
            _LOGGER.exception("Failed to load FAQ from %s", p)
    _LOGGER.warning("No FAQ file found in preferred locations: %s", _FAQ_PATHS)
    return [], []


FAQ, QUESTIONS = _load_faq()


def reload_faq() -> None:
    """Reload the FAQ file into memory (useful during development)."""
    global FAQ, QUESTIONS
    FAQ, QUESTIONS = _load_faq()
    _LOGGER.info("Reloaded FAQ: %d entries", len(FAQ))


def _normalize_llm_output(raw: Any) -> str:
    """Convert various LLM return shapes into a plain string."""
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, dict):
        # common shapes: {'text': '...'} or {'choices': [{'text': '...'}]}
        text = raw.get("text")
        if isinstance(text, str):
            return text.strip()
        choices = raw.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict) and isinstance(first.get("text"), str):
                return first.get("text").strip()
        # fallback to stringify
        try:
            return json.dumps(raw, ensure_ascii=False)
        except Exception:
            return str(raw)
    return str(raw)


async def _ask_llm_for_answer(prompt: str, max_tokens: int = 200) -> str:
    """Ask the LLM and normalize the output; returns a safe default on error."""
    try:
        raw = await llm_client.complete(prompt, max_tokens=max_tokens)
        ans = _normalize_llm_output(raw)
        return ans or _DEFAULT_NO_ANSWER
    except Exception as e:
        _LOGGER.exception("LLM completion failed: %s", e)
        return _DEFAULT_NO_ANSWER


async def answer(question: str) -> Tuple[str, Optional[str], float]:
    """Answer a user question using FAQ lookup + LLM augmentation.

    Returns a tuple: (answer_text, matched_question_or_None, score)
    - If a close FAQ match is found (score >= 0.6) the FAQ answer is returned
      possibly augmented by the LLM. matched_question is the FAQ question.
    - If no good match is found, the LLM is asked to generate a short answer
      and matched_question is None.
    """
    if not question or not question.strip():
        return "", None, 0.0

    try:
        match_q, score = ranker.best_match(question, QUESTIONS)
    except Exception as e:
        _LOGGER.exception("Ranker.best_match failed: %s", e)
        match_q, score = None, 0.0

    # If ranker didn't produce a meaningful match -> free-form LLM answer
    if not match_q or score < 0.6:
        prompt = f"Vasta lühidalt küsimusele Eesti keeles: {question}"
        ans = await _ask_llm_for_answer(prompt)
        return ans, None, score

    # Found a candidate FAQ entry
    # Note: the attached faq.json uses 'question' and 'answer' keys
    entry = next((x for x in FAQ if (x.get("question") or x.get("q")) == match_q), None)
    if not entry:
        _LOGGER.warning("Matched question not found in FAQ entries: %s", match_q)
        prompt = f"Vasta lühidalt küsimusele Eesti keeles: {question}"
        ans = await _ask_llm_for_answer(prompt)
        return ans, None, score

    base = entry.get("answer") or entry.get("a") or ""
    prompt = (
        "Täienda järgmist vastust, vajadusel kohanda stiili Eesti keeles.\n"
        f"Küsimus: {match_q}\nBaasvastus: {base}\nTäiendatud:"
    )
    final = await _ask_llm_for_answer(prompt)
    # If LLM returned the default (error) and base exists, prefer base
    if final == _DEFAULT_NO_ANSWER and base:
        return base, match_q, score
    return final, match_q, score
