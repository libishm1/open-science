"""Extract a zip of PDFs into an empty folder (no path traversal), then identify each PDF by the DOI printed in it.

The zip is untrusted: only *.pdf members are extracted, absolute paths, drive letters and '..' components are
refused, each member is capped at --max-mb, files are flattened to their (sanitised) base name, and a file
without the %PDF magic bytes is reported and not opened. PDFs are opened read-only with PyMuPDF.

Inputs:  zip, empty output folder, --corpus corpus.json (records with doi, title[, first_author, year, citation]),
         optional --fulltext selection.json ([{key, doi}], gives the per-paper key) and
         --request-list TAG=dois.txt (repeatable; tags a PDF whose DOI is on that list).
Outputs: one printed line per PDF; with --map-out, map.json {file name: {key, doi, citation}} for every PDF
         that matched a key (the input of convert_incoming.py).

Example: python -I unzip_identify.py papers.zip incoming/batch1 --corpus screen/corpus.json \
             --fulltext fulltext/selection.json --request-list essential=req_A.txt --map-out incoming/batch1_map.json
Requires: pymupdf.
"""
import argparse
import json
import os
import re
import zipfile

import fitz

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('zip'); ap.add_argument('out_dir', help='empty (or new) folder for the extracted PDFs')
ap.add_argument('--corpus', required=True, help='corpus JSON (list of records with doi, title)')
ap.add_argument('--fulltext', help='full-text selection JSON [{key, doi}]')
ap.add_argument('--request-list', action='append', default=[], metavar='TAG=FILE', help='DOI list to tag matches with (repeatable)')
ap.add_argument('--map-out', help='write {file: {key, doi, citation}} for convert_incoming.py')
ap.add_argument('--max-mb', type=float, default=200, help='largest member extracted, MB (default: 200)')
args = ap.parse_args()

ZIP, OUT = args.zip, args.out_dir
os.makedirs(OUT, exist_ok=True)
assert not os.listdir(OUT), 'output folder must be empty'
LIMIT = int(args.max_mb * 1024 * 1024)
z = zipfile.ZipFile(ZIP)
for i in z.infolist():
    if i.is_dir():
        continue
    n = i.filename.replace('\\', '/')
    assert '..' not in n.split('/') and not n.startswith('/') and ':' not in n, n
    if not n.lower().endswith('.pdf'):
        print('skipped (not .pdf):', n); continue
    if i.file_size > LIMIT:
        print('skipped (too large):', n, i.file_size); continue
    base = re.sub(r'[^\w.\- ()+,]', '_', os.path.basename(n)).lstrip('.') or 'file.pdf'
    dst, k = os.path.join(OUT, base), 1
    while os.path.exists(dst):                       # same name in two folders of the zip
        k += 1; dst = os.path.join(OUT, f'{k}__{base}')
    with z.open(i) as s:
        data = s.read(LIMIT + 1)                     # the header size can lie; never read past the cap
    if len(data) > LIMIT:
        print('skipped (too large):', n); continue
    with open(dst, 'wb') as d:
        d.write(data)

C = json.load(open(args.corpus, encoding='utf-8'))
by_doi = {(r.get('doi') or '').lower(): r for r in C if r.get('doi')}
ft = {(f.get('doi') or '').lower(): f['key'] for f in json.load(open(args.fulltext, encoding='utf-8')) if f.get('doi')} if args.fulltext else {}
REQ = []
for spec in args.request_list:
    tag, _, path = spec.partition('=')
    REQ.append((tag, {l.strip().lower() for l in open(path, encoding='utf-8') if l.strip()}))
known = lambda x: x in by_doi or x in ft or any(x in s for _, s in REQ)
fmap = {}
for f in sorted(os.listdir(OUT)):
    with open(os.path.join(OUT, f), 'rb') as fh:
        if fh.read(4) != b'%PDF':
            print(f'{f[:60]:60s} NOT A PDF (no %PDF header) - not opened'); continue
    d = fitz.open(os.path.join(OUT, f))
    txt = ' '.join(d[i].get_text() for i in range(min(2, d.page_count)))
    dois = [x.rstrip('.,;)').lower() for x in re.findall(r'10\.\d{4,9}/[^\s"<>]+', txt)]
    doi = next((x for x in dois if known(x)), dois[0] if dois else '')
    r = by_doi.get(doi, {})
    tag = next((t for t, s in REQ if doi in s), 'not on list' if REQ else '-')
    key = ft.get(doi) or r.get('key')
    if key:
        cit = r.get('citation') or ' '.join(str(x) for x in (r.get('first_author'), f"({r['year']})." if r.get('year') else '', r.get('title')) if x)
        fmap[f] = {'key': key, 'doi': doi, 'citation': cit}
    print(f'{f[:60]:60s} pages {d.page_count:>3} | doi {doi or "-":38s} | {tag:20s} | key={key or "-":22s} | {(r.get("title") or "")[:70]}')
    d.close()
if args.map_out:
    json.dump(fmap, open(args.map_out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('map', len(fmap), 'of', len(os.listdir(OUT)), 'files ->', args.map_out, '(check and add unmatched files by hand)')
