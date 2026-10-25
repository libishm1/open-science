# Reviewer-comment patterns

Generalised from a few dozen real comments across two review rounds on Project A, plus two further
comment waves on Project B (DOCX threads and relayed messages). They cluster into two nearly
orthogonal axes. Write for both before the first hand-back and most of the round disappears.

Axis C, at the end, covers what only showed up in Project B: comments about *the paper as a
compliance object* rather than as an argument.

---

## Axis A: Structure, register and readability
*(Roughly half the comments. Typical of a senior supervisor reading as an editor would.)*

### A1. Title and keywords
- Title states the **contribution**, not the setup. Strip the model, the code name, the city
  from the title if they are not the finding.
- Keywords must be what a reader would **search**, not what the paper contains. A national code
  number is a poor keyword; "cooling load", "thermal comfort", "dynamic louvres" are good.
- Do not repeat title words in the keyword list.

### A2. Register
- **No first person.** `\b[Ww]e\b|\bour\b` should return nothing in the body. This is the single
  most reliably requested change and the easiest to regress: every new paragraph risks it.
- No emphasis capitals, no bold for stress in body text.
- One consistent phrasing for a recurring ratio. The same fact appeared as a fraction, as "N times
  larger", as "N times more" and as "an order of magnitude"; pick one and enforce it.

### A3. Bullets are for engineering documents, not journal papers
- Contributions: a flowing paragraph ("The study contributes, first…"), not a bulleted list.
- Conclusions: prose, not bullets.
- Discussion: one continuous argument, not numbered subsections.
- Delete **verdict/scorecard tables** ("SUBSTANTIATED / NOT SUBSTANTIATED"). They read as an
  internal review artefact.

### A4. The supervisor's own words are non-negotiable
When a supervisor supplies wording for the aim or the conclusion, **use it verbatim** and assert it
in a regression test. Rewriting it "better" is the fastest way to reopen a settled comment.

### A5. Structure the methodology as named phases
Reviewers navigate methods by phase. Name them, number them, and make the workflow figure use the
**same phase labels** as the text. Rename vague subsections to what they contain
("PCM glazing model formulation", "Coupling strategy and calibration").

### A6. Introduce every table and figure before it appears
"Table N lists…" must precede the object. A table that appears before its introduction reads as
dumped. This also forces you to notice tables nothing refers to.

### A7. One figure, one message
A figure carrying three unrelated comparisons gets split into three. Overloaded figures are the
most common figure comment.

### A8. Literature review: one substantive sentence per study
Not a citation pile. What did *that* study do, and what did it find? Group by theme, and end with an
explicit **research-gap paragraph** that names the intersection nobody has occupied.

### A9. Split sentences that carry more than one job
A 65-word sentence carrying a formula, its meaning, its source and a caveat becomes two or three.

### A10. Say plainly when no experiment was performed
State it once, early, in the methods. It pre-empts the entire Axis-B "validation" thread.

---

## Axis B: Epistemic rigour
*(The other half. Typical of a methods-focused reviewer.)*

### B1. "Validated" is a loaded word
Use it **only** where physical measurement exists. Otherwise:
- *verified*: against another model or a higher-fidelity run
- *checked against manufacturer datasheets*: for material inputs
- *calibrated*: for a fitted factor

Keep **verification and validation distinct** and state which levels were possible without an experiment.

### B2. Decompose a headline number into mechanisms
"X % saved by the PCM" invites the assumption that X is latent storage. Run a **matched control**
(identical assembly, latent term disabled) and report the split. In Project A almost all of the
headline saving was optical and sensible, and only a small fraction was latent: the attribution was
wrong even though the number was right. Promote the control to a **named case in the results table**,
not a footnote.

### B3. Justify every calibration factor
Where did the scalar come from, what is it anchored to, and what happens if it moves ±10 %?

### B4. Verify the coupling per case, not once
A fidelity ladder validated on one configuration does not license the claim for all of them.
Re-run the high-fidelity coupling **per case** and report the range. This superseded an inherited,
larger error range with a smaller measured one, and the inherited number was still in the LaTeX.

### B5. Uncertainty is what licenses a ranking
If cases differ by less than a tenth of a point, the ranking means nothing unless the model
uncertainty is smaller. Perturb calibration, grid and timestep; report the largest shift; then state
explicitly which cases are **equivalent within uncertainty** and stop ranking them.

### B6. Give the full assembly
Layer thicknesses, conductivities, densities, heat capacities, optical properties, film coefficients,
and the assembly U-value/SHGC with what they are matched to. A table, not scattered sentences.

### B7. Attribute every non-published expression
If the functional form is your simplification, say so, cite what the end points come from, and state
where its influence is confined.

### B8. Define derived quantities
Any term doing analytical work ("charging day", "regeneration efficiency") needs an explicit
definition with its threshold.

### B9. Check units on every equation
A unit typo in a headline equation survives many readings. (`siunitx` has no `\year`; that one
rendered as `[kWh/]`.)

### B10. Do not claim what you did not compute
If no daylight metric was calculated, remove every "daylight-preserving" phrase and say plainly that
none was computed. Softening is not enough; delete the claim.

### B11. State comfort-model assumptions in full
Metabolic rate, clothing, air speed, and *why* the metric behaves as it does. An unexplained
"about half of occupied hours" reads as a failure rather than a strict threshold.

### B12. Scope every recommendation
Orientation, climate, code regime. Say where the result does **not** generalise.

