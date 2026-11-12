# ScientistTwo: useful design, bounded evidence

Sources: [Nam et al., arXiv:2609.19644v1](https://arxiv.org/html/2609.19644v1), submitted 17 September 2026; [project site](https://scientist-two.github.io/); [KinemaAnchor-Manifold manuscript](https://scientist-two.github.io/generated-papers/applications/Robotics_KinemaAnchor-Manifold.pdf). Checked 9 November 2026.

## What the reported numbers mean

The project describes a research cycle with idea generation, subset/full experiments, ablations, manuscript drafting and simulated review/rebuttal. The reported 91.9% ScholarPeer and 72.1% Stanford Agentic Reviewer acceptance rates are automated threshold outcomes over 86 generated manuscripts. They are not acceptance decisions by NeurIPS, ICLR or ICML program committees.

The integrity table uses a different denominator: the full-system row reports 49/49 score and method–code checks, 0/49 specification violations, and 0/1,814 hallucinated references. Do not attribute these audit counts to all 86 generated papers or all 107 benchmark tasks. The paper explains that a rule-violating solution is removed between the 50- and 49-task variants. These are authors' reported audits; this integration did not rerun the research repositories.

## What to adopt

1. Keep an explicit ledger linking each manuscript claim to a result, code/configuration version and source.
2. Reproduce the baseline before comparing a proposed improvement.
3. Use screening subsets for development and a frozen evaluation set for final assessment. Evaluate more than the single metric used for selection.
4. Use ablations to test each component's contribution. An ablation does not by itself prove a general causal mechanism.
5. Route a methodological criticism back to experiments when evidence is missing. Editing stronger prose cannot supply missing evidence.
6. Run a separate integrity review after the writing pass. Add claim-support checks to citation-existence checks.
7. Limit review rounds and preserve rejected candidates. A system repeatedly optimizing an automated judge can overfit that judge.

## Robotics example

The released KinemaAnchor-Manifold PDF concerns articulation-aware scene feasibility: moving-part relationships, swept-volume constraints, pose optimization and physics settling. Its abstract reports improved retention of nested objects and reduced articulation obstructions. These are generated-manuscript claims requiring artifact checks, not independently reproduced results here.

The PDF carries an “under review” ICLR 2025 template while citing 2026 work. Treat this as a metadata/template discrepancy to investigate, not evidence of acceptance or misconduct. Before reusing any result, reconcile the manuscript version, benchmark provenance, simulator settings, metric definitions and executable artifacts.

For the user's architecture/robotics work, a plausible extension would connect design intent and fabrication constraints to an evidence ledger. It should distinguish collision-free simulation, executable robot motion and successful physical fabrication as separate claims with separate validation.

## Integration boundary

The present `hz` patch records source/candidate text, hashes, sampling settings and change alarms. It checks selected surface invariants and retains the original when candidates fail. It does **not** implement ScientistTwo's research agents, independently verify citations, reproduce experiments, or certify publication readiness. Those capabilities require a later research-orchestration implementation and empirical validation.

Keep these stages separate: experiment evidence → manuscript claims → venue editing → integrity checks → human review. A style score or detector result must not substitute for any of them.
