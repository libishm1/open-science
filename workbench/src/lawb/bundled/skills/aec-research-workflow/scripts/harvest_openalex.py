"""Systematic OpenAlex harvest driven by a queries file.
Each query string is logged with its hit count (PRISMA identification stage).

Input:  a JSON (or YAML, needs PyYAML) queries file, see templates/harvest_queries.example.json:
        {"date_from": "2021-01-01", "date_to": "2026-12-31", "types": "article|review", "default_cap": 600,
         "blocks": {"NAME": "(... OR ...)"},                 # reusable fragments, written as {NAME} in queries
         "queries": {"Q01_id": "query string" | {"query": "...", "cap": 800}}}
Output: <out_dir>/openalex_raw.json  unique works (abstract rebuilt from the inverted index, plus the
                                      ids of the queries that found them and their relevance rank)
        <out_dir>/search_log.json    per query: expanded query string, total hits, records retrieved

Example: python -P harvest_openalex.py templates/harvest_queries.example.json harvest
Requires: requests (PyYAML only for .yaml/.yml query files).
Env (optional): OPENALEX_API_KEY, OPENALEX_MAILTO.
"""
import argparse
import json
import os
import re
import time

import requests


def inv2abs(ii):
    if not ii: return ''
    pos = {}
    for w, ps in ii.items():
        for p in ps: pos[p] = w
    return ' '.join(pos[k] for k in sorted(pos))


SEL = 'id,doi,title,display_name,publication_year,publication_date,type,primary_location,open_access,best_oa_location,cited_by_count,authorships,abstract_inverted_index,language,topics,keywords,fwci,biblio'


def load_config(path):
    if path.lower().endswith(('.yaml', '.yml')):
        import yaml
        cfg = yaml.safe_load(open(path, encoding='utf-8'))
    else:
        cfg = json.load(open(path, encoding='utf-8'))
    blocks = cfg.get('blocks') or {}
    expand = lambda s: re.sub(r'\{(\w+)\}', lambda m: blocks[m.group(1)] if m.group(1) in blocks else m.group(0), s)
    Q, CAP = {}, {}
    for qid, q in cfg['queries'].items():
        q = q if isinstance(q, dict) else {'query': q}
        Q[qid] = expand(q['query'])
        CAP[qid] = int(q.get('cap', cfg.get('default_cap', 600)))
    return cfg, Q, CAP


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('queries', help='queries file (.json, .yaml or .yml)')
    ap.add_argument('out_dir', nargs='?', default='harvest', help='output folder (default: harvest)')
    args = ap.parse_args()
    cfg, Q, CAP = load_config(args.queries)
    OUT = args.out_dir
    os.makedirs(OUT, exist_ok=True)
    d0, d1 = cfg.get('date_from', '2021-01-01'), cfg.get('date_to', '2026-12-31')
    types = cfg.get('types', 'article|review')
    auth = {k: v for k, v in (('api_key', os.environ.get('OPENALEX_API_KEY', '').strip()),
                              ('mailto', os.environ.get('OPENALEX_MAILTO', '').strip())) if v}
    log = {}; recs = {}
    for qid, q in Q.items():
        cursor = '*'; n = 0; total = None
        while cursor and n < CAP[qid]:
            flt = f'title_and_abstract.search:{q},from_publication_date:{d0},to_publication_date:{d1}' + (f',type:{types}' if types else '')
            params = {'filter': flt, 'per_page': 200, 'cursor': cursor, 'select': SEL, 'sort': 'relevance_score:desc', **auth}
            for attempt in range(4):
                try:
                    r = requests.get('https://api.openalex.org/works', params=params, timeout=60)
                    if r.status_code == 200: break
                    print(qid, 'HTTP', r.status_code, r.text[:200]); time.sleep(3)
                except Exception as e:
                    print(qid, 'ERR', e); time.sleep(3)
            else:
                break
            j = r.json(); total = j['meta']['count']
            for w in j['results']:
                n += 1
                wid = w['id']
                if wid not in recs:
                    w['abstract'] = inv2abs(w.pop('abstract_inverted_index', None))
                    w['queries'] = []; w['rel_rank'] = {}
                    recs[wid] = w
                recs[wid]['queries'].append(qid); recs[wid]['rel_rank'][qid] = n
            cursor = j['meta'].get('next_cursor')
            if not j['results']: break
            time.sleep(0.3)
        log[qid] = {'query': q, 'date_from': d0, 'date_to': d1, 'total_hits': total, 'retrieved': n}
        print(f'{qid}: total={total} retrieved={n} unique_so_far={len(recs)}', flush=True)
    json.dump(list(recs.values()), open(os.path.join(OUT, 'openalex_raw.json'), 'w', encoding='utf-8'))
    json.dump(log, open(os.path.join(OUT, 'search_log.json'), 'w', encoding='utf-8'), indent=1)
    print('UNIQUE', len(recs))