### B13. Discuss durability and practicality
Cycling stability, UV, seals, leakage, fire, cost. Simulation papers routinely omit this and reviewers
routinely ask.

### B14. Include a literature-comparison table
Columns a reader needs to judge transferability: climate, configuration, treatment of the competing
variable, method, whether future weather was considered, and **the limitation this study addresses**.
Mark "not addressed" rather than inventing a value. Put your own study in the last row.

### B15. Explain how the references were selected
"Purposive rather than exhaustive" is acceptable; silence is not.

### B16. References need volume and pages
Not just DOIs. Verify against Crossref and archive the metadata.

### B17. Derive shares rather than asserting them
A claim such as "X % of the west-glazing load" needs the derivation of what the west-glazing share *is*.

### B18. Account for the energy your intervention consumes
Night ventilation has fan energy. Report it, or the saving is overstated.

### B19. Test availability assumptions against the model's own output
The highest-value comment in the entire round. Any assumed resource (cool air, waste heat, a sink,
a source) must be shown to exist in the simulated system. See the worked example in
[claim-rigor-simulation-papers.md](claim-rigor-simulation-papers.md).

---

---

## Axis C: The paper as a compliance object
*(Project B. A supervisor who submits regularly tracks screening rules personally and treats them as binding.)*

### C1. Hedge every absolute claim
> *"Avoid absolute claims. 'No study...' Better: 'To the best of the authors' knowledge, no previous
> study...' Editors prefer this."*

Never assert exhaustive absence of prior work. Applies to "the first", "the only", "none has".

### C2. Do not extrapolate a modelled response without demonstrating linearity
> *"I'd avoid stating that the effect would be 'roughly [X] °C'... unless we can demonstrate that
> the response is linear."*

The supervisor was right, and the verification runs proved it: one city absorbed **more** heat than
another yet shifted **less**, because the deeper canyon buffered it. Interpolating between two
simulated points is a claim about the response surface, and needs the same evidence as any other claim.

### C3. Describe mechanism, not paradox
> *"'inverted' may sound surprising. Maybe demonstrating that the [hypothesis] is supported for [one
> placement] but reverses for [another] governed by different heat-transfer mechanisms."*

A surprising result should read as explained, not as a twist.

### C4. Honesty is not the same as word count
> *"Just limitation is too long / can reduce, too honest."*

Keep every disclosure; cut the prose around them. A limitations section can halve in length without
losing a single admission.

### C5. Approved sections are frozen
> *"Conclusion is ok keep as it is."*

Once a section is explicitly approved, it is out of scope for later cuts. If a word limit later
forces the question, **ask again** rather than quietly compressing it.

### C6. Screening limits are hard limits
> *"Figures + Tables exceeds 20, might get rejected"* … *"yes hard limit."*

Track the journal's display-item cap, word limit, abstract limit and highlight character limit as
first-class constraints from the first draft, not at submission.

### C7. A thin reference list and a short one are different complaints
> *"Check references too. Why they are reduced so much"* (after an aggressive cut) … later
> *"[N] references is enough"* (once the full review had been restored, well above N).

Not a contradiction: the supervisor objected to poor **coverage**, not to a modest count. Fix
coverage first, then cut sources rather than prose. See
[literature-citations-and-length.md](literature-citations-and-length.md).

### C8. Do not pad the bibliography
> *"I would not include a supplementary bibliography unless the journal explicitly requests it...
> Listing additional uncited papers would likely add unnecessary length without increasing the
> paper's scientific value."*

Uncited references are a liability, not evidence of diligence.

### C9. Justify each methods block's existence
> *"I would add one concluding sentence that explains why this framework is necessary for the
> research question."*

### C10. Report the whole metric set you promised
> *"where is the other Performance metric. why just peak cooling load"* … *"provide graphs."*

If a set of metrics is promised in the introduction, all of them appear in the results, and
visualised rather than only tabulated.

### C11. Name what each evidence stage can and cannot establish
> *"make the terminology even more precise by distinguishing verification, validation, and
> corroboration, and explicitly explain why full end-to-end validation... is not feasible."*

This became one of the strongest parts of the paper. See B1 and
[claim-rigor-simulation-papers.md](claim-rigor-simulation-papers.md).

---

## When the data contradicts the supervisor's own words

It happened twice in Project B: the title and the abstract's closing sentence both asserted that urban
morphology reshapes the *optimal design*, and the results showed the optimum was almost always the
same across the densities studied.

**The move that worked:** change it, keep the supervisor's wording and sentence structure, and flag
it explicitly in a comment thread as the supervisor's decision to make. Both were accepted.

Never silently overwrite a supervisor's sentence. Never leave a contradicted claim standing either.

Related: extract the comments **before rebuilding anything**. Project B's commented DOCX was
overwritten by a routine rebuild; the comments survived only because they had already been pulled
verbatim into JSON. That JSON is now the authoritative record.

---

## Working the round

1. Extract every comment into **a numbered list** before changing anything, including ones you think
   are already addressed.
2. Work **in a copy** if the live file is shared and others may be editing. Swap deliberately, keep a
   backup, and never `mv` over a synced file; it breaks the share link.
3. Retain **the reviewer's comments** in the archived copy; strip them from the working one.
4. Write **a regression assertion per comment**. This is the deliverable that keeps paying.
5. Re-run it **before every hand-back**. Later revisions *will* undo earlier fixes silently.
6. Report back **per comment**, in the reviewer's numbering, saying what changed and where.
