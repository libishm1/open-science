"""BLIND RUN A: Crossref REST + doi.org Handle registry.

Input:  a plain list of DOIs only (no claimed metadata is visible to this run).
Output: JSON {doi: {...}} with the handle-registry status and the Crossref record.

Example: python -P verify_run_A.py verify/dois_all.txt verify/runA.json
Requires: requests.
Env: CROSSREF_MAILTO (optional) adds a contact address to the User-Agent (Crossref polite pool).
"""
import argparse
import concurrent.futures as cf
import json
import os
import time

import requests

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('dois', help='text file, one DOI per line')
ap.add_argument('out', help='output JSON')
ap.add_argument('--workers', type=int, default=6, help='parallel requests (default: 6)')
args = ap.parse_args()

dois = [l.strip().lower() for l in open(args.dois, encoding='utf-8') if l.strip()]
out = args.out
_mail = os.environ.get('CROSSREF_MAILTO', '').strip()
UA = {'User-Agent': 'doi-verification-script/1.0 (academic literature review' + (f'; mailto:{_mail}' if _mail else '') + ')'}


def handle(d):
    err = ''
    for a in range(3):
        try:
            r = requests.get('https://doi.org/api/handles/' + d, timeout=30, headers=UA)
            j = r.json(); rc = j.get('responseCode')
            url = next((v['data']['value'] for v in j.get('values', []) if v.get('type') == 'URL'), None)
            return {'handle_exists': rc == 1, 'handle_code': rc, 'resolves_to': url}
        except Exception as e:
            err = str(e); time.sleep(2)
    return {'handle_exists': None, 'handle_error': err}


def crossref(d):
    err = 'rate-limited'
    for a in range(4):
        try:
            r = requests.get('https://api.crossref.org/works/' + requests.utils.quote(d, safe='/:;()'), timeout=40, headers=UA)
            if r.status_code == 404: return {'cr_found': False}
            if r.status_code in (429, 503): time.sleep(3 * (a + 1)); continue
            m = r.json()['message']
            def yr(k):
                v = m.get(k, {}).get('date-parts', [[None]])[0][0]; return v
            au = m.get('author') or []
            upd = [u.get('type') for u in (m.get('updated-by') or [])]
            return {'cr_found': True, 'cr_title': (m.get('title') or [''])[0], 'cr_subtitle': (m.get('subtitle') or [''])[0] if m.get('subtitle') else '',
                    'cr_container': (m.get('container-title') or [''])[0], 'cr_type': m.get('type'),
                    'cr_year_issued': yr('issued'), 'cr_year_print': yr('published-print'), 'cr_year_online': yr('published-online'),
                    'cr_first_author': (au[0].get('family') or au[0].get('name') or '') if au else '',
                    'cr_authors': [a.get('family') or a.get('name') or '' for a in au][:30],
                    'cr_publisher': m.get('publisher'), 'cr_volume': m.get('volume'), 'cr_page': m.get('page') or m.get('article-number'),
                    'cr_updated_by': upd, 'cr_is_retracted_notice': any('retract' in (t or '') for t in upd),
                    'cr_license': [l.get('URL') for l in (m.get('license') or [])][:2]}
        except Exception as e:
            err = str(e); time.sleep(2)
    return {'cr_found': None, 'cr_error': err}


def one(d):
    rec = {'doi': d}; rec.update(handle(d)); rec.update(crossref(d)); return rec


res = {}
with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
    for i, rec in enumerate(ex.map(one, dois)):
        res[rec['doi']] = rec
        if i % 50 == 0: print('A', i, flush=True)
json.dump(res, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('RUN A done', len(res), 'handle ok', sum(1 for r in res.values() if r.get('handle_exists')), 'crossref found', sum(1 for r in res.values() if r.get('cr_found')))
