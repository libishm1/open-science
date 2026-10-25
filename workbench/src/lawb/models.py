"""Model recommendations per task, and one-command installation of local models through Ollama.

Recommendations come from benchmarks/task_models.py, measured on a reference machine, and are
shipped in recommendations.json next to this file. They are a starting point: re-run the benchmark
on your own machine with `python benchmarks/task_models.py` to measure your hardware.
"""

import json
import shutil
import subprocess
from pathlib import Path

REC_FILE = Path(__file__).resolve().parent / "recommendations.json"
TASKS = ("coding", "math", "literature", "general")


def load() -> dict:
    if not REC_FILE.exists():
        return {"tasks": {}, "note": "no recommendations file; run benchmarks/task_models.py"}
    return json.loads(REC_FILE.read_text(encoding="utf-8"))


def recommend(task: str | None = None) -> list[dict]:
    rec = load()["tasks"]
    if task:
        return [{"task": task, **rec[task]}] if task in rec else []
    return [{"task": t, **rec[t]} for t in TASKS if t in rec]


def installed_models() -> list[str]:
    from .llm import OllamaClient
    try:
        return OllamaClient().models()
    except Exception:
        return []


def install(task: str, dry_run: bool = False) -> list[tuple[str, str]]:
    """Pull the recommended model(s) for a task. Returns (model, status) pairs."""
    if not shutil.which("ollama"):
        return [("ollama", "not installed: see https://ollama.com/download, or run the installer script")]
    tasks = TASKS if task == "all" else (task,)
    have = set(installed_models())
    results = []
    for t in tasks:
        entry = load()["tasks"].get(t)
        if not entry:
            results.append((t, "no recommendation for this task"))
            continue
        for model in [entry["model"], *entry.get("small", [])][:2]:
            if model in have:
                results.append((model, "already installed"))
                continue
            if dry_run:
                results.append((model, f"would run: ollama pull {model}"))
                continue
            proc = subprocess.run(["ollama", "pull", model])
            results.append((model, "installed" if proc.returncode == 0 else f"pull failed (exit {proc.returncode})"))
            have.add(model)
    return results
