---
name: research-synthesis
description: Method for running a literature review and a cross-disciplinary synthesis that is reproducible and counted. Three tiers - PRISMA 2020 for the counted funnel and corpus statistics, a per-algorithm extraction card for derived math and code seams, and ROSES-style narrative synthesis across disciplines with an evidence map, compatibility matrix and verdicts. Includes a gap-analysis procedure (unstudied combinations, unmeasured parameters, unvalidated methods, cross-domain transfer gaps) and the counting and honesty rules that keep the output defensible to reviewers. Use for literature reviews, state-of-the-art surveys, systematic or scoping reviews, gap analysis before a paper, and any "what is known, what is missing" question across fields.
license: see repository LICENSE
---

# Research synthesis: counted, traceable, cross-disciplinary

This skill is a procedure. It contains no conclusions about any field.
Fill it with your own sources, counts and verdicts. Every claim the output
makes must trace to a source, a count, or a derivation.

## When to use

- A literature review or scoping review that must be reproducible.
- A gap analysis before a paper, grant or design decision.
- A synthesis that spans fields with no shared effect size.
- Checking whether a "novel" or "first" claim survives a search.

Do not use it for a single-paper summary. Use a reading note for that.

## The three tiers

| Tier | Method | Owns | Answers | Native artifact |
|---|---|---|---|---|
| T0 | PRISMA 2020 | Counts: the identification-to-inclusion funnel, corpus statistics, comparability on one shared metric, risk-of-bias | How many entered, how many survived and why, what the included base looks like | PRISMA flow, corpus tables and plots, risk-of-bias table |
| T1 | Extraction card | Per-algorithm or per-method detail: derived equations, code seam, complexity, numeric pitfalls | For this one method, what is the math and where does it break | One card per included method (schema in `templates/extraction-card.md`) |
| T2 | ROSES-style synthesis | Narrative across non-commensurable methods and disciplines: evidence map, compatibility matrix, verdicts | Across fields with no shared effect size, which method fits which direction, scale and discipline, and why | One synthesis per domain (template in `templates/roses-synthesis.md`) |

PRISMA counts and compares. The card derives and binds. ROSES synthesizes.
Do not let one tier do another's job. Counts belong to T0. Equations belong
to T1, derived from definitions, not copied from a PDF. Verdicts belong to T2.

### Decision rule between T0 comparison and T2 narrative

Write a head-to-head comparison table only when you can name the shared
metric in one sentence. If you cannot, the comparison is narrative and it
belongs in T2. Record this decision in the protocol.

## Phase pipeline

1. **Prior-work query first.** Search the local knowledge base and prior
   reviews for the topic. If a current review exists, load it and stop
   re-searching. Record the query.
2. **Write the protocol before searching.** Research questions, PICO or
   PECO (or its algorithm analogue), search strands, engines and databases,
   inclusion and exclusion criteria, and the search class (see P5). Commit it
   before the search runs.
3. **Identify and screen (T0).** Run each strand. Deduplicate. Screen on
   title and abstract. Assess eligibility. Count every exclusion and give its
   reason. Emit the flow.
4. **Corpus statistics (T0).** Tabulate the included set by sub-topic, year,
   source type, open access, discipline and evidence tag. Plot the figures.
   Save the data so the plot can be regenerated.
5. **Extraction (T1).** One card per included source that defines a method.
   Derive equations from definitions. Do not transcribe equations from PDF
   text without checking them.
6. **Pitfall pass (T1).** Run the pitfall checklist against the paper and
   against any implementation. Resolve each flag or waive it with a reason.
7. **Synthesis (T2).** Cluster cards by discipline and by the pipeline stage
   they inform. Write the evidence map (citing T0 counts), the cross-discipline
   appraisal, the compatibility matrix and the verdicts.
8. **Feedback loop.** An under-covered discipline or stage becomes a new
   counted T0 strand. Re-run the screen for that strand only.
9. **Gap analysis.** Run the procedure in `references/gap-analysis.md` on the
   synthesis output.
10. **Check and hand off.** Run the reviewer checklist (below). Save all data
    and the protocol with the output.

## Counting and honesty rules

These rules apply to every output. A reviewer should be able to re-derive
every number from the included list.

- **P1 Count or do not claim.** Replace "many", "several", "most" with a
  count when a count exists.
- **P2 Reasons are counted.** Every exclusion carries a reason and a number.
- **P3 Comparability needs a one-sentence metric.** Otherwise it is narrative.
- **P4 Tag every source's key value.** Use `[measured]` when the value comes
  from that source, `[lit-default]` for a textbook or handbook value,
  `[anchor]` for a method-class origin with no value. Score risk-of-bias on
  these tags.
- **P5 Declare the search class.** Either an exhaustive census or a rapid,
  AI-assisted, targeted map. Give downstream counts exactly. Label upstream
  identification counts as approximate when they are. Record an exhaustive
  re-run as a named next step. A rapid map is not an exhaustive census.
- **Grounding.** Every claim traces to a full text, a verified abstract, or
  code. Never state a claim from memory.
- **Citations.** Verify bibliographic data against Crossref or the publisher
  before writing. Number citations by first appearance.
- **No unsupported novelty.** Do not call a method "novel", "first", or
  "state of the art" unless a search of the stated scope supports it. Write
  the search scope next to the claim.
- **Style.** No em dashes in generated text. Short declarative sentences.

## Gap analysis (short form)

A gap is a claim the evidence does not yet support. Classify each gap
before ranking it. Full procedure: `references/gap-analysis.md`.

| Gap type | Test |
|---|---|
| Unstudied combination | Two methods, or a method and a domain, with no source that applies both |
| Unmeasured parameter | A parameter the model needs with no measured source, only defaults |
| Unvalidated method | A method with no comparison to measurement or to a reference |
| Transfer gap | A result from one domain or material with no test in the target domain |
| Scale gap | A result at one scale with no test at the scale of use |

Rank gaps by impact on the question and by how much a single new study
would close them. Each ranked gap cites the T0 counts and the T1 cards that
show it.

## Reviewer checklist

- [ ] Protocol committed before the search. Search class declared (P5).
- [ ] Every exclusion has a count and a reason (P2).
- [ ] Every number re-derivable from the included list (P1).
- [ ] Each comparison table has a one-sentence shared metric (P3).
- [ ] Each source's key value tagged (P4).
- [ ] No equation transcribed from a PDF without derivation or check.
- [ ] Every novelty or gap claim has a search scope attached.
- [ ] Citations verified; numbered by first appearance.
- [ ] Data and figures saved so they can be regenerated.
- [ ] Each verdict names the discipline, stage and scale it applies to.

## Files

- `references/gap-analysis.md` - full gap procedure and ranking rubric.
- `templates/prisma-flow.md` - counted flow and corpus statistics template.
- `templates/extraction-card.md` - per-method card schema.
- `templates/roses-synthesis.md` - cross-disciplinary synthesis template.
- `templates/protocol.md` - protocol to commit before searching.

## Failure modes

- **Counts without a denominator.** A count with no screened base cannot be
  checked. Always show the funnel.
- **Narrative masquerading as comparison.** A table that ranks methods on
  different metrics. Move it to T2 or name the shared metric.
- **Copied math.** An equation pasted from a PDF with a typo that propagates.
  Derive it or check it against the source definition.
- **Gap inflation.** Listing every unstudied combination as a gap. Rank them
  and drop the ones a single study would not move.
- **Search drift.** Changing the strands after seeing results. Keep the
  protocol and log any change as a dated amendment.
