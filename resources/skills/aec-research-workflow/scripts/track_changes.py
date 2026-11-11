# -*- coding: utf-8 -*-
"""Real Word tracked changes (w:ins / w:del) on a publisher-formatted DOCX, plus a clean copy.

After the first review round many journals return their own formatted DOCX (with line numbers) and want the
revision marked on it. Rebuilding from your own source loses their layout and the line numbers the reviewers
quote. This script edits that file directly: each edit is a revision the editor can accept or reject, and the
inserted text takes the paragraph's body formatting (<i>, <b>, <sub>, <sup> markup allowed in new text).

Usage
  python -P track_changes.py IN.docx EDITS.json OUT_tracked.docx [--clean OUT_clean.docx]
                             [--author "Corresponding Author"] [--date 2026-10-28T12:00:00Z]

EDITS.json is a list applied in order; "para" selects one paragraph (first by prefix, then by substring; it must
match exactly one paragraph):
  {"para": "The baseline weather of", "old": "a typical year", "new": "a typical meteorological year"}
  {"para": "...", "old": "...", "new": "...", "keep": true}          # keep the run formatting (headings, captions)
  {"para": "...", "after": "unique anchor", "new": " Inserted sentence."}
  {"para": "...", "new_paragraph": "Text of a new paragraph", "like": "start of a paragraph to copy the style of"}
  {"para": "...", "delete_paragraph": true}

Rules learned the hard way
  * Pass whole sentences as old/new: the diff is token-level, so only the changed words are marked.
  * The text an edit can anchor on EXCLUDES earlier tracked insertions and deletions. Anchor later edits on
    untouched original words; an earlier rewrite can silently remove the anchor (the paragraph count assert
    then reports 0 matches; re-anchor, do not loosen the assert).
  * Order: content edits, then global passes (readability splits), then citation renumbering LAST, because a
    renumbering pass rewrites citation numbers in untouched text while inserted text already uses new numbers.
  * Library use: `import track_changes as T`, then T.replace(p, old, new), T.insert_after(p, anchor, new),
    T.new_paragraph_after(p, new), T.delete_paragraph(p), T.accept_all(root).
"""
import argparse, copy, datetime, difflib, io, json, os, re, sys, zipfile
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
q = lambda t: "{%s}%s" % (W, t)
AUTHOR = os.environ.get("TRACK_AUTHOR", "Author")
DATE = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
_id = [9000]


def _nid():
    _id[0] += 1
    return str(_id[0])


def _mark(tag):
    el = etree.Element(q(tag))
    el.set(q("id"), _nid()); el.set(q("author"), AUTHOR); el.set(q("date"), DATE)
    return el


def parse_markup(s):
    """'a <i>T</i><sub>s</sub>' -> [(char, frozenset(fmt)), ...]"""
    out, state = [], set()
    for tok in re.split(r"(</?(?:i|b|sub|sup)>)", s):
        m = re.fullmatch(r"<(/?)(i|b|sub|sup)>", tok)
        if m:
            (state.discard if m.group(1) else state.add)(m.group(2))
            continue
        out += [(c, frozenset(state)) for c in tok]
    return out


def normalize(root):
    """Drop Word's layout-cache page-break marks and split runs that mix text with tabs into one run per child,
    so every text-bearing run holds a single w:t (formatting is unchanged)."""
    for e in list(root.iter(q("lastRenderedPageBreak"))):
        e.getparent().remove(e)
    for r in list(root.iter(q("r"))):
        kids = [c for c in r if c.tag != q("rPr")]
        if len(kids) > 1 and any(c.tag == q("t") for c in kids):
            rpr = r.find(q("rPr"))
            for c in reversed(kids):
                nr = etree.Element(q("r"))
                if rpr is not None:
                    nr.append(copy.deepcopy(rpr))
                nr.append(c)
                r.addnext(nr)
            r.getparent().remove(r)
    return root


def text_runs(p):
    """Text-bearing runs that are direct children of the paragraph (tracked runs are not direct children)."""
    rs = []
    for r in p.findall(q("r")):
        ts = r.findall(q("t"))
        other = [c for c in r if c.tag not in (q("rPr"), q("t"))]
        if ts and not other and len(ts) == 1:
            rs.append(r)
        elif ts:
            raise ValueError("run with mixed content; call normalize() first")
    return rs


def ptext(p):
    return "".join(r.find(q("t")).text or "" for r in text_runs(p))


