# Multi-agent manuscript review

Several review rounds across Project B, each with four agents in parallel. This protocol found real,
submission-blocking defects every time it ran. It also produced confident nonsense every time it ran,
so the verification step is not optional.

---

## The shape that works

**Four agents, one dimension each**, run in parallel, with an explicit severity rubric.

| Agent | Scope | What it reliably finds |
|---|---|---|
| **Numeric integrity** | Recompute every reported table from raw outputs; internal contradictions; arithmetic that does not close | Wrong constants, stale numbers, ranges whose bounds exclude a real value |
| **Citations and references** | Run the resolver; orphaned claims; malformed keys; duplicates; sole-support references | Citations that vanished, claims left unattributed by a cut |
| **Readability and connective tissue** | Severed antecedents, dangling cross-references, voice consistency, figure dumping | Damage from large cuts; its highest-yield moment is right after one |
| **Build output and floats** | Read the LaTeX log; caption-to-artwork pairing; float counts through the pipeline; page geometry | Lost table cells, wrong artwork, misnumbering |

Four is the practical cap. Beyond it the token cost rises without new findings, and the agents start
reporting each other's territory.

---

## Prompt construction

Give each agent **the established facts**. Without them, agents re-derive settled questions and
report the settled answer as a finding. Project B's numeric agent was told, as established, facts of
this kind:

> - The PCM layer occupies CondFD nodes i to j, N nodes. Values on an N-node basis are CORRECT.
> - Phase change state enum: LIQUID = −2, MELTING = −1, FREEZING = +1, CRYSTALLIZED = +2.
> - Energy must be read from `eplusout.mtr`, not `eplusout.csv`.
> - Section 2 was just shortened; its numbers come from cited prior studies, not this study's data.

This single block removed an entire category of false findings that earlier rounds had produced.

Demand **a recomputed counter-value**. Require: file, line, stated value, computed value. A finding
without a counter-value is usually noise.

Require **explicit empties**. "State explicitly if a severity level has no findings." Otherwise
silence is ambiguous between *nothing found* and *did not look*.

**Warn** that the file may change under them. In the final round all four agents independently
flagged that the manuscript was being edited while they read it, and their line numbers drifted.
Ask them to re-verify against a final state and record a hash. Better: freeze the file for the
duration.

Scope the severity rubric to **consequence, not to taste**:
- CRITICAL: a wrong number that changes a conclusion, or a defect that blocks submission
- MAJOR: an inconsistency a referee would catch
- MINOR: cosmetic

Tell them **what not to do**. "Do not propose stylistic rewrites." "This trim was intentional; do not
recommend restoring it." Agents otherwise spend most of their output relitigating decisions.

---

## Verifying findings before acting

Agents are confident and frequently specific and wrong. Both projects hit this.

- Project A: an automated diagram review cited node labels that did not exist; they were misreadings
  *caused by* the label overlap it was correctly reporting. Of five findings, three were real, one was
  real but misdiagnosed, one was correct physics needing explanation.
- Project B: a review agent objected that repointing a claim to a particular table was wrong, because
  that table held best-case configurations rather than the subset the claim was about. **Correct**,
  and it exposed a table that had no home in either document. The same agent objected to a *different*
  repointing to the same table, which was **right**, and provable in one line by recomputing the
  percentage changes from the table's own values.

**Rule:** check every finding against the primary source before acting on it, and before defending
against it. The agent being wrong once says nothing about the next finding.

---

## What agents are good and bad at

**Good at**
- stale cross-references and numbering gaps
- build-output defects nobody would think to look for
- recomputing tables from raw data at a scale a human would not sustain
- noticing that prose promises N items and delivers fewer
- catching voice and register drift after a large edit

**Bad at**
- judgement calls about what to cut
- distinguishing "this is a deliberate editorial decision" from "this is an error"
- estimating consequence: they inflate severity
- respecting an established fact they were not told about

---

## Sequencing

Run the review **after** a substantive change and **before** rebuilding deliverables. In Project B the
order that worked was:

1. make the change
2. run guards (`check_order.py`, citation resolver, word count)
3. rebuild the PDF
4. launch the four agents against the rebuilt state
5. triage: verify each finding at source, fix CRITICAL and cheap MAJOR
6. rebuild, re-run guards, package

Doing the review before the rebuild wastes the build-output agent entirely.

---

## Turning findings into guards

Every confirmed finding becomes a check, or it will return. Project B's guard file grew directly out
of review findings:

```python
# from "figure captions defined out of order"
assert [int(m) for m in re.findall(r"- \*\*Fig\. (\d+)\.", caps)] == list(range(1, n + 1))
# from "table cells lost off-page"
assert log.count("Overfull \\hbox") == 0
# from "citation with no year silently dropped"
assert not re.findall(r"\b[A-Z][\w'-]+ et al\.(?!\s*\()", body)
# from "em dashes reintroduced by a later edit"
assert body.count("\u2014") == 0
```

The guard is the deliverable. The finding is just how you learned you needed it.
