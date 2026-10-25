"""PRISMA 2020 screening counts and a flow diagram from one screening CSV. Standard library only.

The app's agent runs this when a user attaches a screening file; it also runs from a terminal:
    python prisma_flow.py screening.csv --out-dir prisma_output

CSV columns (one row per record; header names are case-insensitive):
    record_id, strand, year, type, duplicate (yes/no), stage (title_abstract | full_text),
    decision (include | exclude), reason

Writes to the output folder:
    counts.md    the counts as tables, every number derived from the rows
    counts.json  the same counts for further analysis
    flow.svg     the PRISMA flow diagram (opens in any browser or image viewer)
    flow.mmd     the same diagram as Mermaid text
"""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

FIELDS = ("record_id", "strand", "year", "type", "duplicate", "stage", "decision", "reason")


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = []
        for raw in reader:
            row = {k.strip().lower(): (v or "").strip() for k, v in raw.items() if k}
            for key in FIELDS:
                row.setdefault(key, "")
            for key in ("duplicate", "stage", "decision"):
                row[key] = row[key].lower()
            rows.append(row)
    return rows


def count(rows: list[dict]) -> dict:
    identified = Counter(r["strand"] or "unspecified" for r in rows)
    duplicates = sum(1 for r in rows if r["duplicate"] == "yes")
    unique = {}
    for r in rows:
        key = (r["record_id"], r["stage"])
        if r["duplicate"] != "yes" and key not in unique:
            unique[key] = r
    kept = list(unique.values())
    ta = [r for r in kept if r["stage"] == "title_abstract"]
    ft = [r for r in kept if r["stage"] == "full_text"]
    ta_excl = Counter(r["reason"] or "unspecified" for r in ta if r["decision"] == "exclude")
    ft_excl = Counter(r["reason"] or "unspecified" for r in ft if r["decision"] == "exclude")
    included = [r for r in ft if r["decision"] == "include"]
    return {
        "identified_total": len(rows),
        "identified_per_strand": dict(identified),
        "duplicates_removed": duplicates,
        "title_abstract_screened": len(ta),
        "title_abstract_excluded": dict(ta_excl),
        "full_text_assessed": len(ft),
        "full_text_excluded": dict(ft_excl),
        "included": len(included),
        "included_by_year": dict(sorted(Counter(r["year"] for r in included).items())),
        "included_by_type": dict(Counter(r["type"] for r in included)),
        "check_advanced_equals_assessed":
            len(ta) - sum(ta_excl.values()) == len(ft),
    }


def table(d: dict) -> str:
    return "\n".join(f"| {k} | {v} |" for k, v in d.items()) or "| none | 0 |"


def markdown(c: dict) -> str:
    check = "yes" if c["check_advanced_equals_assessed"] else "NO - check the stage and decision columns"
    return "\n".join([
        "# Screening counts (derived from the screening CSV)", "",
        f"- Identified: {c['identified_total']}",
        f"- Duplicates removed: {c['duplicates_removed']}",
        f"- Screened at title and abstract: {c['title_abstract_screened']}",
        f"- Excluded at title and abstract: {sum(c['title_abstract_excluded'].values())}",
        f"- Full text assessed: {c['full_text_assessed']}",
        f"- Excluded at full text: {sum(c['full_text_excluded'].values())}",
        f"- Included: {c['included']}",
        f"- Records that passed screening equal records assessed at full text: {check}", "",
        "## Identified per search strand", "| Strand | Records |", "|---|---|", table(c["identified_per_strand"]), "",
        "## Excluded at title and abstract, by reason", "| Reason | Count |", "|---|---|", table(c["title_abstract_excluded"]), "",
        "## Excluded at full text, by reason", "| Reason | Count |", "|---|---|", table(c["full_text_excluded"]), "",
        "## Included by year", "| Year | Count |", "|---|---|", table(c["included_by_year"]), "",
        "## Included by type", "| Type | Count |", "|---|---|", table(c["included_by_type"]), "",
    ])


def reasons_text(d: dict) -> str:
    return "; ".join(f"{k} (n = {v})" for k, v in d.items()) or "none"


