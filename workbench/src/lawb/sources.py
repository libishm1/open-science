"""Where skills come from, in priority order:

  1. local      : your own skill folders, imported on this machine (never bundled)
  2. pulled     : the public repositories, cached under LAWB_HOME/sources (refresh with `setup --pull`)
  3. bundled    : a snapshot of the owned skills shipped inside the package (instant, offline)

Only skills listed in config.OWNED_SKILLS come from the public repositories or the bundle.
"""

import json
import shutil
import subprocess
from pathlib import Path

from . import config


def _git(args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=600)


def sync_source(src: dict, ref_override: str | None = None) -> tuple[bool, str]:
    """Clone or update one source with a sparse, shallow checkout. Returns (ok, message)."""
    dest = config.cache_dir() / src["name"]
    ref = ref_override or src["ref"]
    if not shutil.which("git"):
        return False, "git not found on PATH; install git, or use the bundled skills"
    if (dest / ".git").exists():
        fetched = _git(["fetch", "--depth", "1", "origin", ref], cwd=dest)
        if fetched.returncode != 0:
            return False, f"{src['name']}: fetch failed; keeping the cached copy"
        _git(["checkout", "-q", "-f", "FETCH_HEAD"], cwd=dest)
        return True, f"{src['name']}: updated to {ref}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    cloned = _git(["clone", "--depth", "1", "--filter=blob:none", "--sparse",
                   "-b", ref, src["repo"], str(dest)])
    if cloned.returncode != 0:
        return False, f"{src['name']}: clone failed: {cloned.stderr.strip()[:200]}"
    _git(["sparse-checkout", "set", *src["sparse"]], cwd=dest)
    return True, f"{src['name']}: cloned {ref}"


def pulled_roots() -> list[tuple[Path, str]]:
    roots = []
    for src in config.load_config()["sources"]:
        base = config.cache_dir() / src["name"]
        for rel in src["sparse"]:
            if (base / rel).is_dir():
                roots.append((base / rel, f"pulled:{src['name']}"))
    return roots


def skill_roots_with_origin() -> list[tuple[Path, str]]:
    """Return (folder, origin label) pairs, highest priority first."""
    out = []
    if config.local_skills_dir().is_dir():
        out.append((config.local_skills_dir(), "local"))
    out.extend(pulled_roots())
    if config.bundled_skills_dir().is_dir():
        out.append((config.bundled_skills_dir(), "bundled"))
    return out


def build_bundle() -> dict:
    """Copy the owned skills from the pulled repositories into the package and record their commits."""
    dest = config.bundled_skills_dir()
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    record = {"owned": config.OWNED_SKILLS, "sources": []}
    for src in config.load_config()["sources"]:
        base = config.cache_dir() / src["name"]
        if not (base / ".git").exists():
            raise RuntimeError(f"{src['name']} is not pulled yet; run: python -m lawb setup --pull")
        sha = _git(["rev-parse", "HEAD"], cwd=base).stdout.strip()
        branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=base).stdout.strip()
        record["sources"].append({"name": src["name"], "repo": src["repo"], "ref": branch, "commit": sha})
        for rel in src["sparse"]:
            for folder in sorted(p for p in (base / rel).iterdir() if p.is_dir()):
                if (folder.name in config.OWNED_SKILLS and (folder / "SKILL.md").is_file()
                        and not (dest / folder.name).exists()):  # first source wins
                    shutil.copytree(folder, dest / folder.name,
                                    ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".git"))
    copied = sorted(p.name for p in dest.iterdir())
    record["skills"] = copied
    (dest.parent / "SNAPSHOT.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record
