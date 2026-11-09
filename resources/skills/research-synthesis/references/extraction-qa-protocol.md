# Extraction QA protocol (agents reading full texts)

Version 2026-11-09. Use this for phase 5 when extraction is shared between agents or people.

## 1. Batches and prompts

- Build page-balanced batches (about 170 to 200 pages each) of the included records that are not yet extracted.
  Each batch row carries the record key, its screening fields, the page count and the path to the paper's Markdown.
- Write one prompt file per review. Each agent gets only "follow this file with batch = X". Every agent reads the
  same rules, and a correction reaches all later batches at once.
- Run a first wave that covers every review, so a prompt fault shows early. Then refill each slot as a batch ends.
- Give each agent a private scratch folder. Agents never edit shared files.

## 2. Rules for the extraction agent

- One row per batch row, in batch order. The key column always holds the batch key, never a placeholder.
- Copy every number exactly as printed, with unit and condition. Do not round or convert. If abstract, text and
  conclusion disagree, give each value and where it appears.
- Derived numbers go in notes, labelled "derived".
- Copy equations as printed. A correction goes in notes, labelled, never into the equation.
- Long documents (over 120 pages): read by chapter. List every chapter not read in full in `source_read`.
- If a value is unreadable, say so. Do not guess.
- Report back: counts, excluded keys with codes, the strongest results, reading problems, and uncertain copies.

## 3. Checks at merge

1. **Header check.** The merge script asserts the header of every batch file.
2. **Key check.** Every key matches the review's key pattern and the batch. A key fault is fixed from the batch
   file in batch order, confirmed by title overlap, and the original is kept.
3. **Number trace.** Every number in the quantitative fields of an included row must appear in the paper's
   Markdown or its page-read sidecar, after stripping whitespace and markup characters. Flag a row when more than
   30% of its numbers are missing. Then look at why: an image-only table read from the page is a known, acceptable
   cause; a number that comes only from a model's figure description is not.
4. **Wrong-PDF audit.** Compare title words of the first pages with the record for every paper in the batches.
   Log each mismatch for a new download or a new record.

## 4. Lead-reviewer pass

- Keep one lead-notes file per review. Log each flag as it arrives: borderline eligibility, contradictions inside
  the paper, wrong files, rule questions.
- Resolve contradictions by reading the page or recomputing, never by rewording.
- Rule-level questions (for example, whether theses count) go to the person who owns the protocol. Record the
  decision as a dated protocol amendment.
- Run one lead pass after all batches, not after each one.

## 5. Agreement and sensitivity

- **Dual extraction.** A fresh agent re-extracts a random 10 to 15% of rows without seeing the first CSV. Report
  agreement per field. Disagreements go to the lead pass.
- **Sensitivity analysis.** Re-run the synthesis with each contested rule flipped (theses in or out, borderline
  includes in or out). Report which conclusions change. This turns a preference into evidence.

## 6. Loop

Propose, test on a subset, ablate, critique, revise. The final gate stays with a person: automated reviewers can
score a draft, they cannot accept it.
