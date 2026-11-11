# -*- coding: utf-8 -*-
"""Figure checks for publisher proofs: typography in the plotting code, and proof that a re-render changed
only what it should.

  lint SCRIPT.py...        flags the figure text that production editors query: a signed or %g number format
                           (prints a hyphen-minus for negatives; tick labels are fine, matplotlib already uses
                           U+2212), a hyphen between numbers (use an en dash), a thousands comma in a format or
                           literal (MDPI: commas only from five digits), a letter x between numbers (use the
                           multiplication sign), em dashes, and "[-]" as a unit.
  diff OLD.png NEW.png     the region in which two renders differ, as percentages of the image; "identical"
                           when they match. Unchanged scripts must re-render identically: if they do not, the
                           environment changed and every figure needs a full visual check.
  scale PNG... [--dpi 600] [--text-width-in 6.7]
                           physical size and the scale at which the figure prints at text width. Below 0.5,
                           8 pt labels print under 4 pt ("font size too small"): usually one long single-line
                           footer saved with bbox_inches="tight" has widened the canvas.

Example: python -P figure_checks.py lint plot_*.py && python -P figure_checks.py diff old/Fig8.png new/Fig8.png
Exit status 1 on lint findings, or on any difference when --expect-identical is given to diff.
"""
import argparse, ast, re, sys

MINUS = "wrap the formatted number with .replace('-', '\\u2212')"
RULES = [
    (re.compile(r"%[-#0 ]*\+[\d.]*[dfgeE]|\{[^{}]*:\+[^{}]*\}"), "signed number format: negatives print a hyphen-minus; "
     + MINUS),
    (re.compile(r"%[\d.]*[dfg]\s*(?:to|–|-)\s*%[\d.]*[dfg]|\{[^{}]*\}\s*(?:to|–)\s*\{[^{}]*\}"),
     "range of formatted numbers: a negative bound prints a hyphen-minus; " + MINUS),
    (re.compile(r"(?<![\w.])\d+(?:\.\d+)?-\d"), "hyphen between numbers: use an en dash (U+2013)"),
    (re.compile(r"\b\d+-(?:min|s|h|day|week|K|mm|cm|m|kW|W)\b"), "hyphenated number-unit compound (queried as "
     "'3-min'): write '3 min'"),
    (re.compile(r"\b[A-Za-z]{2,}-\d"), "hyphen before a number (queried as 'WWR-40%'): reads as a minus sign"),
    (re.compile(r"\{[^{}]*:,[^{}]*\}|(?<![\d,.])\d,\d{3}(?![\d,])"), "thousands comma: MDPI uses commas only from "
     "five digits"),
    (re.compile(r"\d\s?x\s?\d"), "letter x between numbers: use the multiplication sign (U+00D7)"),
    (re.compile("—"), "em dash in figure text"),
    (re.compile(r"\[-\]"), "'[-]' as a unit: omit the unit or write 'dimensionless'"),
]
PATHLIKE = re.compile(r"[/\\]|\.(png|jpe?g|pdf|svg|json|jsonl|csv|txt|py|idf|epw)$|^#[0-9a-fA-F]{3,8}$"
                      r"|^(utf|cp|latin|iso)[-_]?\d", re.I)


def _callname(n):
    f = n.func
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")


def _skipped(node, parent):
    """Inside print() (console, not figure) or already wrapped by a minus helper such as mn(...) or minus(...)."""
    for _ in range(6):
        node = parent.get(node)
        if node is None:
            return False
        if isinstance(node, ast.Call):
            name = _callname(node)
            if name == "print" or name == "mn" or "minus" in name.lower():
                return True
    return False


