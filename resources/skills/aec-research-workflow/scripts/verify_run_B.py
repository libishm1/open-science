"""BLIND RUN B: OpenAlex (batched) + Semantic Scholar Graph (batched) + DataCite (fallback).

Input:  a plain list of DOIs only (no claimed metadata is visible to this run).
Output: JSON {doi: {...}} with each service's independent record.

Example: python -P verify_run_B.py verify/dois_all.txt verify/runB.json
Requires: requests.
Env (all optional): OPENALEX_API_KEY, OPENALEX_MAILTO (OpenAlex polite pool),
                    S2_API_KEY (Semantic Scholar; without it the shared unauthenticated pool is used).
"""
import argparse
import json
import os
import time

import requests

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('dois', help='text file, one DOI per line')
ap.add_argument('out', help='output JSON')
args = ap.parse_args()

dois = [l.strip().lower() for l in open(args.dois, encoding='utf-8') if l.strip()]
out = args.out
UA = {'User-Agent': 'doi-verification-script/1.0 (academic literature review)'}
OA_AUTH = {k: v for k, v in (('api_key', os.environ.get('OPENALEX_API_KEY', '').strip()),
                             ('mailto', os.environ.get('OPENALEX_MAILTO', '').strip())) if v}
S2_HDR = dict(UA, **({'x-api-key': os.environ['S2_API_KEY'].strip()} if os.environ.get('S2_API_KEY', '').strip() else {}))
res = {d: {'doi': d} for d in dois}

# --- OpenAlex: 50 DOIs per call -------------------------------------------
for i in range(0, len(dois), 50):
    ch = dois[i:i + 50]
    r = None
    for a in range(4):
        try:
            r = requests.get('https://api.openalex.org/works',
                             params={'filter': 'doi:' + '|'.join(ch), 'per_page': 50,
                                     'select': 'doi,title,publication_year,authorships,primary_location,is_retracted,type', **OA_AUTH},
                             timeout=90, headers=UA)
            if r.status_code == 200:
                break
            print('OA', r.status_code, r.text[:120])
            time.sleep(5 * (a + 1))
        except Exception as e:
            print('OA err', e)
            time.sleep(5)
    if r is None or r.status_code != 200:
        for d in ch:
            res[d]['oa_found'] = None
        continue
    for w in r.json()['results']:
        d = (w.get('doi') or '').replace('https://doi.org/', '').lower()
        if d not in res:
            continue
        au = w.get('authorships') or []
        fa = ''
        if au and au[0].get('author') and au[0]['author'].get('display_name'):
            fa = au[0]['author']['display_name'].split()[-1]
        src = ((w.get('primary_location') or {}).get('source') or {}).get('display_name')
        res[d].update({'oa_found': True, 'oa_title': w.get('title'), 'oa_year': w.get('publication_year'),
                       'oa_first_author': fa, 'oa_venue': src, 'oa_is_retracted': w.get('is_retracted'),
                       'oa_type': w.get('type')})
    time.sleep(0.5)
for d in res:
    res[d].setdefault('oa_found', False)

# --- Semantic Scholar: 400 per call, patient backoff (shared unauthenticated pool) ---
for i in range(0, len(dois), 400):
    ch = dois[i:i + 400]
    ok = False
    for a in range(8):
        try:
            r = requests.post('https://api.semanticscholar.org/graph/v1/paper/batch',
                              params={'fields': 'title,year,authors,venue,publicationVenue,externalIds'},
                              json={'ids': ['DOI:' + d for d in ch]}, timeout=120, headers=S2_HDR)
            if r.status_code == 200:
                ok = True
                break
            print('S2', r.status_code)
            time.sleep(15 * (a + 1))
        except Exception as e:
            print('S2 err', e)
            time.sleep(15)
    if not ok:
        for d in ch:
            res[d]['s2_found'] = None
        continue
    for d, p in zip(ch, r.json()):
        if p:
            au = p.get('authors') or []
            fa = au[0]['name'].split()[-1] if au and au[0].get('name') else ''
            res[d].update({'s2_found': True, 's2_title': p.get('title'), 's2_year': p.get('year'),
                           's2_first_author': fa,
                           's2_venue': p.get('venue') or ((p.get('publicationVenue') or {}).get('name'))})
        else:
            res[d]['s2_found'] = False
    time.sleep(3)

# --- DataCite: only for DOIs neither OpenAlex nor S2 knows (Zenodo, figshare, theses) ---
for d in [d for d, r in res.items() if not r.get('oa_found') and not r.get('s2_found')]:
    try:
        r = requests.get('https://api.datacite.org/dois/' + d, timeout=30, headers=UA)
        if r.status_code == 200:
            a = r.json()['data']['attributes']
            cr = (a.get('creators') or [{}])[0]
            res[d].update({'dc_found': True, 'dc_title': (a.get('titles') or [{}])[0].get('title'),
                           'dc_year': a.get('publicationYear'),
                           'dc_first_author': cr.get('familyName') or cr.get('name') or ''})
        else:
            res[d]['dc_found'] = False
    except Exception as e:
        res[d]['dc_found'] = None
        res[d]['dc_error'] = str(e)[:100]

json.dump(res, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('RUN B done', len(res),
      'openalex', sum(1 for r in res.values() if r.get('oa_found')),
      's2', sum(1 for r in res.values() if r.get('s2_found')),
      's2 unknown(rate-limit)', sum(1 for r in res.values() if r.get('s2_found') is None))
