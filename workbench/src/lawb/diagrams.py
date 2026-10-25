"""Diagrams from a small JSON spec, written as Mermaid text.

Spec example:
{
  "direction": "TD",
  "title": "Review pipeline",
  "nodes": {"search": "Search strands", "screen": "Screening", "include": "Included"},
  "edges": [["search", "screen", "records"], ["screen", "include", "eligible"]]
}

Mermaid text renders in VS Code (with a Mermaid preview extension), GitHub, and most Markdown
viewers. Rendering to an image is optional: it runs only if the Mermaid CLI (mmdc) is installed.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def to_mermaid(spec: dict) -> str:
    direction = spec.get("direction", "TD")
    if direction not in ("TD", "TB", "BT", "LR", "RL"):
        raise ValueError(f"unsupported direction {direction!r}")
    nodes = spec.get("nodes", {})
    lines = [f"flowchart {direction}"]
    if spec.get("title"):
        lines.append(f"  %% {spec['title']}")
    for node_id, label in nodes.items():
        if not ID.match(node_id):
            raise ValueError(f"node id {node_id!r} must be letters, digits or underscores")
        safe = str(label).replace('"', "'")
        lines.append(f'  {node_id}["{safe}"]')
    for edge in spec.get("edges", []):
        a, b = edge[0], edge[1]
        for end in (a, b):
            if end not in nodes:
                raise ValueError(f"edge refers to unknown node {end!r}")
        label = edge[2] if len(edge) > 2 else ""
        if label:
            lines.append(f"  {a} -->|{str(label).replace('|', '/')}| {b}")
        else:
            lines.append(f"  {a} --> {b}")
    return "\n".join(lines) + "\n"


def render_svg(mmd: Path, svg: Path) -> tuple[bool, str]:
    """Render Mermaid text to SVG with the Mermaid CLI. Optional: returns (ok, error text).

    If LAWB_MMDC_CONFIG points to a puppeteer config file, it is passed to mmdc (use it to point
    at a Chromium you already have). Nothing is downloaded here.
    """
    if not shutil.which("mmdc"):
        return False, "mmdc not installed"
    cmd = [shutil.which("mmdc")]  # full path: Windows cannot start a .cmd shim by bare name
    cfg = os.environ.get("LAWB_MMDC_CONFIG")
    if cfg:
        cmd += ["-p", cfg]
    cmd += ["-i", str(mmd), "-o", str(svg)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"{exc.__class__.__name__}: {exc}"
    if proc.returncode == 0 and svg.exists():
        return True, ""
    return False, (proc.stderr or proc.stdout)[-300:]


def build(spec_path: Path, out_dir: Path, render: bool = True) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    mermaid = to_mermaid(spec)
    out_dir.mkdir(parents=True, exist_ok=True)
    mmd = out_dir / (spec_path.stem + ".mmd")
    mmd.write_text(mermaid, encoding="utf-8")
    md = out_dir / (spec_path.stem + ".md")
    md.write_text(f"# {spec.get('title', spec_path.stem)}\n\n```mermaid\n{mermaid}```\n", encoding="utf-8")
    result = {"mmd": str(mmd), "md": str(md), "svg": None}
    if render:
        svg = out_dir / (spec_path.stem + ".svg")
        ok, err = render_svg(mmd, svg)
        if ok:
            result["svg"] = str(svg)
        elif err != "mmdc not installed":
            result["render_error"] = err
    return result
