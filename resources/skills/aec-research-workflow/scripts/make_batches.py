"""Select the screening set and split it into JSONL batches for agent coding (templates/SCREENING_PROTOCOL.md).

Screen set = records in the year range with keyword score >= --min-score (if given), plus records whose `src`
carries a --prior-tag prefix with score >= --prior-min-score. Records are sorted by score and interleaved so
every batch gets a similar mix of strong and weak candidates.

Input:   pool JSON (OpenAlex-style works, optionally with score / src / is_oa / tldr)
Outputs: <out_dir>/batch_NN.jsonl  one compact record per line: id, doi, year, venue, oa, title, abstract, keywords, tldr
         <ids_out>                 JSON list of the screened OpenAlex ids
Existing batch_*.jsonl files in out_dir are removed first.

Example: python -P make_batches.py harvest/openalex_raw.json --out-dir screen --years 2021 2026 --batch-size 100
         python -P make_batches.py harvest/pool_scored.json --min-score 20 --prior-tag prior_ --prior-min-score 12
Requires: standard library only.
"""
import argparse
import json
import os

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('pool', help='pool JSON (list of works)')
ap.add_argument('--out-dir', default='screen', help='batch folder (default: screen)')
ap.add_argument('--ids-out', help='screened-id list (default: <out_dir>/screen_ids.json)')
ap.add_argument('--years', nargs=2, type=int, metavar=('FROM', 'TO'), help='keep publication years in this range')
ap.add_argument('--min-score', type=float, help='score threshold (needs a "score" field; default: no threshold)')
ap.add_argument('--prior-tag', action='append', default=[], help='src tag prefix of prior-corpus records (repeatable)')
ap.add_argument('--prior-min-score', type=float, default=12, help='score threshold for prior-tagged records (default: 12)')
ap.add_argument('--batch-size', type=int, default=100, help='records per batch (default: 100)')
ap.add_argument('--max-abstract', type=int, default=2600, help='abstract characters kept (default: 2600)')
args = ap.parse_args()

SC = args.out_dir
os.makedirs(SC, exist_ok=True)
B = args.batch_size
pool = json.load(open(args.pool, encoding='utf-8'))
prior = lambda w: any(s.startswith(t) for t in args.prior_tag for s in w.get('src', []))
recent = lambda w: not args.years or bool(w.get('publication_year') and args.years[0] <= w['publication_year'] <= args.years[1])
score = lambda w: w.get('score', 0)
THR = args.min_score
sel = [w for w in pool if recent(w) and (THR is None or score(w) >= THR or (prior(w) and score(w) >= args.prior_min_score))]
sel.sort(key=lambda w: -score(w))
recs = []
for w in sel:
    src = (w.get('primary_location') or {}).get('source') or {}
    kw = [k.get('display_name') for k in (w.get('keywords') or [])][:8]
    oa = w['is_oa'] if 'is_oa' in w else bool((w.get('open_access') or {}).get('is_oa'))
    recs.append({'id': w['id'].split('/')[-1], 'doi': (w.get('doi') or '').replace('https://doi.org/', ''), 'year': w.get('publication_year'),
                 'venue': src.get('display_name'), 'oa': oa, 'title': w.get('title') or w.get('display_name'),
                 'abstract': (w.get('abstract') or '')[:args.max_abstract], 'keywords': kw, 'tldr': w.get('tldr', '')})
# interleave by score so every batch gets a similar mix of strong and weak candidates
nb = (len(recs) + B - 1) // B
batches = [recs[i::nb] for i in range(nb)]
for f in os.listdir(SC):
    if f.startswith('batch_') and f.endswith('.jsonl'): os.remove(os.path.join(SC, f))
for b, rs in enumerate(batches):
    with open(os.path.join(SC, f'batch_{b:02d}.jsonl'), 'w', encoding='utf-8') as fh:
        for r in rs: fh.write(json.dumps(r, ensure_ascii=False) + '\n')
json.dump([r['id'] for r in recs], open(args.ids_out or os.path.join(SC, 'screen_ids.json'), 'w'))
print('screen set', len(recs), 'batches', nb, 'sizes', [len(x) for x in batches],
      'title-only', sum(1 for r in recs if len(r['abstract']) < 200), 'prior-tagged', sum(1 for w in sel if prior(w)))
