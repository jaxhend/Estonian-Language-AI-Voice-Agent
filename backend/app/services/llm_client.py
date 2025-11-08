import httpx
from . import logger
from ..core import config


async def complete(prompt: str, max_tokens: int = 512) -> str:
    url = config.LLM_URL
    if not config.VLLM_BASE_URL:
        raise RuntimeError("VLLM_BASE_URL is not configured")

    url = f"{config.VLLM_BASE_URL.rstrip('/')}/v1/completions"
    payload = {
        "model": config.LLM_MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
    }
    headers = {}
    if config.VLLM_API_KEY:
        headers["Authorization"] = f"Bearer {config.VLLM_API_KEY}"

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()

    # Try common response shapes
    # 1) { choices: [ { text: "..." } ] }
    try:
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict) and isinstance(first.get("text"), str):
                text = first.get("text")
                logger.log_event("llm_complete", {"chars": len(prompt)})
                return text.strip()
    except Exception:
        pass

    # 2) { text: "..." }
    if isinstance(data, dict) and isinstance(data.get("text"), str):
        logger.log_event("llm_complete", {"chars": len(prompt)})
        return data.get("text").strip()

    # 3) vllm-like: { completions: [ { data: { text: '...' } } ] }
    try:
        comps = data.get("completions")
        if isinstance(comps, list) and comps:
            first = comps[0]
            txt = None
            if isinstance(first, dict):
                d = first.get("data") or first.get("result")
                if isinstance(d, dict) and isinstance(d.get("text"), str):
                    txt = d.get("text")
            if txt:
                logger.log_event("llm_complete", {"chars": len(prompt)})
                return txt.strip()
    except Exception:
        pass

    # Fallback: stringify the result
    logger.log_event("llm_complete", {"chars": len(prompt)})
    return str(data)
