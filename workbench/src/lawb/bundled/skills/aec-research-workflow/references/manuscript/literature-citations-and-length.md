# Literature, citations, and cutting to a word limit

Three problems that turn out to be one problem: a reference list is simultaneously a scholarly
claim, a compliance object, and a word budget.

---

## 1. Verify claims against the originals, and say what you could not get

Project B verified every statement attributed to a primary study against the original publication
wherever it was accessible, and stated the score in the paper, in this form:

> full texts were obtained and checked for N of the M principal sources; the remainder are cited
> from abstracts and indexing metadata and **support no reported result**.

That last clause is what makes the disclosure useful rather than an admission. Verification corrected
a number of claims, including one that *widened* the paper's novelty: the nearest antecedent turned
out not to show the effect at all, which was the gap being claimed.

**Rules**
- A source you have only read the abstract of may motivate, but must not support a reported result.
- Record the verification state per source in a register, not in your head.
- Institutional access is usually publisher-scoped (often to only a few publishers). Expect a
  permanent unobtainable set and confine it to the review.
- "Purposive rather than exhaustive" is an acceptable selection policy; silence is **not**.

---

## 2. Citation resolution is a place things disappear

See [silent-loss-and-verification.md](silent-loss-and-verification.md) for the full case. The short
version: a resolver that matches author-year patterns **requires a year**, so a citation written
without one is neither numbered nor reported as unresolved. Always pair the resolver with a negative
check:

```python
bare = re.findall(r"\b([A-Z][\w'-]+(?: et al\.)?)(?!\s*\()(?=[ ,;.])", body)
```

Other citation hygiene that reviewers and submission systems check:
- **Uncited references** are a liability. A supervisor asked for a supplementary bibliography of
  consulted-but-uncited works to be deleted outright: *"unnecessary length without increasing the
  paper's scientific value."* Some publishers' submission systems flag uncited entries automatically.
- Keep the in-text surname form and the reference-list form consistent, especially for hyphenated
  and accented surnames (a hyphen dropped in one place, or `ø` written as `o`).
- Pick one of `and` / `&` and enforce it.
- References need **volume and pages**, not just DOIs. Verify against Crossref.
- Distinguish genuinely different works that collide on first-author-and-year with `a`/`b` suffixes,
  and make sure the master pool prints them distinguishably too.

---

## 3. Reference count: thin is a defect, long is a cost

Two supervisor instructions that sound contradictory and are not:

> *"Check references too. Why they are reduced so much"* (after an aggressive cut)
> *"[N] references is enough"* (after the full review had been restored, well above N)

The supervisor objected to a **thin** list, not a **short** one. What was wanted was coverage of the
field, not volume. The resolution that worked:

1. Restore the full literature review to fix coverage.
2. Then cut **sources**, not prose, by keeping every load-bearing citation and dropping corroborating
   ones whose claim is already carried by a stronger source.
3. Protect two categories absolutely:
   - any source cited **outside** the literature review (methods definitions, standards)
   - any source that is the **sole support** for a stage of the argument

The second category is why the final count came in one above the requested number: dropping the
verification-methodology reference to hit a round number would have left an entire evidence stage
unattributed. Say that out loud rather than silently missing the target.

**Procedure for a reference cut:**

```python
s2   = keys(section_2)          # review-only citations
rest = keys(everything_else)    # protected: cited outside the review
budget = TARGET - len(rest - s2)
# drop from s2 only: corroborating sources whose claim survives via a stronger citation
```

---

## 4. Cutting to a word limit

**Measure first**, per section. A per-section word count tells you where the words are and prevents
shaving evenly across a paper, which damages everything and saves nothing.

### The order that costs least

1. **Procedural narration and restatement**: free.
2. **Literature-review prose, keeping every citation**: cheap; no result depends on it.
3. **Method detail that has a supplementary home**: cheap.
4. **The same number stated in two sections**: free. (One draft stated a U-value change in both
   Methods and Results; one had to go.)
5. **Whole coherent blocks moved to the supplement with a summary sentence left behind**: moderate.
6. **Argument**: expensive. Ask before doing this.

### Rephrasing does not shorten

The single most useful empirical finding here. Repeated "write it more concisely" passes each returned
only a small fraction of their word-saving targets. Dense academic prose is already dense; the words
are in the *structure*, not the phrasing.

**What actually works:** deleting whole sentences, merging citation-dense sentences, moving blocks,
and removing duplicate statements of the same fact. Measure after every pass, and **stop rewriting**
once a pass returns less than half its target; that is the signal to switch from rephrasing to
deleting.

### Moving a block correctly

```
1. cut the block whole
2. leave a sentence in the main text that keeps the FINDING and points to the supplement
3. append the block to the supplement under a numbered section
4. re-check: numbering contiguous, pointer resolves, nothing orphaned
5. re-measure
```

Never leave a heading with no body, and never move a block whose conclusion the main text still
relies on without leaving that conclusion behind.

### Display items count too

Figures and tables consume the word budget and are separately capped. Some journals treat
**figures + tables > 20** as a desk-rejection trigger. Two ways to cost them:
- the flat convention (~250 words per item), or
- measured: the document's own words-per-full-page × the column height each item occupies.

In Project A the measured cost came to about half the flat convention's figure. Give **both**, and say
which the journal uses.

When over the float cap, the first candidates are figures whose content the paper has outgrown: a
literature-network figure whose prominent nodes are sources a later trim removed is both the least
load-bearing figure and an active liability.
