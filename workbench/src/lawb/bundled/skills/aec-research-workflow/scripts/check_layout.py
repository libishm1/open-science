# -*- coding: utf-8 -*-
"""Layout check for PDF renditions of a manuscript.

Flags, per page:
  EDGE     text or images beyond the right/left page margin or below the bottom margin
  ORPHAN   a table or figure caption in the bottom part of a page (its table/figure is probably on the next page)
It also lists where each table and figure caption lands, so pairs split across pages can be read off.

Inputs:  one or more PDFs
Output:  a report on stdout

Example: python check_layout.py manuscript.pdf supplementary.pdf
         python check_layout.py --side 36 --bottom 24 --orphan 0.85 manuscript.pdf
Requires: pymupdf.
"""
import argparse, re, sys
import fitz

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("pdfs", nargs="+")
ap.add_argument("--side", type=float, default=18, help="left/right edge zone in pt (default: 18)")
ap.add_argument("--bottom", type=float, default=12, help="bottom edge zone in pt (default: 12)")
ap.add_argument("--orphan", type=float, default=0.88, help="caption below this fraction of page height is flagged (default: 0.88)")
args = ap.parse_args()

sys.stdout.reconfigure(encoding="utf-8")
CAP = re.compile(r"^(Table|Figure|Fig\.)\s*(S?\d+)[.:]")
for path in args.pdfs:
    doc = fitz.open(path)
    flags, where = [], {}
    for pno, page in enumerate(doc, 1):
        W, H = page.rect.width, page.rect.height
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            x0, y0, x1, y1 = b["bbox"]
            kind = "image" if b["type"] == 1 else "text"
            if x1 > W - args.side or x0 < args.side or y1 > H - args.bottom:
                txt = "" if kind == "image" else " ".join(s["text"] for l in b["lines"] for s in l["spans"])[:60]
                flags.append("p%-3d EDGE   %s bbox=(%.0f,%.0f,%.0f,%.0f) %s" % (pno, kind, x0, y0, x1, y1, txt))
            if kind == "text":
                first = " ".join(s["text"] for s in b["lines"][0]["spans"]).strip() if b["lines"] else ""
                m = CAP.match(first)
                if m:
                    key = m.group(1)[0] + m.group(2)
                    where.setdefault(key, pno)
                    if y0 > args.orphan * H:
                        flags.append("p%-3d ORPHAN %s caption at y=%.0f of %.0f" % (pno, key, y0, H))
    print("==", path, "(%d pages)" % len(doc))
    for f in flags:
        print("  ", f)
    if not flags:
        print("   no edge overruns or orphaned captions")
    tabs = sorted((k, v) for k, v in where.items() if k.startswith("T"))
    figs = sorted((k, v) for k, v in where.items() if k.startswith("F"))
    print("   tables on pages:", ", ".join("%s:p%d" % kv for kv in sorted(tabs, key=lambda kv: (len(kv[0]), kv[0]))))
    print("   figures on pages:", ", ".join("%s:p%d" % kv for kv in sorted(figs, key=lambda kv: (len(kv[0]), kv[0]))))
