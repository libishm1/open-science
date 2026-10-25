# The markdown → LaTeX/DOCX build chain

Project B kept one markdown file as the source of truth and generated PDF, DOCX, supplement and a
LaTeX source zip from it. That is the right architecture (it makes rendition drift structurally
impossible), but a hand-written converter has its own failure modes, and all of them are silent.

---

## Architecture

```
Manuscript.md                   <- the ONLY editable file (+ Supplementary_Material.md)
Supplementary_Material.md
      |
      +-- check_order.py        guards: float order, first-mention order, banned characters
      +-- number_citations.py   author-year -> [N], emits the numbered bibliography
      +-- audit_restructure.py  countable word count, per section, against the journal rule
      |
      +-- md2tex.py   -> latex/main.tex   -> pdflatex x2 -> Manuscript.pdf
      +-- md2docx.py  -> Manuscript.docx
      +-- supp2tex.py -> latex_supp/supp.tex -> Supplementary_Material.pdf
      +-- build_docx.py  line-numbered, double-spaced review copy
```

**Rule:** any hand-edit to a generated file is lost on the next build and is indistinguishable from a
bug. State this in the handoff and enforce it by never opening those files in an editor.

---

## Converter traps, all of which shipped a broken document

### Floats are numbered by source order
LaTeX numbers `figure`/`table` environments in the order they appear in the source, not by label. A
table defined out of order renders under the wrong number while every `\ref` remains correct. Guard:

```python
tab = [int(m.group(1)) for m in re.finditer(r"\*\*Table (\d+)\.", body)]
if tab != list(range(1, len(tab) + 1)):
    bad.append(f"TABLES defined out of order: {tab}")
# figures by FIRST MENTION
order, seen = [], set()
for m in re.finditer(r"Fig(?:ure)?\.?\s*(\d+)", body):
    if m.group(1) not in seen:
        seen.add(m.group(1)); order.append(int(m.group(1)))
```

### Hardcoded ranges
`for n in range(1, 13)` silently dropped every figure after the twelfth from every PDF. Derive bounds
from the data (`range(1, max(FIGS) + 1)`) and warn about anything unplaced.

### A hand-maintained figure map
The `FIGS` dict must be regenerated from the caption list after **any** renumbering. Stale, it put
the wrong artwork under most of the captions in both PDF and DOCX. See
[silent-loss-and-verification.md](silent-loss-and-verification.md).

### Width-blind table layout
Gating `\resizebox` on column count let a 4-column table walk off the page and lose two thirds of its
cells. Gate on content width; use `tabularx` with ragged-right wrappable columns; add a conditional
resizebox. Requires `\usepackage{tabularx,array}`; omitting it fails loudly, which is a mercy.

### Soft-wrapped markdown
`**bold**` spanning a line break never matches. An unwrapper that joins paragraph lines is required,
but it must **skip `[N]` reference lines**, or the whole bibliography collapses into one entry.

```python
def _unwrap(lines):
    out, buf = [], []
    for ln in lines:
        if re.match(r"^\[\d+\]", ln.strip()):     # never join reference lines
            if buf: out.append(" ".join(buf)); buf = []
            out.append(ln); continue
        ...
```

### List handling
Must consume multi-line items **and** blank lines between items, otherwise you get one `enumerate`
per line, body text ejected from the list, and literal `**` in the PDF.

```python
def _next_is_num(k):
    while k < len(lines) and not lines[k].strip():
        k += 1
    return k < len(lines) and re.match(r"^\d+\. ", lines[k].strip())
```

### Author capture
A converter written during blinded review only recognised the blinding placeholder and emitted
`\author{\emph{None}}` once a real byline appeared. Handle both.

### Unicode
A bare `Δ` broke the build. Normalise: `°C`, `×`, `±`, `≈`, `≥`, `≤`, `→`, `−`, `·` all need mappings;
prefer writing "Change in" over a symbol in a table header.

### Underscores inside and outside maths
Escape `_` only outside `$…$` spans:

```python
parts = s.split("$")
for k in range(0, len(parts), 2):
    parts[k] = re.sub(r"(?<!\\)_", r"\\_", parts[k])
s = "$".join(parts)
```

---

## Compile recipe

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex   # twice, for refs
grep -c "Overfull \\\\hbox" main.log      # must be 0
grep -c "undefined" main.log              # must be 0
grep "Output written" main.log            # page count sanity
```

`cmd | tail` **masks the exit code**: LaTeX "succeeded" while producing no PDF. Redirect and check
`$?` separately.

For the reference list, long DOIs overflow the margin. In the preamble:

```latex
\usepackage[hyphens]{url}
\sloppy
\def\UrlBreaks{\do\/\do-\do.\do:\do_\do?\do\&\do\=}
```

---

## Supplementary documents need the same rigour

The supplement had its own converter and its own bugs: tables bleeding outside the text block (fixed
with the same `tabularx` + `resizebox` treatment), a long reference list of which **only a couple of
entries were cited**, and section numbering that gained a gap when content moved to the main text.

Treat the supplement as **a document, not an appendix dump**: contiguous numbering, every float
referenced from somewhere, a reference list containing what it cites and nothing else.

---

## Guard suite to ship with the chain

| Guard | Catches |
|---|---|
| float definition + first-mention order | wrong-numbered floats |
| banned characters (em dash, etc.) | style regressions from later edits |
| citation resolution **plus a bare-citation check** | citations that vanish without warning |
| countable word count, per section | limit breaches, and where to cut |
| caption ↔ artwork hash pairing | wrong figure under a caption |
| cross-reference target **content** check | pointers that resolve to the wrong thing |
| `Overfull \hbox` count == 0 | content lost off the page |
| effective DPI per figure | publisher rejection |

Run them after every build, not once at the end. Every one of these exists because it failed first.
