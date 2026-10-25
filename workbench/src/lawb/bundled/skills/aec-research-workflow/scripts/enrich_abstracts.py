"""Fill missing/short abstracts (Semantic Scholar batch, then Crossref) for the candidate screen set.

The candidate set is taken from --select (default: the pool itself), optionally limited by year range and
keyword pre-score; records tagged with a --prior-tag prefix in their `src` list bypass the score limit.
Enriched abstracts (and Semantic Scholar TLDRs) are written back into --pool, so a re-score picks them up.

Inputs:  pool JSON (list of OpenAlex-style works with id, doi, abstract, publication_year[, score, src])
Output:  the same pool file, updated in place (abstract, abstract_src, tldr)

Example: python -P enrich_abstracts.py harvest/openalex_raw.json --years 2021 2026
         python -P enrich_abstracts.py harvest/pool_raw.json --select harvest/pool_scored.json --min-score 12 --prior-tag prior_
Requires: requests.
Env (optional): S2_API_KEY (Semantic Scholar), CROSSREF_MAILTO (Crossref polite pool).
"""
import argparse
import html
import json
import os
import re
import time

import requests

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('pool', help='pool JSON to enrich (written back in place)')
ap.add_argument('--select', help='JSON the candidate set is chosen from (default: the pool)')
ap.add_argument('--years', nargs=2, type=int, metavar=('FROM', 'TO'), help='keep publication years in this range')
ap.add_argument('--min-score', type=float, help='keep records with score >= this (needs a "score" field)')
ap.add_argument('--prior-tag', action='append', default=[], help='src tag prefix that bypasses --min-score (repeatable)')
ap.add_argument('--min-chars', type=int, default=200, help='abstracts shorter than this are re-fetched (default: 200)')
args = ap.parse_args()

raw = {w['id']: w for w in json.load(open(args.pool, encoding='utf-8'))}
p = json.load(open(args.select, encoding='utf-8')) if args.select else list(raw.values())


def nd(d): return re.sub(r'^https?://(dx\.)?doi\.org/', '', (d or '').lower())


def recent(w):
    y = w.get('publication_year')
    return not args.years or bool(y and args.years[0] <= y <= args.years[1])


prior = lambda w: any(s.startswith(t) for t in args.prior_tag for s in w.get('src', []))
sel = [w for w in p if recent(w) and (args.min_score is None or w.get('score', 0) >= args.min_score or prior(w))]
MIN = args.min_chars
need = [w for w in sel if len(w.get('abstract') or '') < MIN and w.get('doi')]
print('candidate set', len(sel), 'need abstracts', len(need))
_mail = os.environ.get('CROSSREF_MAILTO', '').strip()
UA = {'User-Agent': 'lit-review-script/1.0 (academic research' + (f'; mailto:{_mail}' if _mail else '') + ')'}
S2_HDR = dict(UA, **({'x-api-key': os.environ['S2_API_KEY'].strip()} if os.environ.get('S2_API_KEY', '').strip() else {}))
got_s2 = 0
for i in range(0, len(need), 100):
    ch = need[i:i + 100]
    for a in range(5):
        try:
            r = requests.post('https://api.semanticscholar.org/graph/v1/paper/batch', params={'fields': 'abstract,tldr,externalIds'},
                              json={'ids': ['DOI:' + nd(w['doi']) for w in ch]}, timeout=90, headers=S2_HDR)
            if r.status_code == 200: break
            print('S2', r.status_code); time.sleep(10 * (a + 1))
        except Exception as e:
            print('S2 err', e); time.sleep(10)
    else: continue
    for w, res in zip(ch, r.json()):
        if res and res.get('abstract') and len(res['abstract']) >= MIN:
            w['abstract'] = res['abstract']; w['abstract_src'] = 'semanticscholar'; got_s2 += 1
        elif res and res.get('tldr') and res['tldr'].get('text'):
            w['tldr'] = res['tldr']['text']
    time.sleep(3)
print('S2 abstracts', got_s2)
need2 = [w for w in need if len(w.get('abstract') or '') < MIN]
got_cr = 0
for w in need2:
    try:
        r = requests.get('https://api.crossref.org/works/' + nd(w['doi']), timeout=40, headers=UA)
        if r.status_code == 200:
            a = r.json()['message'].get('abstract')
            if a:
                a = html.unescape(re.sub(r'<[^>]+>', ' ', a)); a = re.sub(r'\s+', ' ', a).strip()
                if len(a) >= 150: w['abstract'] = a; w['abstract_src'] = 'crossref'; got_cr += 1
    except Exception:
        pass
    time.sleep(0.15)
print('Crossref abstracts', got_cr, 'still missing', sum(1 for w in need if len(w.get('abstract') or '') < MIN))
# write enriched abstracts back into the pool so a re-score picks them up
for w in p:
    if w['id'] in raw and w.get('abstract') and len(w['abstract']) > len(raw[w['id']].get('abstract') or ''):
        raw[w['id']]['abstract'] = w['abstract']; raw[w['id']]['abstract_src'] = w.get('abstract_src')
    if w['id'] in raw and w.get('tldr'): raw[w['id']]['tldr'] = w['tldr']
json.dump(list(raw.values()), open(args.pool, 'w', encoding='utf-8'))
