# -*- coding: utf-8 -*-
"""Combination map of a research field: which intersections of its dimensions are studied, and which are not.

A field is described by dimensions (technology, element, context, climate, focus, method, ...), each with
levels defined by keyword rules. Every paper of a harvested corpus is coded on every level from its title and
abstract; the script then counts every pair and every k-way combination of levels from different dimensions.

The useful output is the CLOSURE GAP: a k-way combination with no (or almost no) papers although every one of
its (k-1)-way sub-combinations is well populated. Each neighbouring pair is an established line of work, and
nobody has joined them. That is the shape of a defensible novelty claim ("PCM envelopes" x "adaptive envelopes"
x "urban microclimate": every pair studied, the triple empty), and the opposite of a claim the field already
made. A closure gap is a candidate, not a finding: read the nearest papers before claiming it.

Usage
  python -P gap_matrix.py CORPUS.json DIMENSIONS.json OUT_DIR [--k 3] [--max-n 1] [--min-sub 5]
                          [--dims technology,context,focus] [--recent 2023]

CORPUS      harvest_openalex.py output (list of works with title, abstract, publication_year, cited_by_count)
            or any JSON/JSONL list with "title" and "abstract".
DIMENSIONS  {"dimensions": {"<dim>": {"<level>": ["regex", ...] | {"any": [...], "all": [...], "none": [...]}}},
             "scope": ["regex", ...]}    (optional: keep only papers matching at least one scope rule)
            See templates/gap_dimensions.example.json.
OUT_DIR     coded.csv, levels.csv, pairs.csv, combos_k<k>.csv and REPORT.md.

Rules of thumb: keep levels within a dimension specific enough that a paper rarely matches more than two;
check the coverage line of the report (papers coded on a dimension); a level with fewer than ~10 papers makes
every combination involving it look like a gap.
"""
import argparse, csv, io, itertools, json, os, re, statistics


def load(path):
    if path.endswith(".jsonl"):
        return [json.loads(l) for l in io.open(path, encoding="utf-8") if l.strip()]
    d = json.load(io.open(path, encoding="utf-8"))
    return d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))


