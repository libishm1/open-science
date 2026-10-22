# Submission compliance and the compile step

---

## Static validation is not a compile

The single most important lesson of the packaging phase.

A structural checker passed cleanly on a document that had:
- **several overfull boxes** (text past the margin, the worst by several millimetres)
- **two entire tables missing** relative to the other rendition, one of them a reviewer's explicit request
- **colliding table numbers** in the other rendition

Structure checks prove a file is *well-formed*, not that it is *right*. Compile it and **read the PDF**.

### Compile sequence

```bash
pdflatex -interaction=nonstopmode --enable-installer manuscript.tex
bibtex   manuscript
pdflatex -interaction=nonstopmode --enable-installer manuscript.tex   # x2
```

`--enable-installer` lets MiKTeX fetch missing packages without prompting in a non-interactive shell.
Check the toolchain is really absent before assuming it: MiKTeX was installed all along, just **not on
PATH** (`%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\`).

### Read the log for what static checks cannot see

```bash
grep -c "Overfull"  manuscript.log     # must be 0 - text past the margin
grep -c "undefined" manuscript.log     # must be 0 - broken \ref / \cite
grep -c "Underfull" manuscript.log     # loose spacing; tolerable in p{} columns
```

Beware grep escaping: `"Overfull \\\\hbox"` through a shell can silently match nothing and report a
reassuring zero. Count the bare word.

### Read the PDF itself

```python
import fitz
d = fitz.open("manuscript.pdf")
for i, p in enumerate(d, 1):
    words, imgs = len(p.get_text().split()), len(p.get_images())
    if words < 60 and imgs: print(i, "figure-only page")
# does anything cross the margin?
mx = max(b[2] for b in page.get_text("blocks"))
print("right margin:", page.rect.width - mx)
```

---

## Fixing overfull boxes in tables

Cause is almost always an **unbreakable token wider than its column**:

| Token | Fix |
|---|---|
| `Cold/temperate` | the slash blocks a linebreak; write `Cold / temperate` |
| `Mediterranean` | widen the column, or abbreviate |
| A bold two-word header in a 1.0 cm column | widen; each *word* must fit |

If the table sits in `\resizebox{\linewidth}{!}{…}`, extra natural width is scaled back rather than
overflowing, so widening columns is **free**; verify by measuring the rightmost content in the PDF.

Add `\emergencystretch=2em` in the preamble so TeX relaxes interword spacing instead of running past
the margin; it clears most prose overfulls at no visible cost.

---

## Word and element budgets: measure, never assume

Re-measure after **every** content change. One revision's added sentence pushed an abstract past its
**250-word limit**, and it sat there for several revisions because nobody re-checked.

### Costing figures and tables

When asked what display items "cost" against a word budget, give both numbers:

**Measured**, using the document's own typography:

```python
# words per full text page, and the column height they occupy
wpp, colh = words_per_text_page, column_height_pt   # measured from text-only pages
per_pt = wpp / colh           # words per point of column height
cost = item_height_pt * per_pt
```

**Conventional**: most publishers count a display item at a flat ~250 words
(half-page ≈ 500, quarter-page ≈ 250).

For one set of display items, the measured cost came to about half the flat-rate figure. State which
convention the target journal uses; if unknown, budget the larger and report the smaller.

Useful framing for a supervisor: pair a requested *addition* with requested *cuts*. Trimming an
overlong Limitations and Conclusions offset roughly half the cost of reinstating the display items,
turning two competing requests into one affordable plan.

---

## Front-matter checklist

```
[ ] title (contribution, not setup)
[ ] all authors, affiliations, superscript markers consistent
[ ] corresponding author marked, email correct (honour the author's own spelling/case)
[ ] abstract within limit - RE-MEASURE after every edit
[ ] keywords: searchable terms, no title repeats
[ ] highlights: count AND per-item character limit
[ ] CRediT author contributions
[ ] declaration of competing interest
[ ] funding / grant number, verbatim from the funder
[ ] data availability statement
[ ] graphical abstract - usually a SEPARATE upload, not referenced by the manuscript
```

Highlights are a rendition too: check their spelling and phrasing match the body (a cedilla and a
phrasing choice diverged there while the body was correct).

---

## Table and figure numbering

- If one rendition auto-numbers (`\ref`) and another hard-codes, the bug is in **the hard-coded one**
  and only appears on comparison. In one rendition "Table 3" named three different tables.
- Number in **document order**. A table introduced in the literature review is Table 1 even if the
  methodology tables feel more fundamental.
- After any insertion, re-derive the whole sequence rather than patching one reference. Use placeholder
  tokens (`@1@`, `@2@`) during renumbering so replacements are never re-matched by later rules.
- Check for numbers referenced but never captioned, and captions never referenced. Exclude external
  code references (`SBC 601 Table 11.2`) from the regex.

---

## Packaging

- A **reviewer/reproducibility package** contains code, data, figures and a verification harness,
  never document-generation scripts. Assert that explicitly when building it.
- Ship a harness that prints `N/N`, and have anything that *cites* that number read it by running it.
- **Never** `mv` over a shared/synced file; it breaks the share link. Write in place.
- Snapshot every revision to `_versions/` with a date and descriptive slug.
- Keep raw simulation outputs out of the manuscript repo but inside the package, with checksums.
