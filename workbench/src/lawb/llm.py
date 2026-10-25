"""Model providers behind one call: chat(model_spec, user, system, num_predict) -> text.

A model spec is "provider:model". A bare name means Ollama (local), so existing configs keep working.

  ollama:qwen3:8b                  local, always available, default
  anthropic:claude-opus-5-5        Claude API, official 'anthropic' SDK
  openai:<model id>                OpenAI API (Codex-class models), official 'openai' SDK

Cloud providers are OFF by default. They run only when config.cloud.enabled is true AND the
provider's key is in the environment. The default setup therefore never sends data off the machine.
Keys are read from the environment only and are never written to disk or printed.
"""

import json
import os
import re
import urllib.request
from urllib.parse import urlparse

from . import config, secrets

THINK = re.compile(r"<think>.*?</think>", re.DOTALL)
KEY_VARS = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}


class LocalOnlyError(ValueError):
    pass


class CloudDisabledError(RuntimeError):
    pass


def split_spec(spec: str) -> tuple[str, str]:
    """'anthropic:claude-opus-5-5' -> ('anthropic', 'claude-opus-5-5'). A bare name is Ollama."""
    head, _, rest = spec.partition(":")
    if head in ("ollama", "anthropic", "openai") and rest:
        return head, rest
    return "ollama", spec


def cloud_status(provider: str) -> str:
    """Return 'disabled', 'no key', or 'ready'. Never calls the network and never returns the key."""
    if not config.load_config().get("cloud", {}).get("enabled", False):
        return "disabled"
    key, _ = secrets.get_key(provider)
    return "ready" if key else "no key"


class OllamaClient:
    def __init__(self, host: str | None = None, timeout: int = 900):
        self.host = host or config.load_config()["models"]["host"]
        parsed = urlparse(self.host)
        if parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise LocalOnlyError(f"host {self.host!r} is not local; use a cloud provider prefix instead")
        self.timeout = timeout

    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(self.host + path, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def models(self) -> list[str]:
        req = urllib.request.Request(self.host + "/api/tags")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return [m["name"] for m in json.loads(resp.read().decode("utf-8"))["models"]]

    def chat(self, model: str, user: str, system: str | None = None, num_predict: int = 500) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})
        body = {"model": model, "messages": messages, "stream": False, "think": False,
                "options": {"temperature": 0, "num_ctx": 8192, "num_predict": num_predict}}
        data = self._post("/api/chat", body)
        return THINK.sub("", data["message"]["content"]).strip()


def anthropic_chat(model: str, user: str, system: str | None, num_predict: int, client=None,
                   api_key: str | None = None) -> str:
    """Claude via the official SDK. Uses the given key, or ANTHROPIC_API_KEY, or an `ant auth login` profile."""
    if client is None:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    kwargs = {"model": model, "max_tokens": max(num_predict, 16), "messages": [{"role": "user", "content": user}]}
    if system:
        kwargs["system"] = system
    message = client.messages.create(**kwargs)
    return "".join(block.text for block in message.content if block.type == "text").strip()


def openai_chat(model: str, user: str, system: str | None, num_predict: int, client=None,
                api_key: str | None = None) -> str:
    """OpenAI chat completions via the official SDK. Uses the given key, or OPENAI_API_KEY."""
    if client is None:
        import openai
        client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    resp = client.chat.completions.create(model=model, messages=messages, max_completion_tokens=num_predict)
    return (resp.choices[0].message.content or "").strip()


class RouterClient:
    """One entry point for every provider. Pipelines call router.chat(spec, user, system=...)."""

    def __init__(self, ollama: OllamaClient | None = None):
        self._ollama = ollama

    @property
    def ollama(self) -> OllamaClient:
        if self._ollama is None:
            self._ollama = OllamaClient()
        return self._ollama

    def chat(self, spec: str, user: str, system: str | None = None, num_predict: int = 500) -> str:
        provider, model = split_spec(spec)
        if provider == "ollama":
            return self.ollama.chat(model, user, system=system, num_predict=num_predict)
        status = cloud_status(provider)
        if status != "ready":
            hint = ("run: python -m lawb keys enable" if status == "disabled"
                    else f"run: python -m lawb keys set {provider}")
            raise CloudDisabledError(f"{provider} cloud is {status}. {hint}")
        key, _ = secrets.get_key(provider)
        if provider == "anthropic":
            out = anthropic_chat(model, user, system, num_predict, api_key=key)
        else:
            out = openai_chat(model, user, system, num_predict, api_key=key)
        secrets.record_cloud_call(provider, model)  # metadata only: no prompt, no answer
        return out
