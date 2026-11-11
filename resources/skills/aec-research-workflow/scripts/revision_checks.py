# -*- coding: utf-8 -*-
"""Checks for a manuscript revision: content neutrality, letter integrity, readability, order, typography.

  numbers OLD NEW            multiset of the numbers in two versions; prints every number added or removed.
                             A readability or wording pass must leave it unchanged.
  readability DOC [OLD]      sentence-length statistics of the prose (median, mean, counts over 40/50/60 words),
                             with OLD for a before/after comparison and --top N for the longest sentences.
  quotes CLEAN LETTER...     every quoted fragment in a response letter's "Change ..." paragraphs (split at
                             "..." or the ellipsis character) must occur in the clean manuscript.
  order DOC                  numbered citations [n] first cited in ascending order (before "References"), and
                             Tables and Figures first cited in ascending order (captions excluded).
  typography DOC             em dashes, hyphen-minus before a number, commas in four-digit numbers,
                             a letter x between numbers.

DOC may be .docx (body paragraphs and table cells), .md or .txt. Exit status 1 when a check fails.
Example: python -P revision_checks.py quotes R1_clean.docx Response_to_Reviewer_1.docx Response_to_Reviewer_2.docx
"""
import argparse, collections, io, re, statistics, sys

DASH = "\u2014"
ABBR = ("e.g.", "i.e.", "et al.", "Fig.", "Figs.", "Eq.", "Eqs.", "Ref.", "Refs.", "approx.", "vs.", "cf.",
        "No.", "Sect.", "ca.")


def paragraphs(path):
    if path.lower().endswith(".docx"):
        import docx
        from docx.table import Table
        from docx.text.paragraph import Paragraph
        d = docx.Document(path)
        out = []
        for el in d.element.body.iterchildren():
            tag = el.tag.split("}")[1]
            if tag == "p":
                out.append(Paragraph(el, d).text)
            elif tag == "tbl":
                for row in Table(el, d).rows:
                    seen = []
                    for c in row.cells:
                        if c.text not in seen:
                            seen.append(c.text)
                    out.append(" | ".join(seen))
        return out
    return io.open(path, encoding="utf-8").read().split("\n")


def body_until_references(ps):
    for i, p in enumerate(ps):
        if p.strip().rstrip(":").lower() in ("references", "bibliography", "literature cited"):
            return ps[:i]
    return ps


def norm(s):
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).strip()


# ------------------------------------------------------------------------------------------------ numbers
NUM = re.compile(r"[\u2212-]?\d+(?:[.,]\d+)*")


def numbers(path):
    c = collections.Counter()
    for p in paragraphs(path):
        for m in NUM.findall(p):
            c[m.replace("\u2212", "-")] += 1
    return c


def cmd_numbers(a):
    old, new = numbers(a.old), numbers(a.new)
    gone, added = old - new, new - old
    print("numbers: %d in OLD, %d in NEW" % (sum(old.values()), sum(new.values())))
    for lab, c in (("removed", gone), ("added", added)):
        if c:
            print("  %s: %s" % (lab, ", ".join("%s x%d" % (k, v) for k, v in sorted(c.items()))))
    return 1 if (gone or added) and not a.allow else 0


# ------------------------------------------------------------------------------------------------ readability
def sentences(text):
    t = text
    for ab in ABBR:
        t = t.replace(ab, ab.replace(".", "\u2024"))
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[\u2212\d])", t)
    return [s.replace("\u2024", ".") for s in parts if s.strip()]


def prose(path):
    out = []
    for p in body_until_references(paragraphs(path)):
        if " | " in p or re.match(r"^(Figure|Fig\.|Table|Scheme)\s+\d+\.", p):
            continue
        if len(p.split()) < 25:                  # headings, short labels, list stubs
            continue
        out += sentences(p)
    return out


def stats(path):
    L = [len(s.split()) for s in prose(path)]
    return {"sentences": len(L), "median": statistics.median(L), "mean": round(statistics.mean(L), 1),
            ">40": sum(x > 40 for x in L), ">50": sum(x > 50 for x in L), ">60": sum(x > 60 for x in L)}


def cmd_readability(a):
    s = stats(a.doc)
    if a.old:
        o = stats(a.old)
        for k in s:
            print("  %-10s %8s -> %s" % (k, o[k], s[k]))
    else:
        for k, v in s.items():
            print("  %-10s %s" % (k, v))
    if a.top:
        for x in sorted(prose(a.doc), key=lambda x: -len(x.split()))[:a.top]:
            print("\n[%d words] %s" % (len(x.split()), x))
    return 0


