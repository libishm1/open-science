"""Discover, find and load skills from the pulled public repositories and the local skill folder."""

import re
from dataclasses import dataclass
from pathlib import Path

from . import config, sources

FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class Skill:
    name: str
    description: str
    path: Path
    origin: str  # "public:<source>" or "local"

    @property
    def text(self) -> str:
        return (self.path / "SKILL.md").read_text(encoding="utf-8")

    def section(self, title: str) -> str:
        """Return one level-2 section by title, for small models that load one part at a time."""
        body = self.text
        m = re.search(rf"(?m)^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", body, re.DOTALL)
        return ("## " + title + m.group(1)).rstrip() + "\n" if m else ""


def _frontmatter(text: str) -> dict:
    """Read top-level 'key: value' pairs. Supports folded (>) and literal (|) block scalars."""
    m = FRONT_RE.match(text)
    fields = {}
    if not m:
        return fields
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            value = value.strip()
            if value in (">", "|", ">-", "|-"):
                block = []
                i += 1
                while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                    block.append(lines[i].strip())
                    i += 1
                sep = " " if value.startswith(">") else "\n"
                value = sep.join(b for b in block if b)
                fields[key.strip()] = value
                continue
            fields[key.strip()] = value
        i += 1
    return fields


def discover() -> dict[str, Skill]:
    """Return {name: Skill}. The first root that defines a name wins."""
    found: dict[str, Skill] = {}
    for root, origin_label in sources.skill_roots_with_origin():
        for folder in sorted(p for p in root.iterdir() if p.is_dir()):
            md = folder / "SKILL.md"
            if not md.is_file():
                continue
            fields = _frontmatter(md.read_text(encoding="utf-8", errors="replace"))
            name = fields.get("name", folder.name)
            if name in found:
                continue
            if origin_label != "local" and name not in config.OWNED_SKILLS:
                continue  # upstream skills are not bundled or loaded by default
            origin = origin_label
            found[name] = Skill(name=name, description=fields.get("description", ""),
                                path=folder, origin=origin)
    return found


def find(query: str, limit: int = 8) -> list[Skill]:
    """Rank skills by how many query words appear in the name and description."""
    words = [w for w in re.split(r"\W+", query.lower()) if len(w) > 2]
    scored = []
    for skill in discover().values():
        hay = (skill.name + " " + skill.description).lower()
        score = sum(hay.count(w) for w in words)
        if score:
            scored.append((score, skill.name, skill))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [s for _, _, s in scored[:limit]]
