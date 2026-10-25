"""Render one PDF page (or a vertical band of it) to PNG for close reading of equations/figures.

Inputs:  a PDF, a 1-based page number, a resolution in dpi, and optionally a band given as fractions
         of the page height (0 = top, 1 = bottom).
Output:  one PNG.

Example (lower half of page 6 at 250 dpi):  python -P render_page.py paper.pdf 6 250 crop.png 0.5 1.0
Requires: pymupdf.
"""
import argparse

import fitz

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('pdf'); ap.add_argument('page', type=int, help='1-based page number')
ap.add_argument('dpi', type=int); ap.add_argument('out', help='output PNG')
ap.add_argument('band', nargs='*', type=float, metavar='Y', help='optional y0_frac y1_frac')
args = ap.parse_args()

d = fitz.open(args.pdf)
if not 1 <= args.page <= len(d):
    ap.error(f'page must be 1..{len(d)}')
p = d[args.page - 1]
clip = None
if len(args.band) == 2:
    r = p.rect
    y0, y1 = args.band
    clip = fitz.Rect(r.x0, r.y0 + y0 * r.height, r.x1, r.y0 + y1 * r.height)
elif args.band:
    ap.error('give both y0_frac and y1_frac, or neither')
p.get_pixmap(dpi=args.dpi, clip=clip).save(args.out)
print('saved', args.out)
