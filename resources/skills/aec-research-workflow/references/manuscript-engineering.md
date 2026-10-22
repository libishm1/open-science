# Manuscript engineering: build, defend and submit a simulation paper

Distilled from taking simulation-based building-physics papers from first draft through review to publication. Every rule traces to something that actually went wrong. Detailed references live in [`manuscript/`](manuscript/).

## The two ideas that matter most

### 1. A manuscript is a build artefact, and its renditions drift apart silently

The same claims typically live in several places: the DOCX co-authors read, the LaTeX submission, the graphical abstract, and the abstract and highlights. When only the *numbers* come from shared result files and the *sentences* are duplicated in each builder, the renditions drift: one runs revisions ahead, another carries superseded numbers, the graphical abstract recommends something the paper now disproves. Nothing fails.

**For every substantive claim, either generate all renditions from one source or write a parity check that asserts the claim in each rendition.** See [manuscript/rendition-drift-and-guards.md](manuscript/rendition-drift-and-guards.md).

### 2. Content vanishes inside one rendition, and the build reports success

- A four-column table with one long cell ran past the page edge and dropped most of its data cells from view. Exit code 0.
- A citation written without a year was never numbered and never reported as unresolved, because the resolver only matched four-digit years.
- A stale figure map put the wrong artwork under most captions, in both PDF and DOCX.
- Moving supplementary content into the main text orphaned figures and left pointers aimed at floats that no longer held the claim.

These pass every structural check. They are caught only by rendering the artefact and reading what came out. See [manuscript/silent-loss-and-verification.md](manuscript/silent-loss-and-verification.md).

**"No errors reported" is not "no errors."** Design every check to fail loudly, and treat any silent pathway (a filter that can match nothing, a clamp, a hard-coded range, a width-blind layout rule) as a defect waiting to happen.

## Workflow

1. **Freeze results before writing.** Results go to JSON or JSONL with a SHA-256 per file; assert the checksums on every rebuild.
2. **Write from data, not memory.** Every number in prose, figures, abstract and highlights is interpolated from result files (a single `numbers.json` works well). Recompute from raw output; never verify prose against the table that reports it.
3. **One source of truth.** Exactly the source files are editable (for example Markdown); PDF, DOCX, LaTeX and the supplement are generated. Hand edits to generated files are lost on the next build. See [manuscript/markdown-to-latex-build-chain.md](manuscript/markdown-to-latex-build-chain.md).
4. **Write for both reviewer axes up front**: structure and register, and epistemic rigour. See [manuscript/reviewer-comment-patterns.md](manuscript/reviewer-comment-patterns.md) and [manuscript/claim-rigor-simulation-papers.md](manuscript/claim-rigor-simulation-papers.md).
5. **Figure QA**: effective DPI at print width, legibility at reproduction size, caption-to-artwork pairing. See [manuscript/figure-and-diagram-qa.md](manuscript/figure-and-diagram-qa.md).
6. **Compile and read every page.** Static validation is not a compile. Look for overfull boxes, table bleed, split floats, orphaned captions and undefined references. In Word, check that equations and tables are editable and that affiliations sit under the author names.
7. **Review in parallel dimensions** (below).
8. **Guard everything, then hand back.** Turn each fixed defect into a check that fails loudly if it returns.

## Multi-agent review

About four agents in parallel (more burns budget without new findings), each told not to trust the manuscript's arithmetic or helper outputs and to recompute from raw data. Use a CRITICAL / IMPORTANT / COSMETIC rubric, and adversarially verify the most damaging findings yourself before relaying them. Dimensions used across projects:

- journal-reviewer personas (simulation methodologist, domain climatologist, materials expert, methodologist and uncertainty);
- numeric integrity and traceability; citation and reference integrity; build output and float integrity; figure correctness;
- claim-evidence discipline; reviewer coverage and editor compliance;
- readability and cognitive load; connective tissue and narrative architecture; humanisation and authorial presence; register and house style; sentence craft; read-aloud ear; first-time-reader simulation.

See [manuscript/multi-agent-review.md](manuscript/multi-agent-review.md).

## Supervisor and co-author comments

