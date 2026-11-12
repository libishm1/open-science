# Local-model academic integration

This patch targets [sgaofen/humanizer-local-model](https://github.com/sgaofen/humanizer-local-model) at commit `7dd4be90cb3acb2e5d18aeea5837f888d2bb2d52`. It is not an upstream release. No write permission to that repository was available, so the integration is delivered as a patch.

The local-model project is a separate Apache-2.0 fine-tuned rewriter, not a GitHub fork of the Markdown skill. Its README compares against `blader/humanizer`, the upstream of `libishm1/humanizer`. The comparison is project-reported evidence, not an independent benchmark. Combining their names or workflows does not establish shared training or guarantee removal of model-specific patterns.

## Apply on a computer

Clone a fresh checkout, then create a work branch at the tested base:

```bash
git clone https://github.com/sgaofen/humanizer-local-model.git
cd humanizer-local-model
git switch -c academic-review 7dd4be90cb3acb2e5d18aeea5837f888d2bb2d52
git apply --check /absolute/path/to/humanizer/integrations/local-model/academic.patch
git apply /absolute/path/to/humanizer/integrations/local-model/academic.patch
python3 -m unittest discover -s tests -v
python3 -m pip install -e .
```

Use an absolute path to the actual patch on your computer. The patch contains changes to `humanizer/hz.py`, the new `humanizer/academic.py`, regression tests, `docs/ACADEMIC.md`, and a README link. The upstream Apache-2.0 license and notices continue to apply to its code; preserve them in any fork or redistribution.

With a Humanizer model server already running:

```bash
hz paper.md --academic results-in-engineering --json --quiet -o paper.review.md > paper.audit.json
hz paper.md --academic caadria --protect-file terms.txt --json -o paper.review.md > paper.audit.json
```

The trained prompt and sampling remain byte-for-byte unchanged. Profile flags record the target context but do not inject venue instructions. Checks cover selected numerical quantities, citation forms, math/code spans, English claim cues and explicitly protected terms. Copying is allowed in academic mode. All rejected main-attempt candidates are recorded; when none pass, the original piece is retained. Exit 4 means this happened; the output and audit are still written.

Read `docs/ACADEMIC.md` after applying for coverage limits and review instructions. These checks do not establish semantic equivalence. In particular, values can remain present while being attached to the wrong claim. No model weights were downloaded, no model was fine-tuned, and no live inference or detector benchmark was run.

## Validation recorded for this handoff

- Seven new academic regression tests pass, including fake-server integration tests.
- Full local-model suite: 71 tests discovered, 61 passed, 10 skipped because optional Gradio support was unavailable.
- The tests verify prompt/sampling compatibility, changed percentages and units, hedging/negation/causality alarms, citations, inline math, protected terms, retry selection, original fallback and JSON reporting.
- Humanizer skill package validator passes at version 3.2.0.
- `npx --yes skills add . --list` passed and discovered the portable skill.
- The local-model patch passes `git apply --check` against a fresh checkout of its pinned base.

The next empirical task is to run real-model rewriting on a licensed, held-out, section-balanced sample and assess both editing benefit and scientific errors. Count fallback separately; unchanged originals must not masquerade as successful edits.
