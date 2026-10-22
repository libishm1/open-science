# Working with authors and supervisors

Learned from the request stream itself (the author's instructions and the supervisor's comments)
rather than from the paper. This is the part that generalises least obviously and matters most.

---

## Resolve *which artefact* before acting

A supervisor's comments arrived as: *"Move these back to main manuscript"*, *"all of them"*,
a filename, *"Limitation section is too long"*.

Three ambiguities, all resolvable **without asking**:

1. **Which document?** The named PDF had more pages than the paper under discussion. Searching the
   filesystem found it in a **different project entirely**. Acting on the assumed document would have
   edited the wrong manuscript.
2. **Which pages?** A page range, but of what? The supplementary, whose first page in that range is
   literally headed *"Tables moved from the main text"*.
3. **How many?** The author guessed "three pages"; it was four, holding exactly five tables and five
   figures, which explained the otherwise cryptic request to cost "five figures and five tables".

**Rule.** When an instruction references a document, a page range or a count, verify each against the
actual artefact before touching anything. Page counts, headings and filenames are cheap to check and
they disambiguate almost every terse instruction. Say plainly which document you concluded it is.

*(That round ended with "ignore, wrong window"; the verification is what made that harmless.)*

---

## Terse, typo-laden instructions still carry precise intent

Real examples and what they meant:

| Instruction | Intent |
|---|---|
| "make trgew melt percentages larger maybe and to the side" | font size *and* position, in one figure |
| "ita thew fixed 45 degree that needs fixing" | a correction to *which* artefact I had fixed, not the one I chose |
| "dont change just answer me lease" | **answer the question; do not act** |
| "or is it opitmal for PCM?" | a physics question, not a change request |

**Rules.** Act on the request, not the spelling. Distinguish *questions* from *instructions*: a
question about a design choice wants reasoning, not a rewrite. When corrected about which artefact,
re-read the correction literally; the author usually knows exactly which one they mean.

---

## Honour explicit author decisions without relitigating

- Name spellings, affiliation wording, email case, exactly as given.
- Funding text verbatim from the funder.
- Where a venue policy bears on a decision that belongs to the responsible author, flag the relevant
  policy **once**, clearly, then leave the decision with that author and stop raising it.
- Analyses explicitly ruled out (for example daylight or glare metrics) stay out, but **record them as
  an open item** with whose decision it was, because a reviewer may reopen it.

Flag once, decide once, record the decision, move on.

---

## Supervisor comment styles, and what each is really asking

*"How? The Validation Process. Can you list the process of Validation."*
→ Not "add the word validation". Asking for a **named, enumerable process** with levels and what each
one proved. Answer with a structure, not an adjective.

*"Many papers do not include comprehensive uncertainty studies. It is good to have it but not
essential."*
→ A deferral, not a rejection. Do the **cheap version** anyway if another claim depends on it. Here,
the uncertainty run was what licensed the "these three cases are equivalent" claim, so it was worth
doing despite being optional.

*"Move these back."* / *"Yes all."*
→ Terse and complete. The ambiguity is in the referent, not the intent. Resolve the referent.

**A long list of numbered comments in an email.**
→ Respond in **their numbering**, say what changed and where, and never mark something addressed that
is not. Build the regression checker from this list.

---

## Communication artefacts are deliverables

When a supervisor communicates by instant message, a *ready-to-send message* is worth more than a
report:

- Before an expensive run: ask for approval **with the cost attached**. "Bidirectional coupling, well
  under a minute per case, the full response in minutes" turns "let's not" into "run it".
- After: a short factual message, not a summary of your process.
- Keep it to the length that platform expects: a 30-word message, when asked for one.

State **compute cost** up front. Establishing that the whole reviewer response was minutes, not hours,
changed which analyses were considered feasible at all.

---

## Tiered explanation on request

Asked to explain the paper *"like I'm five"* and then *"like I'm in college"*: two genuinely different
registers of the same content, not the same text with shorter words. Both are legitimate deliverables;
build the second on the first rather than restarting.

---

## Shared-file discipline

The manuscript lived in a synced cloud folder with co-authors editing concurrently.

- **Never** `mv`/rename over the shared file; it breaks the share link others hold. Write in place.
- When swapping a reviewed copy for a clean one, **keep a backup, retain the reviewer's comments in the
  archived copy**, and confirm which file is the one to circulate.
- Expect the file to be **locked by Word**. Have a fallback path and a stamp/checksum guard that
  refuses to overwrite a hand-edited canonical file.
- Snapshot to `_versions/` with a date and a descriptive slug before and after any swap.
- When the author asks *"is this the right one to share?"*, verify the actual file; don't answer from
  memory of what you built.

---

## Cost-aware assistance

The author repeatedly steered toward cheap, bounded work: *"keep it cheap, just two agent previews"*.

- Prefer two targeted reviews over a broad sweep.
- **Verify agent findings** before acting. One review cited entities that did not exist: artefacts of
  the very defect it was reporting. Of five findings: three real, one real-but-misdiagnosed, one
  correct-as-is. Acting on all five unchecked would have introduced errors.
- Report which findings were *rejected* and why. That is as valuable as the fixes.

---

## When you find a problem the author did not ask about

Both of the most serious defects were found while doing something else:

- the unavailable night-ventilation sink (found while writing a section)
- the stale builders and a LaTeX rendition several revisions behind (found while fixing figure labels)

Report them **immediately, plainly, with the evidence**, and fix them in the same pass if they affect
what was asked for. Do not bury them in a summary. Say what it would have cost: *"submitting this would
have shipped superseded numbers and reopened settled reviewer points."*

Equally: when a follow-up question implies you may have missed something, **check rather than defend**.
"Is the graphical abstract up to date?" was a question, and the honest answer was no: it had been
stale for several revisions and contradicted the paper's own section.
