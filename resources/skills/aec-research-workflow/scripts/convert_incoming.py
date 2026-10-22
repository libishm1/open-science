"""Stage 1: convert downloaded PDFs into per-paper Markdown folders for Stage 2 (templates/STAGE2_PROTOCOL.md).

For each PDF listed in the map: copy it to <out_root>/fulltext_pdf/<key>.pdf, run PyMuPDF4LLM with image
extraction (raster images and vector-graphic regions), rename images to <key>_pNN_MM.png, render every page
for transcription, flag pages that probably hold display equations, and write an image inventory.
PDFs are untrusted data: a file without the %PDF magic bytes is skipped, keys must be plain file names, and
each PDF is opened read-only with PyMuPDF; nothing inside it is executed.

Inputs:  --src folder of PDFs, --map map.json {file name: {"key", "doi", "citation"[, "extract": true]}}
         (from unzip_identify.py --map-out, or written by hand)
Outputs: <out_root>/fulltext_pdf/<key>.pdf
         <out_root>/fulltext_md/<key>/<key>.md (+ images/)        front matter: key, doi, citation, pages
         <work>/eqpipe/pages/<key>/p-NN.png                       page renders
         <work>/eqpipe/inventory_<key>.json                       images with context, eq_candidate_pages
         <work>/eqpipe/index.json                                 merged across batches (same key replaced)

Example: python -P convert_incoming.py --src incoming/batch1 --map incoming/batch1_map.json --out-root review --work work
Requires: pymupdf, pymupdf4llm.
"""
import argparse
import datetime
import json
import os
import re
import shutil

import fitz
import pymupdf4llm

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--src', required=True, help='folder with the downloaded PDFs')
ap.add_argument('--map', required=True, help='map.json {file name: {key, doi, citation}}')
ap.add_argument('--out-root', default='.', help='holds fulltext_pdf/ and fulltext_md/ (default: .)')
ap.add_argument('--work', default='work', help='scratch folder for eqpipe/ (default: work)')
ap.add_argument('--image-dpi', type=int, default=200, help='image extraction resolution (default: 200)')
ap.add_argument('--page-dpi', type=int, default=120, help='page render resolution (default: 120)')
args = ap.parse_args()

S, LR, INC = args.work, args.out_root, args.src
FMAP = json.load(open(args.map, encoding='utf-8'))
TODAY = datetime.date.today().isoformat()
P4L = getattr(pymupdf4llm, '__version__', None) or getattr(pymupdf4llm, 'version', '?')
for sub in (os.path.join(LR, 'fulltext_pdf'), os.path.join(LR, 'fulltext_md'), os.path.join(S, 'eqpipe')):
    os.makedirs(sub, exist_ok=True)

