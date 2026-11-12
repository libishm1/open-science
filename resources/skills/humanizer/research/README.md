# Academic writing evidence and integration

Research cutoff: 9 November 2026. This is a scoped evidence review and an implementation prototype, not a completed systematic review, publisher endorsement, or validated authorship detector.

## What this changes

Humanizer should edit for the reader, discipline, article type and section. A phrase list cannot establish authorship or remove every statistical feature left by a model. A local rewriter can replace one model's patterns with another's. Scientific editing must first preserve the claim, its evidence and its uncertainty.

The work adds:

- [Source audit](source-audit.md): all 41 reference positions in the inspected Wikipedia source, including duplicates, journalism and unresolved records.
- [Evidence map](evidence-map.md): foundational work, newer studies, verified citation edges and current editorial practices.
- [Historical exemplars and venue profiles](venue-profiles.md): Nature, MDPI Applied Sciences, Results in Engineering, CAADRIA/CumInCAD, clinical writing and related fields.
- [Evaluation and paper ideas](evaluation.md): a reproducible study design and six candidate research papers.
- [ScientistTwo assessment](scientist-two.md): automated-review results, audit denominators and the robotics example.
- [Small models for proofreading and translation](small-models.md): English and Arabic model choice, prompting, quantisation, stylometry and translationese, watermarking and detection.
- [Tamil](tamil.md): models, proofreading evidence, register and script, quality estimation.
- [Verification](verification.md): an independent check of the claims behind the recommendations.
- [Small-model runner](../local/README.md): the runner that applies these findings.
- [Local-model integration](../integrations/local-model/README.md): a patch adding conservative academic checks to `hz`, with tests and an audit trail.

## Main findings

1. The original repository's primary source is Wikipedia's descriptive advice, rather than a peer-reviewed validation of its 26 rules. The rule order should be treated as editorial judgment. See the [source audit](source-audit.md).
2. Historical scientific articles contain words and constructions on AI phrase lists. For example, a 2021 Applied Sciences BIM/robotics paper uses “delve.” That alone cannot identify model authorship. See [the exemplar](venue-profiles.md#historical-pilot).
3. November 2022 is a useful sampling boundary for widespread ChatGPT use, not the invention of AI writing. GPT-3 existed in 2020. Even an older article's currently served text may include later corrections. Use “pre-ChatGPT publication,” not “proven human text.”
4. Evidence for changing lexical distributions is stronger than evidence that any one phrase proves AI use. Research on genre variation, author expertise and detector bias argues against universal bans. Sources and limits are in [the evidence map](evidence-map.md).
5. Scientific hedges, passive methods descriptions, technical compounds, repeated measurement names and structured abstracts often serve a purpose. Preserve them when removing them would change meaning or break the venue's format.

## Scope and reproducibility

The search began from `libishm1/humanizer` at `0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0`, its upstream source and bibliography. It expanded through original publisher pages, arXiv, ACL Anthology, proceedings archives and author/institutional repositories. Search families covered AI lexical/style shifts, register, detection bias, academic stance, scientific writing, reporting guidelines, and pre-2022 robotic fabrication, concrete and clinical exemplars.

Backward tracking means inspecting reference lists of selected seeds. Forward tracking means locating later papers and checking whether their bibliography actually cites a seed. A later paper on the same topic is labelled a thematic follow-up unless a citation edge was inspected. Preprint and journal versions are one study, not independent replications.

This pass did not export complete citing-paper lists from Scopus, Web of Science or OpenAlex, run every citation chain to saturation, acquire every full text, or measure a balanced corpus. The historical examples are a qualitative pilot. A paper's existence, its claims, and independent reproduction of its claims are three different verification levels. The tables state the access level rather than implying all papers were read in full.

To extend this into a formal review: preregister databases, complete search strings, dates and exclusions; export records; deduplicate by DOI and version family; screen with recorded reasons; retrieve eligible full texts; iterate backward/forward searches until a stated stopping rule; publish the screening log and coverage counts. Do not label the present pass exhaustive.

## Product boundary

The academic skill can use venue context when editing. The local model integration is more limited: it preserves the model's exact trained prompt and sampling, then checks candidates. Its profile names label the review context; they do not make the model trained on Nature, CAADRIA or clinical prose. No weights have been trained and no detector-bypass result is claimed.

The ScientistTwo-inspired research loop remains an evaluation design. The patch implements text-change alarms and traceability, not experiment execution, citation retrieval, code audits or independent scientific peer review.
