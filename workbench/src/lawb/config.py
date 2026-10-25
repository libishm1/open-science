"""Configuration and paths.

The workbench keeps its state in a per-user folder (LAWB_HOME, default ~/.lawb). Nothing
personal is written into the repository.
"""

import json
import os
from pathlib import Path

DEFAULT_SOURCES = [
    {
        "name": "computational-design-skill",
        "repo": "https://github.com/libishm1/computational-design-skill.git",
        "ref": "main",
        "sparse": ["skills"],
    },
    {
        "name": "open-science",
        "repo": "https://github.com/libishm1/open-science.git",
        "ref": "main",
        "sparse": ["resources/skills"],
    },
]

# Skills the author owns. Only these are bundled or loaded from the public repositories.
# Upstream skills by other contributors are never bundled; load them from their own repository.
OWNED_SKILLS = [
    "computational-design", "ai-debugging", "research-synthesis", "conversation-handoff",
    "rhino-mcp-setup", "rhino-gh-components", "rhino-gh-presentation-checks", "robotics-ros2-ur",
    "aec-research-workflow", "molecular-figure-design",
    "pdf-to-markdown", "academic-paper-composer", "academic-paper-strategist", "tamil-translator",
    "lean-verification", "latex-document", "local-model-setup",
]

DEFAULT_MODELS = {
    "tiers": ["qwen2.5-coder:1.5b", "qwen2.5-coder:7b", "qwen3:8b"],
    "host": "http://localhost:11434",
}


def home() -> Path:
    base = os.environ.get("LAWB_HOME")
    return Path(base) if base else Path.home() / ".lawb"


def cache_dir() -> Path:
    return home() / "sources"


def bundled_skills_dir() -> Path:
    """Snapshot of the owned skills, shipped inside the package for instant, offline setup."""
    return Path(__file__).resolve().parent / "bundled" / "skills"


def local_skills_dir() -> Path:
    return home() / "local-skills"


def config_path() -> Path:
    return home() / "config.json"


def load_config() -> dict:
    """Return the user config, or the defaults if none has been written yet."""
    if config_path().exists():
        return json.loads(config_path().read_text(encoding="utf-8"))
    return {"sources": DEFAULT_SOURCES, "models": DEFAULT_MODELS, "cloud": {"enabled": False}}


def save_config(cfg: dict) -> None:
    home().mkdir(parents=True, exist_ok=True)
    config_path().write_text(json.dumps(cfg, indent=2), encoding="utf-8")
