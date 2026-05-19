import json
import re
from typing import Any

import httpx

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


class LLMError(Exception):
    pass


async def complete(messages: list[dict], *, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    if not DEEPSEEK_API_KEY:
        raise LLMError("Set DEEPSEEK_API_KEY in .env")

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": DEEPSEEK_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    if r.status_code != 200:
        raise LLMError(f"DeepSeek {r.status_code}: {r.text[:300]}")

    return r.json()["choices"][0]["message"]["content"]


def parse_json(text: str) -> Any:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        text = m.group(1)
    return json.loads(text)