def lint(path):
    """Every string in a plotting script can reach a figure (titles, labels, label tables, notes), so all of
    them are checked except docstrings and path-like strings. Findings are prompts to look, not verdicts."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    docs = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and n.body:
            b = n.body[0]
            if isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant) and isinstance(b.value.value, str):
                docs.add(id(b.value))
    parent = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    finds = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.JoinedStr, ast.FormattedValue, ast.Constant)) and _skipped(n, parent):
            continue
        if isinstance(n, ast.JoinedStr):                 # f"{a}-{b}": a hyphen between two formatted values
            v = n.values
            for i in range(1, len(v) - 1):
                if (isinstance(v[i], ast.Constant) and str(v[i].value).strip() == "-"
                        and isinstance(v[i - 1], ast.FormattedValue) and isinstance(v[i + 1], ast.FormattedValue)):
                    finds.append((n.lineno, "hyphen between two formatted numbers: use an en dash (U+2013)"))
        if isinstance(n, ast.FormattedValue) and n.format_spec is not None:
            spec = "".join(str(c.value) for c in ast.walk(n.format_spec) if isinstance(c, ast.Constant))
            if "+" in spec:
                finds.append((n.lineno, "signed f-string format: negatives print a hyphen-minus; " + MINUS))
            if "," in spec:
                finds.append((n.lineno, "thousands comma in an f-string format: MDPI uses commas only from five digits"))
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs:
            s = n.value
            if len(s) < 3 or PATHLIKE.search(s.strip()):
                continue
            for rx, msg in RULES:
                if rx.search(s):
                    finds.append((n.lineno, "%s: %r" % (msg, s[:70])))
    seen = set()
    for ln, msg in sorted(finds):
        if (ln, msg) not in seen:
            seen.add((ln, msg)); print("%s:%d: %s" % (path, ln, msg))
    return len(seen)


def _open(p):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None                        # own renders at 600 dpi exceed PIL's 89 MP guard
    return Image.open(p)


def cmd_diff(a):
    from PIL import ImageChops
    x, y = _open(a.old).convert("RGB"), _open(a.new).convert("RGB")
    if x.size != y.size:
        dx, dy = x.info.get("dpi", (0,))[0] or a.dpi, y.info.get("dpi", (0,))[0] or a.dpi
        print("size changed: %dx%d (%.1f x %.1f in) -> %dx%d (%.1f x %.1f in)"
              % (x.size + (x.size[0] / dx, x.size[1] / dx) + y.size + (y.size[0] / dy, y.size[1] / dy)))
        return 1
    bb = ImageChops.difference(x, y).getbbox()
    if bb is None:
        print("identical"); return 0
    w, h = x.size
    print("changed region: x %.0f-%.0f%%, y %.0f-%.0f%% (from the top)"
          % (100 * bb[0] / w, 100 * bb[2] / w, 100 * bb[1] / h, 100 * bb[3] / h))
    return 1 if a.expect_identical else 0


def cmd_scale(a):
    low = 0
    for p in a.pngs:
        im = _open(p)
        dpi = (im.info.get("dpi") or (a.dpi,))[0] or a.dpi
        w_in, h_in = im.size[0] / dpi, im.size[1] / dpi
        s = min(1.0, a.text_width_in / w_in)
        flag = "  <- labels print at %.0f%% of their size" % (100 * s) if s < 0.5 else ""
        low += bool(flag)
        print("%s: %.1f x %.1f in at %.0f dpi, prints at %.2f of size%s" % (p, w_in, h_in, dpi, s, flag))
    return 1 if low else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("lint"); s.add_argument("scripts", nargs="+")
    s = sp.add_parser("diff"); s.add_argument("old"); s.add_argument("new")
    s.add_argument("--expect-identical", action="store_true"); s.add_argument("--dpi", type=float, default=600)
    s = sp.add_parser("scale"); s.add_argument("pngs", nargs="+"); s.add_argument("--dpi", type=float, default=600)
    s.add_argument("--text-width-in", type=float, default=6.7)
    a = ap.parse_args()
    if a.cmd == "lint":
        n = sum(lint(p) for p in a.scripts)
        print("%d findings" % n)
        sys.exit(1 if n else 0)
    sys.exit(cmd_diff(a) if a.cmd == "diff" else cmd_scale(a))


if __name__ == "__main__":
    main()
