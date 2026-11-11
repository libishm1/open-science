# Publisher proofs: answering the production queries after acceptance

After acceptance the typeset paper comes back in an online proofreading portal with author queries (Project C:
41 queries in an MDPI portal). Content changes are no longer accepted; the queries are about typography,
figures, tables, references and files. The supervisor answers in the portal. Our deliverable is a reply guide
plus corrected files, ready the same day.

## 1. The deliverable

- **Input:** screenshots of the portal, one per query. They read reliably. Queries marked "the following
  highlights are the same" repeat elsewhere and take the same reply.
- **Reply guide (DOCX and PDF):** one table in proof order with the location, the query in short, the reply to
  paste (first person, to the production editor) and the edit to make on the portal, highlighted where an edit
  is needed. Paste-ready blocks for anything longer than a line: caption sentences, footers, reference entries.
- **Files:** corrected figures numbered as in the paper; supplementary files in the format the portal accepts
  (a file list that takes "Word/.Zip only" needs a PDF supplement zipped).
- **A short section of corrections beyond the queries**, for the author to approve (section 4).
- One zip and a short message; ask for the ORCID if the portal requests it.

## 2. Query catalogue

| Query | What is usually behind it | Answer |
|---|---|---|
| Hyphen between numbers to en dash, in a figure | Ranges in plot text, and compounds such as "3-min" or "WWR-40%" | Fix the plotting script and re-render |
| Hyphen to minus sign (U+2212), in a figure | Python formatting ("%+.2f", "%.1f to %.1f", "%g") prints a hyphen-minus for negatives; matplotlib tick labels are already correct | Wrap formatted numbers: `s.replace("-", "−")` |
| Commas only from five digits | "1,524" in a figure or table | Remove; MDPI fixes running text itself |
| Font too small | `bbox_inches="tight"` with one long single-line footer widened the canvas to 27 in, so the figure prints at a quarter size | Wrap or shorten the footer, re-lay out the panels, move the key into a legend and the caption (`figure_checks.py scale`) |
| Explain arrows, symbols, colours, shading or line styles in the caption | Keys that live only in the figure | Add one caption sentence naming each line style and shading |
| Overlapping content in a figure | Usually clustered markers; sometimes a label on a curve | Markers: explain that they are cases with similar values and the text reports the numbers. Labels: give them a background box or move them |
| Bold in a table body | Highlighted values | Remove, or explain in the footer when it encodes something ("Bold values are the highest R² in each monthly analysis"); verify that claim against the table first |
| Italic notes below tables | Notes typeset as body paragraphs | Ask for them as table footers, without italics |
| Italic run-in headings | Paragraph headings inside a section | Keep them when they structure the section, and say so |
| Background or line colours in tables | House style | Not necessary; standard style |
| Paragraph starting with numbers: make a list? | Phase labels such as "1. Urban microclimate ..." | Keep; they are labels used in the text |
| Tables cited out of order | An early pointer to a later table | Repoint the early citation to the section, so no table moves |
| Variable formatting | An overbar or subscript written as Unicode in running text | Ask for the format of the displayed equation, and list the occurrences |
| Equations: bold removed, duplicates, consistency | MathType conversion | Confirm after reading every displayed equation |
| "Is there an appendix?" | "Appendix G" of ASHRAE 90.1 in the text | Explain the false positive |
| Software version | "Python model generator" | Give the version from the environment record |
| References in the supplement not in the main list | Works cited only in the supplementary file | Add them to the reference list and cite them in the Supplementary Materials statement ("References [52,53] are cited in the Supplementary Materials."); verify their DOIs |
| Files missing | Code or checks zips named in the statement but never attached | Upload them under exactly the names the statement uses |
| One reference holding several documents | "Data Sheets RT24HC (...), RT25 (...) ..., 2020–2024" | One reference per document with its own year, appended at the end of the list so nothing renumbers; citations become a range |
| Acknowledgments overlap Funding | The same programme in both | Confirm no individuals are named; explain the distinction or offer a reworded sentence |

## 3. Re-render, then prove only the text changed

1. Back up every figure and every other file the scripts write. Scripts often write several figures; one
   regenerated file in Project C fed the supplement and had to be restored.
2. Lint the plotting scripts (`figure_checks.py lint`): on Project C's scripts it found every queried hyphen,
   minus, comma and multiplication sign.
3. Re-render through `render_600dpi.py`.
4. Pixel-diff each figure against the accepted version (`figure_checks.py diff`): the changed region must be
   where the text changed. Scripts that were not edited must re-render identically; if they do not, the
   environment changed and every figure needs a full visual check.
5. Read every changed figure at reproduction size.

## 4. Re-read every figure against the revised paper

A revision changes text and tables; figures drawn before it keep stale content, and the proof is the last chance
to fix it. Project C's proof found five: a run count not updated after its table changed (60 against 78), a note
pointing at a table that had been renumbered, a figure title contradicting its own panels and table, a note
saying a bound was untested after the revision had tested it, and a title without the qualification its caption
had gained in review. Fix them in the same re-upload and list them separately for the author's approval.

## 5. The supplement gets the same scrutiny

- Verify the supplement's own references against Crossref and a second source: one DOI in Project C resolved to
  an unrelated paper.
- Rebuild and diff the old and new text: only the intended change may appear.
- If a vendor page cited in the paper is gone, cite the archived copy (see [revision-and-response.md](revision-and-response.md), section 6).
