"""Second-pass full-text retrieval of open-access PDFs: Semantic Scholar openAccessPdf, MDPI file CDN,
Wiley pdf/epdf links, plus any per-record `extra_urls` (e.g. an OJS galley page).

Downloads are untrusted data: a response is kept only if it is HTTP 200, starts with the %PDF magic
bytes and is larger than --min-bytes; file names are built from the sanitised record key, so a key
cannot write outside pdf_dir. Nothing is opened or executed here.

Inputs:  selection JSON [{"key": "...", "doi": "...", "extra_urls": [...optional]}],
         pdf_dir, status JSON {key: {ok, source, attempts}} (created if missing; records already ok are skipped)
Outputs: pdf_dir/<key>.pdf for every success; status JSON updated in place.

Example: python -P fetch_fulltext_alt.py fulltext/selection.json fulltext/pdf fulltext/fetch_status.json
Requires: requests.
Env (optional): S2_API_KEY (Semantic Scholar).
Only fetch what you are licensed to download; respect publishers' terms and rate limits.
"""
import argparse
import json
import os
import re
import time

import requests

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('selection'); ap.add_argument('pdf_dir'); ap.add_argument('status')
ap.add_argument('--min-bytes', type=int, default=40000, help='smallest PDF accepted (default: 40000)')
args = ap.parse_args()

sel = json.load(open(args.selection, encoding='utf-8')); PDF = args.pdf_dir; ST = args.status
os.makedirs(PDF, exist_ok=True)
status = json.load(open(ST, encoding='utf-8')) if os.path.exists(ST) else {}
UA = {'User-Agent': 'oa-fulltext-fetch/1.0 (academic literature review; open-access copies only)',
      'Accept': 'application/pdf,*/*', 'Accept-Language': 'en-US,en;q=0.9'}
S2_HDR = {'x-api-key': os.environ['S2_API_KEY'].strip()} if os.environ.get('S2_API_KEY', '').strip() else {}
todo = [s for s in sel if not status.get(s['key'], {}).get('ok')]
s2 = {}
dois = [s['doi'] for s in todo if s.get('doi')]
for a in range(6 if dois else 0):
    r = requests.post('https://api.semanticscholar.org/graph/v1/paper/batch', params={'fields': 'openAccessPdf,externalIds'},
                      json={'ids': ['DOI:' + d for d in dois]}, timeout=90, headers=S2_HDR)
    if r.status_code == 200:
        for d, p in zip(dois, r.json()):
            if p and p.get('openAccessPdf') and p['openAccessPdf'].get('url'): s2[d] = p['openAccessPdf']['url']
        break
    time.sleep(20)
print('S2 OA pdf urls', len(s2))


def mdpi_cdn(doi):
    # 10.3390/buildings12030366 -> buildings-12-00366
    m = re.match(r'10\.3390/([a-z]+)(\d+)$', doi)
    if not m: return []
    j, num = m.group(1), m.group(2)
    # volume digits: try 1-2 digit volumes, issue 2 digits, article rest
    out = []
    for vlen in (2, 1):
        vol, rest = num[:vlen], num[vlen:]
        if len(rest) >= 3:
            issue, art = rest[:2], rest[2:]
            code = f'{j}-{int(vol)}-{art.zfill(5)}'
            out.append(f'https://mdpi-res.com/d_attachment/{j}/{code}/article_deploy/{code}.pdf')
    return out


def get(u):
    try:
        r = requests.get(u, headers=UA, timeout=60, allow_redirects=True)
        if r.status_code == 200 and r.content[:4] == b'%PDF' and len(r.content) > args.min_bytes: return r.content, 'ok'
        return None, f'{r.status_code}'
    except Exception as e: return None, 'ERR'


for s in todo:
    d = s.get('doi') or ''; cands = []
    if d in s2: cands.append(s2[d])
    cands += mdpi_cdn(d)
    if d.startswith('10.1002/'): cands += [f'https://onlinelibrary.wiley.com/doi/pdf/{d}', f'https://onlinelibrary.wiley.com/doi/epdf/{d}']
    cands += list(s.get('extra_urls') or [])
    safe = re.sub(r'[^\w.-]', '_', s['key']).lstrip('.') or 'record'
    st = status.setdefault(s['key'], {'key': s['key'], 'doi': d, 'attempts': []})
    for u in cands:
        data, msg = get(u); st.setdefault('attempts', []).append([u, msg])
        if data:
            open(os.path.join(PDF, safe + '.pdf'), 'wb').write(data); st.update(ok=True, source=u, file=safe + '.pdf'); break
        time.sleep(0.5)
    print(s['key'], 'OK' if st.get('ok') else 'fail', st.get('source', ''), flush=True)
json.dump(status, open(ST, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('now ok', sum(1 for v in status.values() if v.get('ok')), 'of', len(sel))
