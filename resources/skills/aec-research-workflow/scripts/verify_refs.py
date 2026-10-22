"""Verify every reference of the manuscript against the DOI registries and write references.bib.

For each entry of references_in.json (key, expected title, first author, year, DOI or null):
  * a DOI is resolved at https://doi.org by content negotiation (CSL JSON; Crossref and DataCite);
  * an entry without a DOI is searched in Crossref (query.bibliographic) and accepted only if the title matches;
  * the resolved title must match the expected one (similarity >= 0.85) and the first author's family name must agree.
Entries that pass go to references.bib with the registry's metadata (authors, year, journal, volume, issue, pages, DOI);
entries with no DOI by nature (books, standards, software, datasets) are written from references_in.json and marked.
A report (verification_report.csv) lists every entry: verified / not verified / no DOI, and why.
Titles are converted to sentence case; words in the protect list (proper nouns, software names) keep their
capitals and are wrapped in braces so biblatex does not lower-case them.

references_in.json is a list of
    {"key", "author" (first author's family name), "year", "title", "doi" (or null),
     "type" (optional biblatex type override), "override" (optional CSL fields the registry lacks)}
  or, for works without a DOI by nature,
    {"key", "title", "no_doi": true, "type": "book|manual|software|...", "fields": {biblatex field: value}, "why"}

Example: python -P verify_refs.py references_in.json --bib references.bib --report verification_report.csv --protect protect.txt
Exit code 1 if any reference is NOT VERIFIED. Requires: standard library only (needs internet access).
Env (optional): CROSSREF_MAILTO adds a contact address to the User-Agent (Crossref polite pool).
"""
import argparse
import csv
import html
import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

_mail = os.environ.get("CROSSREF_MAILTO", "").strip()
UA = {"User-Agent": "manuscript-reference-check/1.0" + (f" (mailto:{_mail})" if _mail else "")}
# Generic default; extend with --protect (one word per line) for place names, software, author names in titles.
PROTECT = {"OpenStudio", "EnergyPlus", "TRNSYS", "Radiance", "Revit", "Rhino", "Grasshopper", "BESTEST", "ISO", "ASHRAE",
           "Python", "PyTorch", "UK", "US", "USA", "EU", "Europe", "European", "IFC", "BIM", "CAD", "GIS", "AI", "ML",
           "3D", "2D", "LOD", "HVAC", "CNN", "GNN", "GNNs", "GCN", "Bayesian", "Gaussian", "Markov", "Euclidean",
           "Laplacian", "Chebyshev", "Fourier", "Monte", "Carlo", "Kalman", "Navier", "Stokes"}


def get(url, accept="application/vnd.citationstyles.csl+json", tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={**UA, "Accept": accept})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8")
        except Exception as ex:  # noqa: BLE001
            err = ex
            time.sleep(1.5 * (k + 1))
    raise err


