# -*- coding: utf-8 -*-
"""Convert author-year citations in a Markdown manuscript to numbered [n] in order of first appearance and
regenerate the References section (cited works, numbered). Optionally append the uncited pool entries as a
supplementary bibliography.

Recognised forms: narrative "Smith et al. (2019)", "Smith and Jones (2016, 2017a)", "Smith et al.'s (2020)";
parenthetical "(Smith et al., 2019; Jones, 2020a, b)", also with prose inside the brackets. Everything after
the references heading is replaced; a section starting with --tail-heading (e.g. figure captions) is kept.

Inputs:  manuscript.md, refpool.json [{"key" (ends in the year, optional a/b suffix), "authors" ("Surname, I.; ..."),
         "year", "title", "venue", "doi_or_url", optional "cr_volume", "cr_issue", "cr_pages"}]
Output:  numbered manuscript (default: <manuscript>_numbered.md); citations that could not be resolved are printed.

Example: python number_citations.py Manuscript.md refpool.json --out Manuscript_numbered.md
Requires: standard library only.
"""
import argparse, json, os, re, unicodedata

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("manuscript"); ap.add_argument("refpool")
ap.add_argument("--out", help="output Markdown (default: <manuscript>_numbered.md)")
ap.add_argument("--refs-heading", default="## References", help='references heading (default: "## References")')
ap.add_argument("--tail-heading", default="### Figure captions", help="section after the references to keep (default: \"### Figure captions\")")
ap.add_argument("--with-supplementary", action="store_true", help="append uncited pool entries as a supplementary bibliography")
args = ap.parse_args()

def norm(s):
    for a, b in (("ø", "o"), ("Ø", "O"), ("æ", "ae"), ("Æ", "Ae"), ("ß", "ss"), ("ł", "l")):
        s = s.replace(a, b)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.lower())

pool = json.load(open(args.refpool, encoding="utf-8"))
lookup = {}
for r in pool:
    first = r["authors"].split(";")[0].split(",")[0].strip()
    toks = [t for t in first.split()
            if not re.fullmatch(r"([A-Z]\.?-?)+", t) and t.lower().strip(".") not in ("et", "al")]
    surname = norm("".join(toks)) if toks else norm(first.split()[0])
    m = re.search(r"(\d{4})([ab]?)$", r["key"])
    suf = m.group(2) if m else ""
    lookup[(surname, str(r["year"]) + suf)] = r["key"]
    lookup.setdefault((surname, str(r["year"])), r["key"])

unresolved = []

def cite_keys(author_txt, years_txt):
    a2 = norm(re.sub(r"\bet al\.?'?s?\b|&.*| and .*", "", author_txt))
    keys = []
    parts = [y.strip() for y in years_txt.split(",")]
    expanded = []
    lastyear = None
    for p in parts:
        if re.fullmatch(r"\d{4}[ab]?", p):
            expanded.append(p); lastyear = p[:4]
        elif re.fullmatch(r"[ab]", p) and lastyear:
            expanded.append(lastyear + p)
    for y in expanded:
        key = lookup.get((a2, y))
        if not key:
            unresolved.append(f"{author_txt} {y} (norm={a2})"); continue
        keys.append(key)
    return keys

ms = open(args.manuscript, encoding="utf-8").read()
body, _, refs_old = ms.partition(args.refs_heading)

AUTH = r"[A-Z][\w\-'À-ɏ]+(?:\s+[A-Z][\w\-'À-ɏ]+)?"

def repl_narrative(m):
    keys = cite_keys(m.group(1), m.group(2))
    if not keys: return m.group(0)
    return m.group(1) + " {{C:" + "|".join(keys) + "}}"

# narrative: "Smith et al.'s (2019)", "Jones et al. (2016, 2017)", "Lee et al. (2020)"
body = re.sub(rf"({AUTH}(?:\s+(?:and|&)\s+{AUTH})?(?:\s+et al\.?'?s?)?)\s*\((\d{{4}}[ab]?(?:\s*,\s*(?:\d{{4}}[ab]?|[ab]))*)\)",
              repl_narrative, body)

