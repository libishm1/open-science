"""API keys for the optional cloud providers, kept out of files and out of the repository.

Where a key lives, in the order it is read:
  1. the operating system credential store (Windows Credential Manager, macOS Keychain, or
     the Secret Service on Linux), via the 'keyring' package. This is what `lawb keys set` uses.
  2. the environment variable ANTHROPIC_API_KEY or OPENAI_API_KEY, if the store has no entry.

Keys are never written to config.json, the repository, or any log. Commands show whether a key is
set, never its value. Every cloud call is recorded in a local log with the provider, the model, and
the time. The prompt and the answer are not recorded.
"""

import getpass
import json
import os
import time

from . import config

SERVICE = "local-agent-workbench"
ENV_VARS = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY"}


def _keyring():
    try:
        import keyring
        return keyring
    except ImportError:
        return None


def get_key(provider: str) -> tuple[str | None, str | None]:
    """Return (key, source). Source is 'keyring', 'environment', or None. Never prints the key."""
    kr = _keyring()
    if kr is not None:
        try:
            value = kr.get_password(SERVICE, provider)
            if value:
                return value, "keyring"
        except Exception:
            pass  # no usable credential store on this machine; fall through to the environment
    value = os.environ.get(ENV_VARS[provider])
    if value:
        return value, "environment"
    return None, None


def set_key(provider: str, value: str | None = None) -> str:
    """Store a key in the credential store. Prompts with hidden input when no value is given."""
    kr = _keyring()
    if kr is None:
        raise RuntimeError("the 'keyring' package is not installed: python -m pip install keyring")
    if value is None:
        value = getpass.getpass(f"Paste your {provider} API key (input is hidden): ").strip()
    if not value:
        raise ValueError("no key entered")
    kr.set_password(SERVICE, provider, value)
    enable_cloud()
    return "keyring"


def delete_key(provider: str) -> bool:
    kr = _keyring()
    if kr is None:
        return False
    try:
        kr.delete_password(SERVICE, provider)
        return True
    except Exception:
        return False


def enable_cloud(enabled: bool = True) -> None:
    cfg = config.load_config()
    cfg["cloud"] = {**cfg.get("cloud", {}), "enabled": enabled}
    config.save_config(cfg)


def status_rows() -> list[tuple[str, str, str]]:
    """Return (provider, status, detail). No key value appears here."""
    rows = []
    enabled = config.load_config().get("cloud", {}).get("enabled", False)
    for provider in ENV_VARS:
        key, source = get_key(provider)
        if key is None:
            state = "not set"
            detail = f"run: python -m lawb keys set {provider}"
        else:
            state = "set"
            detail = f"from {source}; cloud {'enabled' if enabled else 'disabled (run: python -m lawb keys enable)'}"
        rows.append((provider, state, detail))
    return rows


def log_path():
    return config.home() / "cloud-calls.jsonl"


def record_cloud_call(provider: str, model: str) -> None:
    """Append a metadata-only line. The prompt and the answer are never written."""
    config.home().mkdir(parents=True, exist_ok=True)
    line = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "provider": provider, "model": model}
    with log_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line) + "\n")


def read_cloud_log(limit: int = 50) -> list[dict]:
    if not log_path().exists():
        return []
    lines = log_path().read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in lines[-limit:]]
