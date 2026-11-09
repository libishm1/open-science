# Full-text extraction protocol (PDF to Markdown with local models)

Version 2026-11-09. Use this before extraction (phase 5) when the full texts are PDFs and the review needs equations,
figures and numbers, not only prose.

## 1. Division of labour

- Python finds, crops, numbers, logs and checks. Models only read what Python hands them.
- Every model output is marked unverified until a check or a person confirms it.
- Keep the PDFs, the extracted text and the crops out of version control. They are copyrighted.

## 2. Routing

| Material | Reader | Output |
|---|---|---|
| Born-digital page text | PDF text layer (PyMuPDF or similar) | Markdown, page by page |
| Equation crops | Vision OCR model, equation prompt | LaTeX draft per numbered equation |
| Figures | Vision OCR model, caption in the prompt | Two- or three-sentence description |
| Scanned or garbled pages, pages where a numbered equation is missing | Vision OCR model, whole page | Sidecar Markdown per paper (`<key>.pages.md`) |
| Long documents with a good text layer | Text layer only | Do not OCR whole pages: it costs days and adds little |

Put the caption in the figure prompt. Without it, small models misname the object in the figure.

## 3. Choosing or replacing an engine: subset first

Never switch engines on a hunch. Run a trial on a small, representative subset, then decide.

1. **Pick the subset.** Include born-digital pages that hold hand-verified equations (ground truth for prose and
   equations), scans, non-English pages, and at least one paper with a broken font layer.
2. **Score against ground truth.**
   - Prose: word-multiset F1 against the text layer, after removing LaTeX and markup.
   - Equations: normalised string similarity against hand-verified LaTeX, with the current reader as baseline.
   - Rescue: how many equations the current pipeline lost does the candidate find, by equation number.
   - Failure modes: outputs that hit the token limit, repeated lines (loops), and seconds per page.
3. **Compare chunk sizes.** Whole page, half page (cut at a blank band so no line is split) and page pairs. In our
   trial the whole page won on accuracy and speed.
4. **Decide, record, and only then run the full set.** Save the trial script, the per-page CSV and the report.

Example from our own trial (62 pages, a 4B OCR model through llama.cpp, Q4 weights, 8 GB GPU):
whole-page prose F1 0.951 against 0.949 for a larger page OCR model; 4 of 4 lost equations found; equation
similarity 0.938 against 0.937 for crop reads; about 30 s per page cool, against 2 to 4 minutes.

## 4. Context and memory on a small GPU

- Measure, do not estimate. Start the server at the candidate context, read VRAM after load and after one page.
- One page at 200 dpi costs about 3,300 image tokens for a 448-px-tile vision encoder. A dense page with display
  LaTeX can need 2,000 or more output tokens. Size the context for input plus output with margin.
- An f16 KV cache is faster than an 8-bit cache. Use the 8-bit cache only when the context does not fit otherwise.
- Laptops throttle. Log GPU temperature, pause above a set limit, and give a long run a cool-down first. In our trial
  a hot GPU fell from about 55 to about 9 tokens per second.

## 5. Text-layer faults to check per paper

- Fonts that map Greek to Latin letters (for example delta as d, theta as u). Read symbols from the equation LaTeX
  or the crop.
- Decimal points printed as colons, full-width digits, decimal commas, markup inside numbers (`0 _._ 0825`).
- Tables that come out empty or flattened, missing first pages, one character per line.
- Wrong or mixed PDFs: the file is another paper, an older version, or a whole journal issue. Check the title words
  of the first pages against the record before extraction (see the QA protocol).

## 6. Critical equations

Equations that a build or a conclusion depends on are transcribed by hand from the crop, checked for units, and,
where the claim is algebra or calculus, proved in a proof assistant (we use Lean 4 with Mathlib). Keep a record per
equation: crop, LaTeX, how the model draft compared, source problems, proof file.
