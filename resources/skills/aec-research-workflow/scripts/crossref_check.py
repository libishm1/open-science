"""Quick DOI lookup on Crossref: prints one JSON line per DOI with title/authors/year/venue/type, or ERROR.
Use it to verify every DOI before recording it in an extraction record (templates/SCHEMA.md).

Inputs:  DOIs on the command line (bare or https://doi.org/...)
Output:  JSON lines on stdout

Example: python -P crossref_check.py 10.xxxx/first-doi https://doi.org/10.xxxx/second-doi
Requires: requests.
Env (optional): CROSSREF_MAILTO adds a contact address to the User-Agent (Crossref polite pool).
"""
import argparse
import json
import os
import time

import requests

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('dois', nargs='+')
args = ap.parse_args()

_mail = os.environ.get('CROSSREF_MAILTO', '').strip()
H = {"User-Agent": "lit-review-doi-check/1.0" + (f" (mailto:{_mail})" if _mail else "")}
for doi in args.dois:
    doi = doi.strip().lower().replace("https://doi.org/", "")
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}", headers=H, timeout=30)
        if r.status_code != 200:
            print(json.dumps({"doi": doi, "status": "ERROR", "http": r.status_code})); continue
        m = r.json()["message"]
        au = "; ".join(f"{a.get('family','')}, {a.get('given','')}" for a in m.get("author", [])[:6])
        yr = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        print(json.dumps({"doi": doi, "status": "OK", "title": (m.get("title") or [""])[0], "authors": au, "year": yr,
                          "venue": (m.get("container-title") or [""])[0], "type": m.get("type")}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"doi": doi, "status": "ERROR", "err": str(e)}))
    time.sleep(0.2)
