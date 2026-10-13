"""OpenAI-compatible chat client (stdlib). Works with OpenAI, LiteLLM, vLLM, Ollama and llama.cpp servers."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

DEFAULT_BASE_URL = "http://localhost:4000/v1"  # LiteLLM's default port; override for any other server
Post = Callable[[str, dict, dict], dict]


class LLMError(RuntimeError):
    pass


def _http(url: str, payload: dict | None, headers: dict) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
        raise LLMError(f"{url}: {err}") from err


@dataclass
class LLM:
    base_url: str
    api_key: str
    model: str | None
    http: Post = _http

    @classmethod
    def from_env(cls, base_url: str | None = None, model: str | None = None, *,
                 file_base_url: str | None = None, file_model: str | None = None,
                 key_env: str | None = None) -> "LLM":
        """Resolve settings: command-line flag, then environment, then config file, then the default."""
        env = os.environ
        return cls(
            base_url=(base_url or env.get("WEEKSHIP_LLM_BASE_URL") or env.get("OPENAI_BASE_URL")
                      or file_base_url or DEFAULT_BASE_URL).rstrip("/"),
            api_key=env.get("WEEKSHIP_LLM_API_KEY") or (key_env and env.get(key_env)) or env.get("OPENAI_API_KEY") or "none",
            model=model or env.get("WEEKSHIP_MODEL") or file_model,
        )

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def resolve_model(self) -> str:
        """Use the configured model, else the first one the server lists."""
        if self.model:
            return self.model
        listing = self.http(f"{self.base_url}/models", None, self._headers())
        ids = [m["id"] for m in listing.get("data", []) if m.get("id")]
        if not ids:
            raise LLMError(f"{self.base_url}/models lists no models; set WEEKSHIP_MODEL")
        self.model = ids[0]
        return self.model

    def complete(self, system: str, user: str, max_tokens: int = 700) -> str:
        payload = {"model": self.resolve_model(), "temperature": 0.3, "max_tokens": max_tokens,
                   "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        reply = self.http(f"{self.base_url}/chat/completions", payload, self._headers())
        try:
            text = reply["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as err:
            raise LLMError(f"unexpected reply shape: {str(reply)[:200]}") from err
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
        if not text:
            raise LLMError("empty completion")
        return text


def numbers_in(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", text))


def numbers_ok(output: str, facts: str) -> bool:
    """True when every number the model wrote also appears in the facts it was given."""
    return numbers_in(output) <= numbers_in(facts)
