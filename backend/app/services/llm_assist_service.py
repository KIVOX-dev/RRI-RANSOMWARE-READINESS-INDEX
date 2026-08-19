"""Optional plain-language explain assist (spec §34). Uses OpenRouter free-
tier models with key/model rotation on rate limit. This service NEVER
computes or influences scores, priorities, remediation ranking, or compliance
status — it only rewrites text the deterministic backend already produced.
Degrades silently (feature hidden, not erroring the page) if unconfigured or
if every key/model is exhausted.
"""
import time

import httpx

from app.core.config import get_settings

_exhausted_until: dict[str, float] = {}

SYSTEM_PROMPT = (
    "You rewrite short cybersecurity-assessment text in plain, non-technical language for a business "
    "audience. You do not add new facts, numbers, scores, priorities, or recommendations beyond what is "
    "given. You do not invent statistics or legal/regulatory citations. Keep it to 2-4 sentences."
)


def is_configured() -> bool:
    return bool(get_settings().openrouter_keys_list)


def explain(content: str) -> str | None:
    settings = get_settings()
    keys = settings.openrouter_keys_list
    models = settings.openrouter_models_list
    if not keys or not models:
        return None

    now = time.time()
    for model in models:
        for key in keys:
            backoff_key = f"{model}:{key[-6:]}"
            if _exhausted_until.get(backoff_key, 0) > now:
                continue
            try:
                response = httpx.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": content},
                        ],
                        "max_tokens": 220,
                        "temperature": 0.3,
                    },
                    timeout=15.0,
                )
                if response.status_code == 429 or response.status_code >= 500:
                    _exhausted_until[backoff_key] = now + 60
                    continue
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
            except (httpx.HTTPError, KeyError, IndexError):
                _exhausted_until[backoff_key] = now + 30
                continue
    return None