# parenthetical groups possibly with prose and multiple cites
def repl_paren(m):
    inner = m.group(1)
    if not re.search(r"\d{4}", inner) or "{{C:" in inner: return m.group(0)
    frags = inner.split(";")
    out_frags, all_keys, pure = [], [], True
    for f in frags:
        cm = re.search(rf"({AUTH}(?:\s+(?:and|&)\s+{AUTH})?(?:\s+et al\.?)?)\s*,\s*(\d{{4}}[ab]?(?:\s*,\s*(?:\d{{4}}[ab]?|[ab]))*)\s*$", f.strip())
        if cm:
            keys = cite_keys(cm.group(1), cm.group(2))
            prefix = f.strip()[:cm.start()].rstrip(" ,;—-")
            if prefix:
                pure = False
                out_frags.append((prefix + " {{C:" + "|".join(keys) + "}}") if keys else f.strip())
            else:
                all_keys.extend(keys)
        else:
            pure = False
            out_frags.append(f.strip())
    if pure and all_keys:
        return "{{C:" + "|".join(dict.fromkeys(all_keys)) + "}}"
    if all_keys:
        out_frags.append("{{C:" + "|".join(all_keys) + "}}")
    return "(" + "; ".join(x for x in out_frags if x) + ")"

body = re.sub(r"\(([^()]*\b(?:19|20)\d{2}[ab]?[^()]*)\)", repl_paren, body)

# phase 2: assign numbers strictly by position of markers in the final text
order, numbers = [], {}
def assign(m):
    keys = m.group(1).split("|")
    nums = []
    for k in keys:
        if k not in numbers:
            order.append(k); numbers[k] = len(order)
        nums.append(numbers[k])
    return "[" + ",".join(map(str, nums)) + "]"
body = re.sub(r"\{\{C:([^}]+)\}\}", assign, body)

cited = [k for k in order]
bykey = {r["key"]: r for r in pool}
ref_lines = []
for i, k in enumerate(cited, 1):
    r = bykey[k]
    # volume(issue), pages or article number (e.g. from Crossref), when available
    vol = r.get("cr_volume", "")
    loc = (vol + (f"({r['cr_issue']})" if r.get("cr_issue") else "")) if vol else ""
    pg = r.get("cr_pages", "").replace("-", "–")
    src = ", ".join(x for x in (loc, pg) if x)
    ref_lines.append(f"[{i}] {r['authors']} ({r['year']}). {r['title']}. *{r['venue']}*"
                     + (f" {src}" if src else "") + f". {r.get('doi_or_url','')}")
supp = [r for r in pool if r["key"] not in numbers]
supp_lines = [f"- {r['authors']} ({r['year']}). {r['title']}. *{r['venue']}*. {r.get('doi_or_url','')}" for r in supp]

# Uncited works are left out by default: they add length without scientific value unless the venue asks for them.
new = body + args.refs_heading + "\n\n" + "\n".join(ref_lines) + "\n"
if args.with_supplementary and supp_lines:
    new += "\n## Supplementary bibliography (not cited)\n\n" + "\n".join(supp_lines) + "\n"
# keep the section which followed the old references (e.g. figure captions)
tail = refs_old.partition(args.tail_heading)[2] if args.tail_heading else ""
if tail:
    new += "\n" + args.tail_heading + tail
out = args.out or os.path.splitext(args.manuscript)[0] + "_numbered.md"
open(out, "w", encoding="utf-8").write(new)
print(f"cited (numbered in order of appearance): {len(cited)}")
print(f"supplementary (uncited): {len(supp)}" + ("" if args.with_supplementary else " (not written)"))
print("UNRESOLVED:", unresolved if unresolved else "none")
print("->", out)