def rule(spec):
    if isinstance(spec, list):
        spec = {"any": spec}
    comp = {k: [re.compile(r, re.I) for r in spec.get(k, [])] for k in ("any", "all", "none")}
    return lambda t: ((not comp["any"] or any(r.search(t) for r in comp["any"]))
                      and all(r.search(t) for r in comp["all"]) and not any(r.search(t) for r in comp["none"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("corpus"); ap.add_argument("dimensions"); ap.add_argument("out")
    ap.add_argument("--k", type=int, default=3, help="size of the combinations searched for closure gaps")
    ap.add_argument("--max-n", type=int, default=1, help="a combination with at most this many papers is a gap")
    ap.add_argument("--min-sub", type=int, default=5, help="every (k-1)-sub-combination needs at least this many")
    ap.add_argument("--dims", help="comma-separated dimensions to combine (default: all)")
    ap.add_argument("--recent", type=int, default=2023, help="first year counted as recent")
    ap.add_argument("--anchor", help="comma-separated levels (level or dimension:level); report only gaps that "
                    "contain at least one, e.g. the levels where the researcher already has outputs")
    ap.add_argument("--top", type=int, default=25, help="closure gaps written to the report")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfg = json.load(io.open(a.dimensions, encoding="utf-8"))
    dims = cfg["dimensions"]
    scope = [re.compile(r, re.I) for r in cfg.get("scope", [])]
    works = []
    for w in load(a.corpus):
        t = "%s %s" % (w.get("title") or w.get("display_name") or "", w.get("abstract") or "")
        if scope and not any(r.search(t) for r in scope):
            continue
        works.append((w, t))
    N = len(works)
    levels = [(d, lv) for d, lvs in dims.items() for lv in lvs]
    test = {(d, lv): rule(spec) for d, lvs in dims.items() for lv, spec in lvs.items()}
    hits = {key: set() for key in levels}
    for i, (w, t) in enumerate(works):
        for key in levels:
            if test[key](t):
                hits[key].add(i)
    year = lambda i: works[i][0].get("publication_year") or works[i][0].get("year") or 0
    recent = {i for i in range(N) if year(i) >= a.recent}
    cites = lambda i: works[i][0].get("cited_by_count") or works[i][0].get("cited_by") or 0
    title = lambda i: (works[i][0].get("title") or works[i][0].get("display_name") or "")[:110]
    no_abs = sum(1 for w, _ in works if not (w.get("abstract") or "").strip())

    with io.open(os.path.join(a.out, "coded.csv"), "w", encoding="utf-8", newline="") as f:
        cw = csv.writer(f); cw.writerow(["doi", "year", "title"] + ["%s:%s" % k for k in levels])
        for i, (w, _) in enumerate(works):
            cw.writerow([w.get("doi"), year(i), title(i)] + [int(i in hits[k]) for k in levels])
    with io.open(os.path.join(a.out, "levels.csv"), "w", encoding="utf-8", newline="") as f:
        cw = csv.writer(f); cw.writerow(["dimension", "level", "papers", "recent"])
        for k in levels:
            cw.writerow([k[0], k[1], len(hits[k]), len(hits[k] & recent)])

    pairs = []
    for x, y in itertools.combinations(levels, 2):
        if x[0] == y[0]:
            continue
        n = len(hits[x] & hits[y]); e = len(hits[x]) * len(hits[y]) / N if N else 0
        pairs.append((x, y, n, len(hits[x] & hits[y] & recent), e, n / e if e else 0))
    with io.open(os.path.join(a.out, "pairs.csv"), "w", encoding="utf-8", newline="") as f:
        cw = csv.writer(f); cw.writerow(["level_a", "level_b", "papers", "recent", "expected", "lift"])
        for x, y, n, r, e, l in sorted(pairs, key=lambda p: -p[2]):
            cw.writerow(["%s:%s" % x, "%s:%s" % y, n, r, round(e, 1), round(l, 2)])

    use = [d for d in (a.dims.split(",") if a.dims else dims)]
    pool = [k for k in levels if k[0] in use]
    combos = []
    for c in itertools.combinations(pool, a.k):
        if len({k[0] for k in c}) < a.k:
            continue
        inter = set.intersection(*(hits[k] for k in c))
        subs = [(s, len(set.intersection(*(hits[k] for k in s)))) for s in itertools.combinations(c, a.k - 1)]
        weakest = min(n for _, n in subs)
        combos.append((c, len(inter), len(inter & recent), weakest, subs, inter))
    with io.open(os.path.join(a.out, "combos_k%d.csv" % a.k), "w", encoding="utf-8", newline="") as f:
        cw = csv.writer(f); cw.writerow(["combination", "papers", "recent", "weakest_sub_combination"])
        for c, n, r, wk, _, _ in sorted(combos, key=lambda z: (z[1], -z[3])):
            cw.writerow([" x ".join("%s:%s" % k for k in c), n, r, wk])
    anchors = {x.strip() for x in a.anchor.split(",")} if a.anchor else set()
    anchored = lambda c: not anchors or any(k[1] in anchors or "%s:%s" % k in anchors for k in c)
    gaps = sorted([z for z in combos if z[1] <= a.max_n and z[3] >= a.min_sub and anchored(z[0])], key=lambda z: -z[3])

    L = ["# Combination map", "",
         "Corpus: %d papers after scope filter (%d without an abstract, coded on the title only). Coding is by "
         "keyword rules on title and abstract; every count is a lower bound for papers that use other words." % (N, no_abs), "",
         "## Coverage per dimension", "", "| Dimension | Papers coded | Levels (papers) |", "|---|---|---|"]
    for d, lvs in dims.items():
        cov = len(set().union(*(hits[(d, lv)] for lv in lvs)))
        L.append("| %s | %d (%.0f%%) | %s |" % (d, cov, 100 * cov / max(N, 1),
                                            ", ".join("%s (%d)" % (lv, len(hits[(d, lv)])) for lv in lvs)))
    L += ["", "## Densest intersections (established lines of work)", "", "| Pair | Papers | Since %d |" % a.recent,
          "|---|---|---|"]
    for x, y, n, r, e, l in sorted(pairs, key=lambda p: -p[2])[:15]:
        L.append("| %s x %s | %d | %d |" % (x[1], y[1], n, r))
    L += ["", "## Pairs far below expectation (each level is common, together they are rare)", "",
          "| Pair | Papers | Expected if independent |", "|---|---|---|"]
    for x, y, n, r, e, l in sorted([p for p in pairs if p[4] >= 5 and p[5] < 0.25], key=lambda p: p[5])[:15]:
        L.append("| %s x %s | %d | %.0f |" % (x[1], y[1], n, e))
    L += ["", "## Closure gaps (k = %d): every %d-way sub-combination is studied, the whole is not" % (a.k, a.k - 1), "",
          "A gap needs at most %d paper(s); each sub-combination at least %d. Ranked by the weakest sub-combination."
          % (a.max_n, a.min_sub), ""]
    for c, n, r, wk, subs, inter in gaps[:a.top]:
        L.append("### %s  (%d papers)" % (" x ".join(k[1] for k in c), n))
        for s, sn in subs:
            members = set.intersection(*(hits[k] for k in s))
            top = sorted(members, key=lambda i: -cites(i))[:2]
            L.append("- %s: %d papers; most cited: %s" % (" x ".join(k[1] for k in s), sn,
                                                         "; ".join("%s (%s)" % (title(i), year(i)) for i in top)))
        for i in sorted(inter, key=lambda i: -cites(i)):
            L.append("- the paper(s) at the intersection: %s (%s), %s" % (title(i), year(i), works[i][0].get("doi")))
        L.append("")
    if not gaps:
        L.append("None at these thresholds; lower --min-sub or raise --max-n.")
    io.open(os.path.join(a.out, "REPORT.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("%d papers, %d levels, %d pairs, %d combinations, %d closure gaps -> %s"
          % (N, len(levels), len(pairs), len(combos), len(gaps), os.path.join(a.out, "REPORT.md")))


if __name__ == "__main__":
    main()
