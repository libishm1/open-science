# Scripts

Standalone command-line helpers for an agent-assisted systematic literature review and manuscript
production. Every script takes its paths as arguments (`python <script> -h` prints the docstring with an
example), writes plain JSON / JSONL / CSV / Markdown, and has no project-specific values built in.
Install the packages with `python -m pip install -r requirements.txt`.

Run Python with `-P` (or `-I`) so a file planted in the working folder cannot shadow a module. Downloaded
PDFs and zips are untrusted data: keep them in their own folders, separate from these scripts.

## Environment variables (all optional)

| Variable | Used by | Effect |
|---|---|---|
| `CROSSREF_MAILTO` | verify_run_A, enrich_abstracts, verify_refs, crossref_check | Adds `mailto:` to the User-Agent (Crossref polite pool). Unset: no contact is sent. |
| `OPENALEX_API_KEY` | harvest_openalex, verify_run_B | Sent as `api_key` to OpenAlex. |
| `OPENALEX_MAILTO` | harvest_openalex, verify_run_B | Sent as `mailto` to OpenAlex (polite pool). Unset: no contact is sent. |
| `S2_API_KEY` | verify_run_B, enrich_abstracts, fetch_fulltext_alt | Sent as `x-api-key` to Semantic Scholar; without it the shared, heavily rate-limited pool is used. |

## Scripts

| Script | What it does | Inputs → outputs | Packages | Env |
|---|---|---|---|---|
| `harvest_openalex.py` | Boolean title/abstract search on OpenAlex, one logged query at a time (PRISMA identification). | queries file (`templates/harvest_queries.example.json`, JSON or YAML) → `openalex_raw.json`, `search_log.json` | requests (PyYAML) | OPENALEX_* |
| `enrich_abstracts.py` | Fills missing/short abstracts from Semantic Scholar, then Crossref; keeps S2 TLDRs. | pool JSON → same file, enriched in place | requests | S2_API_KEY, CROSSREF_MAILTO |
| `make_batches.py` | Selects the screening set (years, optional score threshold, prior-corpus tags) and writes score-interleaved batches. | pool JSON → `batch_NN.jsonl`, `screen_ids.json` | stdlib | – |
| `build_claimed.py` | Splits a corpus into the blind DOI list and the claimed metadata. | corpus JSON → `dois_all.txt`, `claimed.json` | stdlib | – |
| `verify_run_A.py` | Blind run A: doi.org handle registry + Crossref record for each DOI. | `dois_all.txt` → `runA.json` | requests | CROSSREF_MAILTO |
| `verify_run_B.py` | Blind run B: OpenAlex + Semantic Scholar (batched) + DataCite fallback. | `dois_all.txt` → `runB.json` | requests | OPENALEX_*, S2_API_KEY |
| `verify_reconcile.py` | Compares A, B and the claimed record (title, first author, year); verdict per DOI, retraction flags, Cohen's kappa / PABAK / Gwet's AC1 between independent sources. Offline. | `claimed.json`, `runA.json`, `runB.json` → `reconciled.json` | stdlib | – |
| `verify_refs.py` | Verifies a manuscript's reference list at doi.org (CSL JSON) or by Crossref title search, and writes biblatex entries from the registry metadata (sentence-case titles, protected capitals). Exit 1 if any reference fails. | `references_in.json` (+ optional protect-word list) → `references.bib`, `verification_report.csv` | stdlib | CROSSREF_MAILTO |
| `crossref_check.py` | Quick Crossref lookup of DOIs given on the command line. | DOIs → JSON lines on stdout | requests | CROSSREF_MAILTO |
| `fetch_fulltext_alt.py` | Open-access PDF retrieval (S2 openAccessPdf, MDPI CDN, Wiley, per-record `extra_urls`); keeps only HTTP 200 + `%PDF` + minimum size. | selection JSON `[{key, doi}]`, status JSON → `<pdf_dir>/<key>.pdf`, status updated | requests | S2_API_KEY |
| `unzip_identify.py` | Safe extraction of a zip of PDFs into an empty folder (only `.pdf`, no traversal, size cap), then identifies each PDF by the DOI on pages 1–2. | zip, corpus JSON (+ selection, DOI request lists) → PDFs, printed table, optional `map.json` | pymupdf | – |
| `convert_incoming.py` | Stage 1 conversion for Stage 2: per-paper Markdown with extracted images, page renders, equation-page candidates, image inventory. | PDFs + `map.json` → `fulltext_pdf/`, `fulltext_md/<key>/`, `eqpipe/` | pymupdf, pymupdf4llm | – |
| `pdf_to_md.py` | Plain PDF → Markdown conversion with a text-length check (flags scanned PDFs). | PDF folder → Markdown folder, `report.json` | pymupdf, pymupdf4llm | – |
| `render_page.py` | Renders one page, or the part of it between two heights, at any dpi for close reading. | PDF, page, dpi → PNG | pymupdf | – |
| `check_latex.py` | Compiles each transcribed equation with pdflatex (`-no-shell-escape`); exit 1 on any error. | `equations/<key>.json` → report on stdout | stdlib + pdflatex | – |
| `make_review_batch.py` | Collects the `MISMATCH` numeric checks of given papers into one adversarial-review batch. | `equations/<key>.json` → `batch<N>.json` | stdlib | – |
| `check_equations.py` | SI dimensional-homogeneity check of every extracted equation (sympy units): PASS / EMPIRICAL / FAIL / SKIP. | `papers.jsonl` (`templates/SCHEMA.md`) → `equations_checked.csv` | sympy | – |
| `docx_helpers.py` | Import-only helpers for the synthesis report in Word: A4/Arial styles, page numbers, hyperlinks, zebra tables with repeating headers, captions, figures, landscape sections. | – (library) | python-docx | – |
| `number_citations.py` | Converts author-year citations in a Markdown manuscript to numbered `[n]` in order of first appearance and rebuilds the reference list. | manuscript `.md`, reference pool JSON → `<name>_numbered.md` | stdlib | – |
| `render_600dpi.py` | Runs a matplotlib figure script with every `savefig` forced to 600 dpi (or `--dpi`); layout unchanged. | figure script → its figures | matplotlib | – |
| `check_layout.py` | Flags text/images in the page margins and captions orphaned at the page foot; lists the page of every table and figure. | PDFs → report on stdout | pymupdf | – |
| `snapshot.py` | Versioned snapshots of the working manuscript with a history log, and a `backup()` that build scripts call before overwriting a deliverable. | manuscript → `versions/`, `versions/history.jsonl` | stdlib | – |