def base_rpr(p):
    """Body formatting of the paragraph: rPr of its longest plain (non-italic, non-bold, non-script) run."""
    best, n = None, -1
    for r in text_runs(p):
        rp = r.find(q("rPr"))
        if rp is not None and any(rp.find(q(t)) is not None for t in ("i", "b", "vertAlign")):
            continue
        L = len(r.find(q("t")).text or "")
        if L > n:
            best, n = rp, L
    if best is None:                       # no plain run (heading, caption): longest run
        rs = sorted(text_runs(p), key=lambda r: -len(r.find(q("t")).text or ""))
        best = rs[0].find(q("rPr")) if rs else None
    return copy.deepcopy(best) if best is not None else etree.Element(q("rPr"))


def _set_t(t, s):
    t.text = s
    if s != s.strip() or "  " in s:
        t.set("{%s}space" % XML, "preserve")
    else:
        t.attrib.pop("{%s}space" % XML, None)


def _split(p, pos):
    """Ensure a run boundary at character offset pos of the paragraph text."""
    k = 0
    for r in text_runs(p):
        t = r.find(q("t")); s = t.text or ""
        if k < pos < k + len(s):
            r2 = copy.deepcopy(r)
            _set_t(t, s[:pos - k]); _set_t(r2.find(q("t")), s[pos - k:])
            r.addnext(r2)
            return
        k += len(s)


def _runs_in(p, a, b):
    out, k = [], 0
    for r in text_runs(p):
        L = len(r.find(q("t")).text or "")
        if a <= k and k + L <= b and L:
            out.append(r)
        k += L
    return out


def _ins_runs(chars, rpr, keep=False):
    """Group (char, fmt) into runs inside one w:ins. keep: use rpr as it is (e.g. a heading run)."""
    ins = _mark("ins")
    groups = []
    for c, f in chars:
        if groups and groups[-1][1] == f:
            groups[-1][0].append(c)
        else:
            groups.append(([c], f))
    for cs, f in groups:
        r = etree.SubElement(ins, q("r"))
        rp = copy.deepcopy(rpr)
        if not keep:
            for tag in ("b", "i", "vertAlign"):
                for e in rp.findall(q(tag)):
                    rp.remove(e)
            if "i" in f:
                rp.insert(0, etree.Element(q("i")))
            if "b" in f:
                rp.insert(0, etree.Element(q("b")))
            if "sub" in f or "sup" in f:
                va = etree.SubElement(rp, q("vertAlign")); va.set(q("val"), "subscript" if "sub" in f else "superscript")
        r.append(rp)
        t = etree.SubElement(r, q("t")); _set_t(t, "".join(cs))
    return ins


def _delete(runs):
    d = _mark("del")
    runs[0].addprevious(d)
    for r in runs:
        r.find(q("t")).tag = q("delText")
        d.append(r)
    return d


def _tokens(s):
    return re.findall(r"\s+|\w+|[^\w\s]", s)


def replace(p, old, new, keep=False):
    """Tracked replacement of `old` (plain text, unique in the paragraph) by `new` (markup allowed).
    keep=True gives inserted text the formatting of the run where `old` starts (headings, captions)."""
    full = ptext(p)
    assert full.count(old) == 1, "old text not unique (%d): %r" % (full.count(old), old[:60])
    return replace_at(p, full.index(old), old, new, keep)


def replace_at(p, start, old, new, keep=False):
    """As replace(), for the occurrence of `old` that starts at character `start` of the paragraph text."""
    assert ptext(p)[start:start + len(old)] == old, (start, old)
    rpr = base_rpr(p)
    if keep:
        k = 0
        for r in text_runs(p):
            L = len(r.find(q("t")).text or "")
            if k <= start < k + L:
                rpr = copy.deepcopy(r.find(q("rPr"))) if r.find(q("rPr")) is not None else etree.Element(q("rPr"))
                break
            k += L
    nchars = parse_markup(new)
    a, b = _tokens(old), _tokens("".join(c for c, _ in nchars))
    oa, na = [0], [0]
    for t in a:
        oa.append(oa[-1] + len(t))
    for t in b:
        na.append(na[-1] + len(t))
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    for tag, i1, i2, j1, j2 in ops:
        _split(p, start + oa[i1]); _split(p, start + oa[i2])
    for tag, i1, i2, j1, j2 in reversed(ops):           # from the end so earlier offsets stay valid
        if tag == "equal":
            continue
        s0, s1 = start + oa[i1], start + oa[i2]
        ins = _ins_runs(nchars[na[j1]:na[j2]], rpr, keep) if tag in ("insert", "replace") else None
        if tag in ("delete", "replace"):
            d = _delete(_runs_in(p, s0, s1))
            if ins is not None:
                d.addnext(ins)
        else:                                             # pure insertion at s0
            before = _runs_in(p, 0, s0)
            if before:
                last = before[-1]
                (last.getparent() if last.getparent().tag == q("del") else last).addnext(ins)
            else:
                text_runs(p)[0].addprevious(ins)
    return p