# ------------------------------------------------------------------------------------------------ quotes
def cmd_quotes(a):
    clean = norm(" ".join(paragraphs(a.clean)))
    bad = 0
    for letter in a.letters:
        n = 0
        for p in paragraphs(letter):
            if not p.lstrip().startswith("Change"):
                continue
            s = norm(p)
            pairs = re.findall(r'"([^"]+)"\s*(?:\u2192|->|replaced by|becomes)\s*"([^"]+)"', s)
            if pairs:                                 # '"old" -> "new"': only the new text must be in the paper
                quoted = [new for _, new in pairs]
            else:
                m = re.search(r'"(.*)"\s*$', s)
                if not m:
                    continue                          # a description of a change, not a quotation
                quoted = [m.group(1)]
            for frag in (f for qt in quoted for f in re.split(r"\.\.\.|\u2026", qt)):
                frag = norm(frag).strip(" \"'")
                if len(frag) < 20:
                    continue
                n += 1
                if frag not in clean:
                    bad += 1
                    print("NOT FOUND in %s:\n  %s" % (letter, frag[:200]))
        print("%s: %d quoted fragments checked" % (letter, n))
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------ order
def expand(group):
    out = []
    for part in re.split(r"\s*,\s*", group):
        m = re.fullmatch(r"(\d+)\s*[\u2013-]\s*(\d+)", part)
        out += list(range(int(m.group(1)), int(m.group(2)) + 1)) if m else ([int(part)] if part.isdigit() else [])
    return out


def cmd_order(a):
    body = body_until_references(paragraphs(a.doc))
    bad = 0
    seen, top = set(), 0
    for p in body:
        for g in re.findall(r"\[(\d+(?:\s*[,\u2013-]\s*\d+)*)\]", p):
            for n in expand(g):
                if n not in seen:
                    if n != top + 1:
                        bad += 1; print("citation [%d] first cited after [%d]" % (n, top))
                    seen.add(n); top = max(top, n)
    print("citations: %d distinct, highest [%d]" % (len(seen), top))
    for kind, pat in (("Table", r"\bTables?\s+((?:\d+(?:\s*(?:,|and|\u2013|-)\s*)?)+)"),
                      ("Figure", r"\b(?:Figures?|Figs?\.)\s+((?:\d+(?:\s*(?:,|and|\u2013|-)\s*)?)+)")):
        first = []
        for p in body:
            if re.match(r"^(%s|Fig\.)\s+\d+\." % kind, p):
                continue                              # the caption itself
            for g in re.findall(pat, p):
                for n in expand(re.sub(r"\band\b", ",", g).strip(" ,")):
                    if n not in first:
                        first.append(n)
        out = [n for i, n in enumerate(first) if i and n < max(first[:i])]
        print("%ss first cited in the order %s" % (kind, first))
        for n in out:
            bad += 1; print("  %s %d is first cited after a higher-numbered %s" % (kind, n, kind.lower()))
    return 1 if bad else 0


# ------------------------------------------------------------------------------------------------ typography
def cmd_typography(a):
    bad = 0
    for i, p in enumerate(paragraphs(a.doc), 1):
        for lab, pat in (("em dash", DASH), ("hyphen-minus before a number", r"(?:^|[\s(=])-\d"),
                         ("comma in a four-digit number", r"(?<![\d,.])\d,\d{3}(?![\d,])"),
                         ("letter x between numbers", r"\d\s?x\s?\d")):
            for m in re.finditer(pat, p):
                bad += 1
                print("para %d, %s: ...%s..." % (i, lab, p[max(0, m.start() - 30):m.end() + 30]))
    print("%d typography findings" % bad)
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("numbers"); s.add_argument("old"); s.add_argument("new")
    s.add_argument("--allow", action="store_true", help="report differences but exit 0")
    s = sp.add_parser("readability"); s.add_argument("doc"); s.add_argument("old", nargs="?")
    s.add_argument("--top", type=int, default=0)
    s = sp.add_parser("quotes"); s.add_argument("clean"); s.add_argument("letters", nargs="+")
    s = sp.add_parser("order"); s.add_argument("doc")
    s = sp.add_parser("typography"); s.add_argument("doc")
    a = ap.parse_args()
    sys.exit({"numbers": cmd_numbers, "readability": cmd_readability, "quotes": cmd_quotes, "order": cmd_order,
              "typography": cmd_typography}[a.cmd](a))


if __name__ == "__main__":
    main()
