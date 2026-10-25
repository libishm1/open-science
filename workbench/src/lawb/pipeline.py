"""Routed error loop: a fixed pipeline detects an error, a local model proposes one exact edit, the pipeline re-checks.

Project config (pipeline.json, in the project folder):
{
  "steps":   [{"name": "compile", "cmd": ["python", "-m", "py_compile", "units.py"]},
              {"name": "tests",   "cmd": ["python", "-m", "unittest", "test_all", "-v"]}],
  "modules": ["units.py", "stats.py"],           # the only files the model may edit
  "routing": {"test_units": "units.py"},          # failing test name -> module that test covers
  "max_rounds": 4
}

Rules that keep the loop safe for small models:
  - the model sees the module(s) covered by the failing tests, with their current code
  - the history records only each attempt's outcome, never old text, so the model copies "old" from the current code
  - an edit applies only if its "old" text occurs exactly once in an allowed module
  - the loop stops when every step passes or when max_rounds is reached
"""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

FAILED_TEST = re.compile(r"^(test_\w+) .*\.\.\. (?:FAIL|ERROR)", re.MULTILINE)


def load_project(project_dir: Path) -> dict:
    cfg = json.loads((project_dir / "pipeline.json").read_text(encoding="utf-8"))
    for key in ("steps", "modules"):
        if key not in cfg:
            raise ValueError(f"pipeline.json is missing '{key}'")
    cfg.setdefault("routing", {})
    cfg.setdefault("max_rounds", 4)
    return cfg


def run_steps(root: Path, cfg: dict) -> tuple[bool, str, str]:
    """Run each step in order. Return (passed, error_output, failing_step_name)."""
    for step in cfg["steps"]:
        proc = subprocess.run(step["cmd"], cwd=root, capture_output=True, text=True, timeout=300)
        if proc.returncode != 0:
            return False, proc.stdout + proc.stderr, step["name"]
    return True, "", ""


def targets(err: str, cfg: dict) -> list[str]:
    """Modules covered by the failing tests, in order, without duplicates. Falls back to the first module."""
    found = []
    for name in FAILED_TEST.findall(err):
        module = cfg["routing"].get(name)
        if module and module not in found:
            found.append(module)
    return found or [cfg["modules"][0]]


def parse_edit(reply: str) -> dict | None:
    m = re.search(r"\{.*\}", reply, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return obj if all(k in obj for k in ("file", "old", "new")) else None


def apply_edit(root: Path, cfg: dict, edit: dict) -> tuple[bool, str]:
    name = Path(edit["file"]).name
    if name not in cfg["modules"]:
        return False, f"{name} is not an editable module"
    path = root / name
    text = path.read_text(encoding="utf-8")
    if text.count(edit["old"]) != 1:
        return False, "old text does not occur exactly once"
    path.write_text(text.replace(edit["old"], edit["new"], 1), encoding="utf-8")
    return True, ""


def build_prompt(root: Path, cfg: dict, err: str, failing_step: str, history: list[dict]) -> str:
    tests = FAILED_TEST.findall(err)
    tail = "\n".join(err.splitlines()[-12:])
    code_blocks = []
    for module in targets(err, cfg):
        code = (root / module).read_text(encoding="utf-8")
        code_blocks.append(f"--- {module} (current code) ---\n{code}")
    past = "\n".join(f"- round {h['round']}: {h['result']}" for h in history) or "- none"
    return (
        f"Failing step: {failing_step}\n"
        f"Failing tests: {', '.join(tests) if tests else 'unknown'}\n"
        f"Error output (last 12 lines):\n{tail}\n\n"
        + "\n\n".join(code_blocks) + "\n\n"
        f"Previous attempts (outcome only):\n{past}\n\n"
        "Fix one module so a failing test passes. Copy \"old\" exactly from the CURRENT code above. "
        "Reply with ONE JSON object only: "
        '{"file": "<module name>", "old": "<exact text to replace>", "new": "<replacement>"}'
    )


def run_loop(project_dir: Path, client, model: str, system: str | None = None) -> dict:
    """Run the loop on a fresh copy of the project. The original folder is never edited."""
    cfg = load_project(project_dir)
    tmp = Path(tempfile.mkdtemp(prefix="lawb_"))
    root = tmp / project_dir.name
    shutil.copytree(project_dir, root, ignore=shutil.ignore_patterns("__pycache__"))
    log: list[dict] = []
    passed, err, step = run_steps(root, cfg)
    rounds = 0
    while not passed and rounds < cfg["max_rounds"]:
        rounds += 1
        reply = client.chat(model, build_prompt(root, cfg, err, step, log), system=system)
        edit = parse_edit(reply)
        if edit is None:
            log.append({"round": rounds, "result": "invalid JSON"})
        else:
            ok, why = apply_edit(root, cfg, edit)
            log.append({"round": rounds, "result": "applied" if ok else f"rejected: {why}",
                        "file": edit.get("file")})
        passed, err, step = run_steps(root, cfg)
    return {"model": model, "fixed": passed, "rounds": rounds, "log": log, "workdir": str(root)}
