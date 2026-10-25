"""Collect the MISMATCH numeric checks of the given papers into one adversarial-review batch
(the input of templates/REVIEW_PROTOCOL.md).

Inputs:  <equations_dir>/<key>.json files from Stage 2 (numeric_checks entries with status "MISMATCH")
Output:  out JSON {"keys": [...], "items": [{id "<key>#<index>", key, check_index, what, paper_value, recomputed, lean}]}

Example: python -P make_review_batch.py work/eqpipe/equations work/eqpipe/mismatch_review/batch0.json Smith2024 Lee2025
Requires: standard library only.
"""
import argparse
import json
import os

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('equations_dir'); ap.add_argument('out', help='batch JSON to write')
ap.add_argument('keys', nargs='+', help='paper keys')
args = ap.parse_args()

KEYS = args.keys
items = []
for k in KEYS:
    e = json.load(open(os.path.join(args.equations_dir, k + '.json'), encoding='utf-8'))
    for i, c in enumerate(e.get('numeric_checks', [])):
        if c.get('status') == 'MISMATCH':
            items.append({'id': f'{k}#{i}', 'key': k, 'check_index': i, 'what': c.get('what'), 'paper_value': c.get('paper_value'),
                          'recomputed': c.get('recomputed'), 'lean': c.get('lean')})
out = args.out
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
json.dump({'keys': KEYS, 'items': items}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(out, len(items), {k: sum(1 for x in items if x['key'] == k) for k in KEYS})