## Literature-review pipeline: run order

Folder names below are suggestions; every path is an argument.

1. **Harvest.** Copy `templates/harvest_queries.example.json`, write your own blocks and queries, then
   `python -P harvest_openalex.py queries.json harvest`.
   Optional (no script shipped): merge prior reference lists into the pool, tagging their records in a `src`
   list (e.g. `prior_<name>`), and add a keyword pre-score as a `score` field.
2. **Enrich.** `python -P enrich_abstracts.py harvest/openalex_raw.json --years 2021 2026`
   (with a score: `--min-score 12 --prior-tag prior_`).
3. **Batches.** `python -P make_batches.py harvest/openalex_raw.json --out-dir screen --years 2021 2026 --batch-size 100`
   (with a score: `--min-score 20 --prior-tag prior_`).
4. **Agent screening.** Fill in `templates/SCREENING_PROTOCOL.md`. One agent per `screen/batch_NN.jsonl`
   writes a JSON array of coded records (relevance 0–3, themes, gap codes, ...). Check the record count and id order of every output.
5. **Selection.** Merge the coded batches and choose the corpus (e.g. relevance ≥ 2) and the full-text set
   (e.g. the top N by relevance and gap coverage). Write `screen/corpus.json` (records with `doi`, `title`,
   `year`, `first_author`, `venue`) and `fulltext/selection.json` (`[{key, doi}]`).
6. **DOI verification (double-blind).**
   `python -P build_claimed.py screen/corpus.json --out-dir verify`, then, independently of each other,
   `python -P verify_run_A.py verify/dois_all.txt verify/runA.json` and
   `python -P verify_run_B.py verify/dois_all.txt verify/runB.json`, then
   `python -P verify_reconcile.py verify/claimed.json verify/runA.json verify/runB.json verify/reconciled.json`.
   Resolve every `CONFLICT`, `NOT_FOUND` and `UNRESOLVED` verdict by hand; drop or correct retracted records.
7. **Full-text fetch and conversion.**
   `python -P fetch_fulltext_alt.py fulltext/selection.json fulltext/pdf fulltext/fetch_status.json` for open-access copies;
   obtain the rest through your library. For a zip of PDFs:
   `python -I unzip_identify.py papers.zip incoming/batch1 --corpus screen/corpus.json --fulltext fulltext/selection.json --map-out incoming/batch1_map.json`.
   Then `python -P convert_incoming.py --src incoming/batch1 --map incoming/batch1_map.json --out-root review --work work`
   (or `pdf_to_md.py` for text-only Markdown).
8. **Stage 2.** One agent per few papers with `templates/STAGE2_PROTOCOL.md` (uses `render_page.py`, `check_latex.py`,
   `templates/PaperTemplate.lean`) and, for papers flagged `"extract": true`, `templates/EXTRACTION_PROTOCOL.md`.
   Then `python -P make_review_batch.py work/eqpipe/equations work/eqpipe/mismatch_review/batch0.json <key> ...`
   and an adversarial reviewer per batch with `templates/REVIEW_PROTOCOL.md`.
   For extraction records in the `templates/SCHEMA.md` format, check DOIs with `crossref_check.py` and equations with `check_equations.py`.
9. **Synthesis and manuscript.** Build the report with `docx_helpers.py`; verify the manuscript's own reference list
   with `verify_refs.py`; number citations with `number_citations.py`; re-render figures with `render_600dpi.py`;
   check the PDF layout with `check_layout.py`; snapshot each version with `snapshot.py`.

Only download what you are licensed to access, and respect each API's rate limits and terms.
