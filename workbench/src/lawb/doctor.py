"""Environment check: what is installed, what is reachable, what is missing, and the next command to run."""

import importlib.util
import shutil
import sys

from . import config, sources
from .llm import OllamaClient


def _has(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def report() -> list[tuple[str, str, str]]:
    """Return (check, status, next step) rows. Status is OK, WARN or MISSING."""
    rows = []
    rows.append(("python 3.10+", "OK" if sys.version_info >= (3, 10) else "MISSING",
                 "install Python 3.10 or later"))
    rows.append(("git", "OK" if shutil.which("git") else "MISSING",
                 "install git (needed to pull the public skill repositories)"))
    cached = [s["name"] for s in config.load_config()["sources"] if (config.cache_dir() / s["name"]).exists()]
    bundled = config.bundled_skills_dir().is_dir()
    if cached:
        rows.append(("skills from public repos", "OK", "refresh with: python -m lawb setup --pull"))
    elif bundled:
        rows.append(("skills from public repos", "WARN", "using the bundled snapshot; pull with: python -m lawb setup --pull"))
    else:
        rows.append(("skills", "MISSING", "run: python -m lawb setup --pull"))
    rows.append(("PyMuPDF (PDF parsing)", "OK" if _has("fitz") else "WARN",
                 "pip install pymupdf (pypdf is used if this is missing)"))
    rows.append(("pypdf (PDF fallback)", "OK" if _has("pypdf") else "WARN",
                 "pip install pypdf, only if PyMuPDF is not installed"))
    try:
        client = OllamaClient()
        present = client.models()
        rows.append(("Ollama reachable", "OK", "server on localhost"))
        tiers = config.load_config()["models"]["tiers"]
        for model in tiers:
            ok = any(m == model or m.startswith(model + ":") or m == model.split(":")[0] for m in present)
            rows.append((f"model {model}", "OK" if ok else "MISSING", f"run: ollama pull {model}"))
    except Exception as exc:  # network refused, or host not local
        rows.append(("Ollama reachable", "MISSING", f"start Ollama (ollama serve): {exc.__class__.__name__}"))
    from .llm import KEY_VARS, cloud_status
    for provider in ("anthropic", "openai"):
        status = cloud_status(provider)
        rows.append((f"cloud provider {provider}", "OK" if status == "ready" else "WARN",
                     f"optional, off by default; to enable run: python -m lawb keys set {provider}"
                     if status != "ready" else "enabled; the key is present (not checked live)"))
    rows.append(("Node.js (VS Code extension tests)", "OK" if shutil.which("node") else "WARN",
                 "optional: install Node.js to check the extension file"))
    rows.append(("VS Code 'code' command", "OK" if shutil.which("code") else "WARN",
                 "optional: enable the 'code' command in VS Code to open the extension folder"))
    return rows


def print_report() -> int:
    rows = report()
    width = max(len(r[0]) for r in rows)
    for name, status, nxt in rows:
        hint = "" if status == "OK" else f"  -> {nxt}"
        print(f"{name.ljust(width)}  {status}{hint}")
    return 0 if all(r[1] != "MISSING" for r in rows) else 1