- Read comments in the shared DOCX, extract them to JSON **before** any rebuild, and apply them to a **new copy** that keeps the comment threads visible.
- Give comments about 70% weight: use judgement and evidence for each, push back with data where needed, and do not rewrite the supervisor's own prose extensively.
- When the supervisor's words are contradicted by the data, change them while keeping their wording and structure, and flag it for their decision.
- Build a **regression checker, not a to-do list**: one assertion per comment, run before every hand-back. Name the lists generically (`SUPERVISOR_ROUND_1`).

```python
SUPERVISOR_ROUND_1 = [
    ("no first person", lambda: not re.search(r"\b[Ww]e\b|\bour\b", body)),
    ("matched no-latent control exists", lambda: "latent heat disabled" in text),
    ("no em dashes", lambda: body.count(chr(0x2014)) == 0),
]
```

- Reply with a short message listing the decisions needed. See [manuscript/collaboration-and-supervision.md](manuscript/collaboration-and-supervision.md).

## Revision after peer review

1. Parse the decision letter into a plan of action.
2. Add analyses **additively**: frozen results stay untouched, and every new script first asserts it reproduces them.
3. Write the response letter in a non-defensive tone, plus the highlighted manuscript (latexdiff without bibliography noise, or Word with changes highlighted).
4. Split the response into per-reviewer files plus an editor response when the portal requires it, and produce the portal's Word upload from the canonical DOCX after every rebuild.
5. When reviewers say a paper "reads as an experimental report", change the claim (for example to a quantified validity envelope), not just the wording.

## After rejection

Diagnose the novelty failure. Mine the last ~100 related papers for stated limitations and future work, with forward and backward citation tracking, and list paywalled papers to request. Re-anchor the novelty on a specific prior claim the results contradict, propose a new dimension, run a small pilot, and get approval before extending. Archive removed content verbatim in a `FUTURE_PAPER_<topic>.md` file to seed a later paper.

## Document-engineering rules

- **Never edit a copy.** Patch the canonical builder; a fixed scratchpad copy ships the right document while the project builder regenerates an older one.
- **Auto-numbering hides manual-numbering bugs.** LaTeX numbers floats by source order, not label; a table defined out of order renders under the wrong number.
- **Renumbering strands pointers in the other document.** After any renumber, check each cross-reference against what the target actually contains.
- **Write patch scripts as files, never shell heredocs**, make them atomic and assert every anchor.
- Escaping hazards: `\%%` in a `%`-formatted string truncates; `"\textbf"` in generated Python source turns `\t` into a tab; `%` binds tighter than `+`.
- Captions must be bold end to end in the Markdown source or `\ref` breaks; `\resizebox` decisions must be width-based.
- Filenames are an interface: a regenerated figure can silently overwrite a hand-made one with the same name.

## Cutting to a word limit (cheapest first)

1. Procedural narration and restatement.
2. Literature-review prose, keeping the citations.
3. Method detail with a supplementary home.
4. The same number stated in two sections.
5. Whole coherent blocks moved to the supplement, with a summary sentence left behind.
6. Argument (expensive; ask first).

Rephrasing does not shorten; deleting sentences and moving blocks does. Measure after every pass. See [manuscript/literature-citations-and-length.md](manuscript/literature-citations-and-length.md) and [manuscript/submission-compliance.md](manuscript/submission-compliance.md).

## Pre-hand-back checklist

```
 1. results unchanged         sha256 of every result file == baseline
 2. reviewer regression       every past comment still addressed
 3. derived metrics           definition, n, basis, independent estimator for each
 4. structure                 environments, tables, refs, citations, escaping
 5. rendition parity          every claim and table in ALL renditions
 6. cross-references          every target exists AND contains what the sentence claims
 7. citations                 all resolve, including citations lacking a year
 8. figures                   caption-to-artwork hash pairing; effective DPI at print width
 9. COMPILE and read the PDF  overfull == 0, undefined == 0, no lost table cells
10. limits                    abstract, word count, display items, highlights
11. snapshot                  versioned copy with date and descriptive slug
```

Steps 1 to 8 are cheap and catch regressions. Step 9 catches what the others cannot.

## Reproducibility packages

A reviewer package holds code, weather files, model inputs, result JSONs, a tiered `verify.py` (tier 1 without the simulator, tier 2 full re-simulation), pinned requirements, `config.json`, README, data provenance, `MANIFEST.sha256` and `expected_results.json`. It never holds document-generation scripts or assistant and session identifiers. See [manuscript/reproducibility-and-packaging.md](manuscript/reproducibility-and-packaging.md).