def norm(s):
    s = unicodedata.normalize("NFKD", re.sub(r"<[^>]+>", "", s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", s.lower()).split()


def similar(a, b):
    return difflib.SequenceMatcher(None, " ".join(norm(a)), " ".join(norm(b))).ratio()


def resolve(doi):
    return json.loads(get("https://doi.org/" + urllib.parse.quote(doi, safe="/:()")))


def search(title, author):
    q = urllib.parse.urlencode({"query.bibliographic": f"{title} {author}", "rows": 5})
    items = json.loads(get(f"https://api.crossref.org/works?{q}", accept="application/json"))["message"]["items"]
    best = max(items, key=lambda it: similar(title, (it.get("title") or [""])[0]), default=None)
    return best


def sentence_case(title):
    words, out, cap_next = title.split(" "), [], True
    for w in words:
        core = re.sub(r"^[^\w]+|[^\w]+$", "", w)
        parts = [x for x in core.split("-") if x]
        plain = all(x[:1].isupper() and x[1:].islower() for x in parts) and not any(x in PROTECT for x in parts)   # "Non-Manifold"
        keep = (cap_next or core in PROTECT or (any(c.isupper() for c in core[1:]) and not plain) or any(c.isdigit() for c in core)
                or (core.isupper() and len(core) > 1))
        piece = w if keep else w.lower()
        if not cap_next and keep and core and core[0].isupper():
            piece = piece.replace(core, "{" + core + "}", 1)        # protect capitals from biblatex case changes
        out.append(piece)
        cap_next = w.endswith(":") or w.endswith("?")
    return " ".join(out)


def bib_escape(s):
    return (s or "").replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")


def names(csl):
    out = []
    for a in csl.get("author", []) or csl.get("editor", []):
        if "family" in a:
            out.append(f"{a['family']}, {a.get('given', '')}".strip(", "))
        elif "literal" in a:
            out.append("{" + a["literal"] + "}")
    return " and ".join(out)


def entry_from_csl(key, csl, kind):
    title = (csl.get("title") or "")
    title = title[0] if isinstance(title, list) else title
    sub = csl.get("subtitle") or ""
    sub = sub[0] if isinstance(sub, list) and sub else sub
    if sub and sub.lower() not in title.lower():                       # some registries split "Title: subtitle"
        title = f"{title}: {sub}"
    title = html.unescape(title).replace("<sup>TM</sup>", "™").replace("‐", "-").replace("‑", "-")
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", title)).strip()
    dates = [csl.get(k) for k in ("published-print", "journal-issue", "issued", "published-online")]   # the issue's year first
    dates = [d.get("published-print", d) if k == 1 and isinstance(d, dict) else d for k, d in enumerate(dates)]
    year = next((d["date-parts"][0][0] for d in dates if isinstance(d, dict) and d.get("date-parts") and d["date-parts"][0][0]), None)
    cont = csl.get("container-title") or ""
    cont = html.unescape(cont[0] if isinstance(cont, list) else cont)
    typ = csl.get("type", "")
    f = {"author": names(csl), "title": sentence_case(title), "year": year, "doi": csl.get("DOI")}
    if typ in ("journal-article",):
        btype = "article"; f |= {"journaltitle": cont, "volume": csl.get("volume"), "number": csl.get("issue"), "pages": csl.get("page")}
    elif typ in ("proceedings-article", "paper-conference"):
        btype = "inproceedings"; f |= {"booktitle": cont, "pages": csl.get("page"), "publisher": csl.get("publisher")}
    elif typ in ("book-chapter", "chapter"):
        btype = "incollection"; f |= {"booktitle": cont, "pages": csl.get("page"), "publisher": csl.get("publisher")}
    elif typ in ("book", "monograph"):
        btype = "book"; f |= {"publisher": csl.get("publisher")}
    elif typ in ("article", "posted-content", "preprint") or "arxiv" in (csl.get("DOI") or "").lower():
        btype = "online"; f |= {"eprinttype": "arXiv" if "arxiv" in (csl.get("DOI") or "").lower() else None, "publisher": csl.get("publisher")}
    else:
        btype = "article" if cont else "misc"; f |= {"journaltitle": cont or None, "volume": csl.get("volume"), "pages": csl.get("page")}
    if f.get("pages"):
        f["pages"] = re.sub(r"(?<=\d)-(?=\d)", "--", str(f["pages"]))
    if kind:
        btype = kind
        if kind == "inproceedings" and "journaltitle" in f:
            f["booktitle"] = f.pop("journaltitle")
    body = ",\n".join(f"  {k} = {{{bib_escape(str(v)) if k not in ('title', 'author', 'doi') else str(v).replace('&', chr(92) + '&')}}}"
                      for k, v in f.items() if v not in (None, ""))
    return f"@{btype}{{{key},\n{body}\n}}\n", title, year, (csl.get("author") or [{}])[0].get("family", "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("references_in", nargs="?", default="references_in.json", help="input list (default: references_in.json)")
    ap.add_argument("--bib", default="references.bib", help="output BibTeX/biblatex file (default: references.bib)")
    ap.add_argument("--report", default="verification_report.csv", help="output CSV report (default: verification_report.csv)")
    ap.add_argument("--protect", help="text file, one word per line, added to the capitalisation protect list")
    ap.add_argument("--min-sim", type=float, default=0.85, help="title similarity needed (default: 0.85)")
    args = ap.parse_args()
    if args.protect:
        PROTECT.update(w.strip() for w in Path(args.protect).read_text(encoding="utf-8").splitlines() if w.strip())
    MIN_SIM = args.min_sim
    refs = json.loads(Path(args.references_in).read_text(encoding="utf-8"))
    bib, rows = [], []
    for r in refs:
        key, doi = r["key"], r.get("doi")
        if r.get("no_doi"):
            fields = ",\n".join(f"  {k} = {{{v}}}" for k, v in r["fields"].items())
            bib.append(f"@{r['type']}{{{key},\n{fields}\n}}\n")
            rows.append(dict(key=key, status="no DOI (by nature)", doi="", title=r["title"], note=r.get("why", "")))
            continue
        try:
            if not doi:
                hit = search(r["title"], r["author"])
                doi = hit["DOI"] if hit and similar(r["title"], (hit.get("title") or [""])[0]) >= MIN_SIM else None
            if not doi:
                rows.append(dict(key=key, status="NOT VERIFIED", doi="", title=r["title"], note="no matching record in Crossref")); continue
            csl = resolve(doi)
            for k2, v2 in (r.get("override") or {}).items():                  # venue names / issue years the registry lacks
                csl[k2] = v2
            text, title, year, fam = entry_from_csl(key, csl, r.get("type"))
            sim = similar(r["title"], title)
            okauth = norm(r["author"])[:1] == norm(fam)[:1] if fam else True
            if sim >= MIN_SIM and okauth:
                bib.append(text)
                rows.append(dict(key=key, status="verified", doi=doi, title=title, note=f"title match {sim:.2f}; {year}"))
            else:
                rows.append(dict(key=key, status="NOT VERIFIED", doi=doi, title=title, note=f"title match {sim:.2f}, first author {fam!r} vs {r['author']!r}"))
        except Exception as ex:  # noqa: BLE001
            rows.append(dict(key=key, status="NOT VERIFIED", doi=doi or "", title=r["title"], note=f"{type(ex).__name__}: {ex}"[:150]))
        time.sleep(0.3)
    Path(args.bib).write_text("% Generated by verify_refs.py - every DOI resolved at doi.org and matched by title and first author\n\n"
                              + "\n".join(bib), encoding="utf-8")
    with open(args.report, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["key", "status", "doi", "title", "note"]); w.writeheader(); w.writerows(rows)
    bad = [x for x in rows if x["status"] == "NOT VERIFIED"]
    print(f"{len(rows)} references: {sum(x['status'] == 'verified' for x in rows)} verified, "
          f"{sum(x['status'].startswith('no DOI') for x in rows)} without DOI by nature, {len(bad)} not verified")
    for x in bad:
        print("  NOT VERIFIED", x["key"], x["doi"], "-", x["note"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
