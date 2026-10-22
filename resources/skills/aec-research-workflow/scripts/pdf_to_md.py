"""Convert downloaded PDFs (untrusted data) to Markdown full texts.

Each PDF is opened read-only with PyMuPDF; nothing inside the PDF is executed. Files that do not start
with the %PDF magic bytes are skipped. A conversion counts as text_ok when it yields more than
--min-chars characters (scanned PDFs without a text layer fail this check).

Inputs:  pdf_dir with <key>.pdf files
Outputs: md_dir/<key>.md and report.json {key: {pages, chars, text_ok} | {error, text_ok: false}}

Example: python -P pdf_to_md.py fulltext/pdf fulltext/md fulltext/convert_report.json
Requires: pymupdf, pymupdf4llm.
"""
import argparse
import json
import os

import fitz
import pymupdf4llm

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('pdf_dir'); ap.add_argument('md_dir'); ap.add_argument('report')
ap.add_argument('--min-chars', type=int, default=5000, help='minimum text length for text_ok (default: 5000)')
args = ap.parse_args()

pdf_dir, md_dir, rep_path = args.pdf_dir, args.md_dir, args.report
os.makedirs(md_dir, exist_ok=True)
rep = {}
for f in sorted(os.listdir(pdf_dir)):
    if not f.lower().endswith('.pdf'):
        continue
    key = f[:-4]
    src = os.path.join(pdf_dir, f)
    with open(src, 'rb') as fh:
        if fh.read(4) != b'%PDF':
            rep[key] = {'error': 'not a PDF (missing %PDF header)', 'text_ok': False}
            print(key, rep[key], flush=True)
            continue
    try:
        doc = fitz.open(src)
        pages = len(doc)
        try:
            md = pymupdf4llm.to_markdown(doc, show_progress=False)
        except Exception:
            md = '\n\n'.join(p.get_text() for p in doc)
        doc.close()
        ok = len(md.strip()) > args.min_chars
        open(os.path.join(md_dir, key + '.md'), 'w', encoding='utf-8').write(md)
        rep[key] = {'pages': pages, 'chars': len(md), 'text_ok': ok}
    except Exception as e:
        rep[key] = {'error': str(e)[:200], 'text_ok': False}
    print(key, rep[key], flush=True)
json.dump(rep, open(rep_path, 'w', encoding='utf-8'), indent=1)
print('converted', sum(1 for v in rep.values() if v.get('text_ok')), 'of', len(rep))
