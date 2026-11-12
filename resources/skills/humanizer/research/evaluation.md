# Evaluation protocol and paper ideas

This is a proposed study, not experimental results. Freeze the protocol before collecting test outcomes. Power and sample sizes should follow a pilot variance estimate and a stated smallest effect of interest.

## Questions

1. Does a venue- and section-aware editor improve expert-rated clarity over generic Humanizer and unedited drafts?
2. Does editing preserve claims, uncertainty and evidence better when conservative guards are enabled?
3. How much do apparent style improvements depend on author, topic, source model, quantization and judge?
4. Do repeated rewriting and automated review reduce errors or merely improve scores from familiar judges?

## Corpus construction

- Use a primary historical stratum from 2010–2019, a separate 2020–29 November 2022 stratum, and a contemporary stratum. Include older anchors where useful. Dates indicate publication era, not guaranteed authorship provenance.
- Balance venue, article type and section. Do not pool abstracts with methods or randomized trials with case reports. Keep whole-document links so local edits can be checked against definitions and results elsewhere.
- Record DOI, version, publication date, retrieval date, source URL, license, correction history, article type, section and text hash. Record author provenance only where legitimately documented; do not infer native language from names.
- Preserve train/dev/test separation by paper, author group and near-duplicate family. Hold out entire venues and model families for transfer tests. Check overlap with the local model's disclosed training data before calling a sample held out.
- Collect permitted texts; an abstract visible online is not automatically licensed for redistribution or training. Publish identifiers and acquisition scripts where full-text redistribution is unavailable.
- Use the current historical table as a retrieval seed. Do not fit frequency targets to this purposive pilot.

## Conditions

Compare unchanged text, generic skill editing, academic skill editing, local rewriter alone, local rewriter plus guards, and a domain editor reference. Run source-identical paired comparisons. Keep model version, full prompt hash, seed where supported, sampling, quantization, token budget, attempts, wall time and chosen candidate. Report every generated candidate, not just attractive examples.

Do not add journal instructions to the local rewriter's trained completion prompt and call that a validated configuration. Test prompt modifications as a separate experimental arm. Current profile flags in the patch label audit context only.

## Outcomes

Primary: claim preservation and domain-reader clarity. Score claim additions/omissions, changed negation, causal strengthening, uncertainty loss, unit/denominator errors, citation misattachment, and inconsistency with tables or code. Track unchanged-original fallback separately from successful rewriting; otherwise a conservative system can appear perfect by never editing.

Use two qualified independent reviewers for a subset, adjudicate disagreements, and report agreement with uncertainty. Blind and randomize presentation order. Rate precision, flow, venue fit and author voice separately. Readability and lexical diversity are secondary descriptive metrics, not quality proxies.

Analyze paired outcomes with paper/author clustering; report effect sizes and confidence intervals. Predeclare multiplicity handling. Include failure rates, abstention/fallback rates, latency and cost. Do not silently remove truncations or failed runs. A test suite confirms software behavior; it cannot establish empirical writing quality.

Detector and model-attribution tests, if run, are secondary audits with frozen versions, matched human controls, false-positive rates and out-of-domain tests. Do not optimize against the final held-out detector. A lower score does not prove human authorship or removal of all model information.

## Ablations and closed-loop checks

Remove venue context, section context, author examples, protected terminology, uncertainty checks and artifact grounding one at a time. Test one pass versus repeated passes. For research-agent drafts, compare a prose-only review loop against an experiment-backed review loop at equal compute budgets. Use an independent final judge and frozen test data. Cap iterations and report unresolved failures rather than looping until a favorable score appears.

Before final release, inspect citation existence **and claim support**; recompute reported results from frozen outputs; compare method prose with actual code/configuration; verify data split and protocol compliance. These are proposed checks beyond the implemented text guard.

## Six candidate papers

Venue suggestions below reflect topical fit, not verified calls, fees or acceptance predictions. Check current scope before submission.

| Working title | Research contribution | Core experiment | Candidate venue |
|---|---|---|---|
| **Scientific Style Before ChatGPT: A Cross-Venue Corpus of Engineering and Architectural Research** | Versioned, licensed benchmark distinguishing venue, section and era | Annotate historical corpus; estimate within- versus between-venue variation; compare generic phrase flags with expert judgments | Applied Sciences; a corpus/academic-writing journal if linguistic contribution is strongest |
| **Claim-Preserving Local Rewriting of Engineering Manuscripts** | Auditable editing with selective fallback | Paired evaluation on Results in Engineering and materials/construction texts; errors versus edit coverage; guard ablations | Results in Engineering or Applied Sciences |
| **Preserving Design Intent in AI-Assisted Architectural Writing** | A rubric for computational method, design rationale and fabrication evidence | Blinded CAADRIA/eCAADe passage review by architects; compare generic, venue-aware and author-aware editing | CAADRIA / eCAADe, subject to event scope |
| **Uncertainty Loss During Automated Clinical Manuscript Editing** | Error taxonomy for hedges, causal scope, endpoints and harms | Clinical editors annotate trials, observational reports and cases; causal-strengthening and omitted-harm rates | A medical-writing, biomedical-informatics or research-integrity journal |
| **From Reviewer Scores to Reproducible Claims in Robotic Research Agents** | Separation of manuscript rating from artifact-grounded validity | A bounded ScientistTwo-inspired loop on reproducible robotic scene or fabrication tasks; compare text-only rebuttals with new experiments | Robotics/computational-design venue; Applied Sciences for an application-led study |
| **Does Rewriting Erase or Replace Model Style?** | Cross-model attribution and fidelity under repeated edits | Unseen-model transfer, human controls, multiple quantizations and 0/1/3 passes; assess semantic drift alongside attribution | NLP or empirical academic-writing venue |

Recommended starting paper: claim-preserving local rewriting. It has a concrete implementation, falsifiable outcomes and a manageable scope. The corpus paper can supply its benchmark; it should be a separate publication only if the dataset and analysis provide a substantial independent contribution.

For the robotics paper, test feasibility metrics, object/joint configurations, scene difficulty and simulator sensitivity. A robotically fabricated result needs physical validation appropriate to the claim; simulated improvement alone cannot establish site deployment performance.
