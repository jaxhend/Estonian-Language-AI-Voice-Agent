import httpx
from . import logger
from ..core import config

async def complete(prompt: str, max_tokens: int = 512) -> str:
    url = config.LLM_URL
    payload = {
        "model": config.LLM_MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["text"]
        logger.log_event("llm_complete", {"chars": len(prompt)})
        return text.strip()

