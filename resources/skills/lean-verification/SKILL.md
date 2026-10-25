---
name: lean-verification
description: Procedure for formal verification with Lean 4 and Mathlib, and for checking that shipping code matches the proofs. Covers the honesty contract (proved, cited axiom, or documented prose, never sorry), CI gates for build, sorry count and axiom list, an adversarial audit, common Mathlib pitfalls, and turning each proven invariant into a property-based test (CsCheck for C#, Hypothesis for Python), with Dafny as the escalation for the single riskiest kernel. Use when formalising an algorithm, auditing a Lean library, or checking code against its proofs.
compatibility: Claude, Codex, local models, Herdr and Omarchy. Lean 4 with elan runs on Windows, macOS and Linux. Property tests need the language's test runner.
license: see repository LICENSE
---

# Lean verification and proof-to-code checks

Procedure only. It contains no proofs or results from any project.

## Quick start (for small local models)

1. State the theorem in one sentence before writing Lean.
2. Search Mathlib for an existing lemma first. Do not reprove what exists.
3. Write the statement. Build it. Then fill the proof in small steps, building after each.
4. Never leave `sorry`. If a step is out of reach, mark it as a cited axiom or as prose, and record why.
5. Run the CI gates: build, sorry count, axiom list.
6. For each proven invariant, write one property-based test against the real code.

## The honesty contract

Every named result in a library is exactly one of these:

| Status | Meaning | Allowed in main |
|---|---|---|
| Proved | Lean checks the full proof | Yes |
| Cited axiom | Stated as `axiom` with a citation to the published source and a reason Mathlib cannot prove it yet | Yes, listed in the axiom gate |
| Documented prose | Explained in comments where Mathlib lacks the machinery; no Lean statement claims it | Yes |
| `sorry` | Unfinished | No |

Write the status next to each result in the progress log. A reader must be able to tell which
results Lean actually checks.

## CI gates

Run on every push:

1. `lake build` succeeds with no errors.
2. Real-sorry count is zero. Search the sources for `sorry`, excluding comments and strings.
3. The axiom list matches the approved list. Print `#print axioms` for each top-level theorem and
   compare. A new axiom fails the build until it is reviewed.
4. Check that the CI file itself is valid. A workflow that never runs passes nothing.

## Adversarial audit

Before calling a library finished, audit it in slices, with a reviewer who did not write the proofs:

1. For each axiom, look for a counterexample to its statement as written. A missing hypothesis can
   make an axiom false.
2. For each theorem with a convexity, finiteness, or non-emptiness hypothesis, check that the
   hypothesis does not make the result vacuous.
3. Check that each docstring matches the statement it describes.
4. Record each finding with its fix and the commit that fixed it.

## From proofs to code

A proof shows that an algorithm has a property. It does not show that the shipping code is that
algorithm. Close the gap with property-based tests:

1. List the invariants the theorems establish (for example: no overlap, monotone objective, output
   convex, topological order preserved).
2. Write one property test per invariant that calls the real code on generated inputs.
3. Triage each failure: a code bug, a specification gap, or a test generator that produces invalid input.
4. Pick the single riskiest kernel and prove it in Dafny if the property tests cannot cover it.

Details and examples: `references/property-tests.md`.

## Files

- `references/mathlib-pitfalls.md` - common Lean and Mathlib traps and their fixes.
- `references/property-tests.md` - property-test patterns for C# and Python, and the Dafny escalation.
- `references/platform-compatibility.md` - where each step runs.

## Do not

- Use Microsoft Code Contracts or Spec#. Both are discontinued.
- Claim a result is verified when only its statement compiles.
- Hide an axiom inside a definition. Every assumption must appear in the axiom gate.