def flow_boxes(c: dict) -> list[tuple[str, str]]:
    """(main box, side box) pairs from top to bottom."""
    after_dup = c["identified_total"] - c["duplicates_removed"]
    return [
        (f"Records identified (n = {c['identified_total']})", f"Duplicates removed (n = {c['duplicates_removed']})"),
        (f"Records screened (n = {c['title_abstract_screened']})",
         f"Excluded at title and abstract (n = {sum(c['title_abstract_excluded'].values())}): {reasons_text(c['title_abstract_excluded'])}"),
        (f"Full texts assessed (n = {c['full_text_assessed']})",
         f"Excluded at full text (n = {sum(c['full_text_excluded'].values())}): {reasons_text(c['full_text_excluded'])}"),
        (f"Studies included (n = {c['included']})", ""),
    ], after_dup


def wrap(text: str, width: int) -> list[str]:
    # Keep "n = 12" together: counts use non-breaking spaces, and only ordinary spaces split lines.
    words, lines, line = text.replace("n = ", "n = ").split(" "), [], ""
    for w in words:
        if len(line) + len(w) + 1 > width and line:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        lines.append(line)
    return lines


def svg(c: dict) -> str:
    boxes, _ = flow_boxes(c)
    main_w, side_w, line_h, pad = 300, 340, 18, 12
    x_main, x_side = 30, 400
    y = 30
    parts = []
    for i, (main, side) in enumerate(boxes):
        main_lines = wrap(main, 38)
        side_lines = wrap(side, 44) if side else []
        h = max(len(main_lines), len(side_lines), 1) * line_h + 2 * pad
        parts.append(f'<rect x="{x_main}" y="{y}" width="{main_w}" height="{h}" rx="6" fill="#ffffff" stroke="#1f6f5c" stroke-width="1.5"/>')
        for j, text in enumerate(main_lines):
            parts.append(f'<text x="{x_main + pad}" y="{y + pad + 13 + j * line_h}">{escape(text)}</text>')
        if side_lines:
            parts.append(f'<rect x="{x_side}" y="{y}" width="{side_w}" height="{h}" rx="6" fill="#f6f6f3" stroke="#8a8a84" stroke-width="1"/>')
            for j, text in enumerate(side_lines):
                parts.append(f'<text x="{x_side + pad}" y="{y + pad + 13 + j * line_h}">{escape(text)}</text>')
            parts.append(f'<line x1="{x_main + main_w}" y1="{y + h / 2}" x2="{x_side}" y2="{y + h / 2}" stroke="#555" marker-end="url(#a)"/>')
        if i < len(boxes) - 1:
            parts.append(f'<line x1="{x_main + main_w / 2}" y1="{y + h}" x2="{x_main + main_w / 2}" y2="{y + h + 28}" stroke="#555" marker-end="url(#a)"/>')
        y += h + 30
    height = y + 10
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="770" height="{height}" viewBox="0 0 770 {height}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="13" fill="#1d1d1b">'
            '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
            '<path d="M0,0 L8,4 L0,8 z" fill="#555"/></marker></defs>'
            f'<rect width="770" height="{height}" fill="#ffffff"/>' + "".join(parts) + "</svg>\n")


def mermaid(c: dict) -> str:
    boxes, _ = flow_boxes(c)
    lines = ["flowchart TD"]
    for i, (main, side) in enumerate(boxes):
        lines.append(f'  m{i}["{main.replace(chr(34), chr(39))}"]')
        if side:
            lines.append(f'  s{i}["{side.replace(chr(34), chr(39))}"]')
            lines.append(f"  m{i} --> s{i}")
        if i:
            lines.append(f"  m{i - 1} --> m{i}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="PRISMA counts and flow diagram from a screening CSV.")
    ap.add_argument("csv")
    ap.add_argument("--out-dir", default="prisma_output")
    args = ap.parse_args()
    rows = read_rows(Path(args.csv))
    c = count(rows)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "counts.md").write_text(markdown(c), encoding="utf-8")
    (out / "counts.json").write_text(json.dumps(c, indent=2), encoding="utf-8")
    (out / "flow.svg").write_text(svg(c), encoding="utf-8")
    (out / "flow.mmd").write_text(mermaid(c), encoding="utf-8")
    print(f"identified {c['identified_total']}, duplicates {c['duplicates_removed']}, "
          f"screened {c['title_abstract_screened']}, full text {c['full_text_assessed']}, included {c['included']}")
    print(f"wrote {out / 'counts.md'}, {out / 'flow.svg'}")
    if not c["check_advanced_equals_assessed"]:
        print("warning: records that passed screening do not equal records assessed at full text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