def insert_after(p, anchor, new):
    full = ptext(p)
    assert full.count(anchor) == 1, "anchor not unique: %r" % anchor[:60]
    pos = full.index(anchor) + len(anchor)
    _split(p, pos)
    _runs_in(p, 0, pos)[-1].addnext(_ins_runs(parse_markup(new), base_rpr(p)))


def new_paragraph_after(p, new, like=None):
    """Insert a tracked new paragraph after p, formatted like `like` (default p)."""
    like = p if like is None else like
    np_ = etree.Element(q("p"))
    ppr = copy.deepcopy(like.find(q("pPr"))) if like.find(q("pPr")) is not None else etree.Element(q("pPr"))
    rpr_mark = ppr.find(q("rPr"))
    if rpr_mark is None:
        rpr_mark = etree.SubElement(ppr, q("rPr"))
    rpr_mark.append(_mark("ins"))
    np_.append(ppr)
    np_.append(_ins_runs(parse_markup(new), base_rpr(like)))
    p.addnext(np_)
    return np_


def delete_paragraph(p):
    """Tracked deletion of a whole paragraph: its runs and its paragraph mark."""
    _delete(text_runs(p))
    ppr = p.find(q("pPr"))
    if ppr is None:
        ppr = etree.Element(q("pPr")); p.insert(0, ppr)
    rpr = ppr.find(q("rPr"))
    if rpr is None:
        rpr = etree.SubElement(ppr, q("rPr"))
    rpr.append(_mark("del"))


def accept_all(root):
    """Clean copy: accept every insertion and deletion."""
    gone = [d.getparent().getparent().getparent() for d in root.iter(q("del"))
            if d.getparent().tag == q("rPr") and d.getparent().getparent().tag == q("pPr")]
    for d in list(root.iter(q("del"))):
        d.getparent().remove(d)
    for i in list(root.iter(q("ins"))):
        par = i.getparent()
        if par.tag == q("rPr"):
            par.remove(i)
            continue
        idx = par.index(i)
        for c in list(i):
            par.insert(idx, c); idx += 1
        par.remove(i)
    for p in gone:                                        # paragraphs deleted as a whole
        if not "".join(t.text or "" for t in p.iter(q("t"))) and p.getparent() is not None:
            p.getparent().remove(p)
    return root


def find_paragraph(body, start):
    """The one paragraph whose (untracked) text starts with `start`, else the one that contains it."""
    ps = list(body.iter(q("p")))
    hit = [p for p in ps if ptext(p).startswith(start)] or [p for p in ps if start in ptext(p)]
    assert len(hit) == 1, "%d paragraphs for %r" % (len(hit), start[:60])
    return hit[0]


def _write(src, out, root, track):
    """Copy every part of src into out, replacing word/document.xml; switch track-changes on or off."""
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            elif item.filename == "word/settings.xml":
                s = data.decode("utf-8")
                if track and "<w:trackRevisions/>" not in s:
                    s = s.replace("<w:zoom ", "<w:trackRevisions/><w:zoom ", 1)
                if not track:
                    s = s.replace("<w:trackRevisions/>", "")
                data = s.encode("utf-8")
            zout.writestr(item, data)


def main():
    global AUTHOR, DATE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docx"); ap.add_argument("edits"); ap.add_argument("out")
    ap.add_argument("--clean", help="also write a copy with every change accepted")
    ap.add_argument("--author", help="revision author (default: $TRACK_AUTHOR or 'Author')")
    ap.add_argument("--date", help="revision timestamp, ISO 8601 (default: now, UTC)")
    a = ap.parse_args()
    AUTHOR = a.author or AUTHOR
    DATE = a.date or DATE
    for f in (a.out, a.clean):
        assert f is None or os.path.abspath(f) != os.path.abspath(a.docx), "never overwrite the input"
    root = normalize(etree.fromstring(zipfile.ZipFile(a.docx).read("word/document.xml")))
    body = root.find(q("body"))
    edits = json.load(io.open(a.edits, encoding="utf-8"))
    for n, e in enumerate(edits, 1):
        p = find_paragraph(body, e["para"])
        if "old" in e:
            replace(p, e["old"], e["new"], keep=e.get("keep", False))
        elif "after" in e:
            insert_after(p, e["after"], e["new"])
        elif "new_paragraph" in e:
            new_paragraph_after(p, e["new_paragraph"], find_paragraph(body, e["like"]) if e.get("like") else None)
        elif e.get("delete_paragraph"):
            delete_paragraph(p)
        else:
            sys.exit("edit %d: no action" % n)
    _write(a.docx, a.out, root, track=True)
    print("%s: %d edits by %s" % (a.out, len(edits), AUTHOR))
    if a.clean:
        _write(a.docx, a.clean, accept_all(copy.deepcopy(root)), track=False)
        print("%s: all changes accepted" % a.clean)


if __name__ == "__main__":
    main()