out_index = []
for fn in sorted(os.listdir(INC)):
    if not fn.lower().endswith('.pdf'):
        continue
    if fn not in FMAP:
        print('UNMATCHED', fn)
        continue
    key = FMAP[fn]['key']
    if not re.fullmatch(r'[\w.-]+', key) or key.startswith('.'):
        print('BAD KEY (letters, digits, _ . - only)', fn, key)
        continue
    row = {'doi': FMAP[fn].get('doi'), 'citation': FMAP[fn].get('citation'), 'save_as': key + '.pdf'}
    src = os.path.join(INC, fn)
    with open(src, 'rb') as fh:
        if fh.read(4) != b'%PDF':
            print('NOT A PDF (no %PDF header)', fn)
            continue
    shutil.copyfile(src, os.path.join(LR, 'fulltext_pdf', key + '.pdf'))
    pdir = os.path.join(LR, 'fulltext_md', key)
    idir = os.path.join(pdir, 'images')
    if os.path.isdir(pdir):
        try:
            shutil.rmtree(pdir)
        except PermissionError:   # cloud-sync clients can lock an empty folder: delete the files, keep the folders
            for root, _, files in os.walk(pdir):
                for f in files:
                    os.remove(os.path.join(root, f))
    os.makedirs(idir, exist_ok=True)
    doc = fitz.open(src)
    tmp_img = os.path.join(S, 'eqpipe', 'tmpimg', key)
    if os.path.isdir(tmp_img):
        shutil.rmtree(tmp_img)
    os.makedirs(tmp_img)
    md = pymupdf4llm.to_markdown(doc, write_images=True, image_path=tmp_img, image_format='png', dpi=args.image_dpi, show_progress=False)
    # rename images and rewrite links to images/<key>_pNN_MM.png
    inv = []
    def relink(m):
        old = m.group(1)
        base = os.path.basename(old)
        mm = re.search(r'-(\d{4})-(\d+)\.png$', base)
        page = int(mm.group(1)) if mm else 0
        new = f'{key}_p{page:02d}_{int(mm.group(2)):02d}.png' if mm else base
        srcp = os.path.join(tmp_img, base)
        if os.path.exists(srcp) and not os.path.exists(os.path.join(idir, new)):
            shutil.move(srcp, os.path.join(idir, new))
            try:
                pix = fitz.Pixmap(os.path.join(idir, new))
                wh = (pix.width, pix.height)
            except Exception:
                wh = (None, None)
            inv.append({'file': 'images/' + new, 'page': page, 'bytes': os.path.getsize(os.path.join(idir, new)),
                        'width': wh[0], 'height': wh[1]})
        return f'![](images/{new})'
    md = re.sub(r'!\[[^\]]*\]\(([^)]+)\)', relink, md)
    # caption/context snippets for each image
    for it in inv:
        i = md.find(it['file'])
        after = re.sub(r'\s+', ' ', md[i + len(it['file']) + 1:i + 400])
        before = re.sub(r'\s+', ' ', md[max(0, i - 300):i - 4])
        it['context_before'] = before[-200:]
        it['context_after'] = after[:300]
    shutil.rmtree(tmp_img, ignore_errors=True)
    # page renders for transcription and figure checking
    pg_dir = os.path.join(S, 'eqpipe', 'pages', key)
    os.makedirs(pg_dir, exist_ok=True)
    eq_pages = []
    for pno in range(len(doc)):
        page = doc[pno]
        page.get_pixmap(dpi=args.page_dpi).save(os.path.join(pg_dir, f'p-{pno + 1:02d}.png'))
        txt = page.get_text()
        fonts = ' '.join(f[3] for f in page.get_fonts())
        if re.search(r'\(\s*\d{1,2}[a-z]?\s*\)\s*$', txt, re.M) or re.search(r'Math|CMMI|CMSY|CMEX|Symbol|MT Extra|Cambria Math', fonts):
            eq_pages.append(pno + 1)
    header = (f"---\nkey: {key}\ndoi: {row['doi'] or 'none'}\ncitation: \"{(row['citation'] or '').replace(chr(34), chr(39))}\"\n"
              f"source_pdf: ../../fulltext_pdf/{key}.pdf\npages: {len(doc)}\nconverted: {TODAY} (PyMuPDF4LLM {P4L}; images {args.image_dpi} dpi)\n---\n\n")
    open(os.path.join(pdir, key + '.md'), 'w', encoding='utf-8').write(header + md)
    json.dump({'key': key, 'doi': row['doi'], 'pages': len(doc), 'eq_candidate_pages': eq_pages, 'images': inv,
               'page_renders': pg_dir, 'extract': bool(FMAP[fn].get('extract'))},
              open(os.path.join(S, 'eqpipe', 'inventory_' + key + '.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    out_index.append({'key': key, 'file': fn, 'pages': len(doc), 'images': len(inv), 'eq_pages': len(eq_pages), 'chars': len(md)})
    print(f"{key:34s} pages {len(doc):3d} images {len(inv):3d} eq-pages {len(eq_pages):2d} chars {len(md)}", flush=True)
    doc.close()
IDX = os.path.join(S, 'eqpipe', 'index.json')
if os.path.exists(IDX):   # later batch: replace entries with the same key, keep the rest
    new_keys = {r['key'] for r in out_index}
    out_index = [r for r in json.load(open(IDX, encoding='utf-8')) if r['key'] not in new_keys] + out_index
json.dump(out_index, open(IDX, 'w', encoding='utf-8'), indent=1)
print('DONE', len(out_index), 'entries in index')
