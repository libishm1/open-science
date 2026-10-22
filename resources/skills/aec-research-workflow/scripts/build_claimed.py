"""Write the inputs for the double-blind DOI check of a corpus.

Inputs:  corpus JSON, a list of records with doi, title, year, first_author, venue.
Outputs: <out_dir>/dois_all.txt   plain DOI list (the only thing runs A and B see)
         <out_dir>/claimed.json   {doi: {title, year, first_author, venue}} as recorded in the corpus
                                  (used only by verify_reconcile.py)

Example: python -P build_claimed.py screen/corpus.json --out-dir verify
Requires: standard library only.
"""
import argparse
import json
import os

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('corpus', help='corpus JSON (list of records)')
ap.add_argument('--out-dir', default='verify', help='output folder (default: verify)')
args = ap.parse_args()

V = args.out_dir
os.makedirs(V, exist_ok=True)
C = json.load(open(args.corpus, encoding='utf-8'))
claimed = {}
for r in C:
    if r.get('doi'):
        claimed[r['doi']] = {'title': r['title'], 'year': r['year'], 'first_author': r.get('first_author') or '', 'venue': r.get('venue') or ''}
open(os.path.join(V, 'dois_all.txt'), 'w', encoding='utf-8').write('\n'.join(sorted(claimed)) + '\n')
json.dump(claimed, open(os.path.join(V, 'claimed.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('DOIs', len(claimed), 'corpus without DOI', sum(1 for r in C if not r.get('doi')))
