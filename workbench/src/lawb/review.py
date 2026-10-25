"""Literature review counts (PRISMA 2020 style) derived from a screening CSV.

CSV columns (one row per record):
  record_id, strand, year, type, duplicate (yes/no),
  stage (title_abstract | full_text), decision (include | exclude), reason

Every number in the output is computed from these rows, so a reviewer can re-derive it.
Records marked duplicate=yes are removed before screening. A record counts once in the
funnel, under its first strand.
"""

import csv
from collections import Counter
from pathlib import Path


def prisma(csv_path: Path) -> dict:
    with csv_path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    # Normalise spelling variants (case, spaces) so 'Include ' and 'include' count the same.
    for r in rows:
        for key in ("record_id", "strand", "year", "type", "duplicate", "stage", "decision", "reason"):
            r[key] = (r.get(key) or "").strip()
        for key in ("duplicate", "stage", "decision"):
            r[key] = r[key].lower()
    identified = Counter(r["strand"] for r in rows)
    dup_rows = [r for r in rows if r["duplicate"].strip().lower() == "yes"]
    # One row per record per stage. A record can appear at title/abstract and again at full text.
    unique = {}
    for r in rows:
        key = (r["record_id"], r["stage"])
        if r["duplicate"].strip().lower() != "yes" and key not in unique:
            unique[key] = r
    screened = list(unique.values())
    ta_excluded = Counter(r["reason"] or "unspecified" for r in screened
                          if r["stage"] == "title_abstract" and r["decision"] == "exclude")
    ft_rows = [r for r in screened if r["stage"] == "full_text"]
    ft_excluded = Counter(r["reason"] or "unspecified" for r in ft_rows if r["decision"] == "exclude")
    included = [r for r in screened if r["decision"] == "include" and r["stage"] == "full_text"]
    return {
        "identified_per_strand": dict(identified),
        "identified_total": len(rows),
        "duplicates_removed": len(dup_rows),
        "title_abstract_screened": sum(1 for r in screened if r["stage"] == "title_abstract"),
        "title_abstract_excluded": dict(ta_excluded),
        "full_text_assessed": len(ft_rows),
        "full_text_excluded": dict(ft_excluded),
        "included": len(included),
        "included_by_year": dict(sorted(Counter(r["year"] for r in included).items())),
        "included_by_type": dict(Counter(r["type"] for r in included)),
    }


def to_markdown(counts: dict) -> str:
    def table(d):
        return "\n".join(f"| {k} | {v} |" for k, v in d.items()) or "| none | 0 |"
    return "\n".join([
        "# Screening counts (derived from the screening CSV)",
        "",
        f"Identified: {counts['identified_total']}. Duplicates removed: {counts['duplicates_removed']}. "
        f"Records screened at title and abstract (unique): {counts['title_abstract_screened']}.",
        "",
        "## Identified per strand",
        "| Strand | Records |", "|---|---|", table(counts["identified_per_strand"]),
        "",
        "## Excluded at title and abstract, by reason",
        "| Reason | Count |", "|---|---|", table(counts["title_abstract_excluded"]),
        "",
        f"Full text assessed: {counts['full_text_assessed']}.",
        "",
        "## Excluded at full text, by reason",
        "| Reason | Count |", "|---|---|", table(counts["full_text_excluded"]),
        "",
        f"Included: {counts['included']}.",
        "",
        "## Included by year", "| Year | Count |", "|---|---|", table(counts["included_by_year"]),
        "",
        "## Included by type", "| Type | Count |", "|---|---|", table(counts["included_by_type"]),
        "",
    ])
