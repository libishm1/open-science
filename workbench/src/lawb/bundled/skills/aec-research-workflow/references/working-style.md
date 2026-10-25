# Working style: how this researcher works with agents

These rules come from hundreds of corrections across many research sessions. Apply them by default.

## Ask before acting

- When the request is a question, **answer in chat first** and do not edit files. Typical prompts: "answer in chat first", "dont change just answer me", "give all of this in chat so we can decide together".
- When a supervisor or co-author is involved, propose the change and let the researcher check with them before editing ("lets communicate with the supervisor before editing").
- Do not make non-essential edits. If nothing is critical, say so and leave the text alone.

## Expect short, dictated prompts

Prompts are often voice-dictated and fast, with typos and phonetic spellings of place names, codes and file types (for example "MPW" for EPW). Infer the intent from context and confirm only when the reading changes the outcome. Further instructions often arrive while a run is in progress; fold them in.

Pasted WhatsApp threads and emails from the supervisor or PI are usually **the real instructions**. Treat the supervisor's latest written decision as governing.

## Verify everything

- DOIs: check with Crossref and at least one independent API (see [literature-review.md](literature-review.md)).
- Numbers: recompute from raw result files, never from the table that reports them.
- Arithmetic and derivations: check formally (Lean 4 or sympy) when they carry a claim.
- Agent findings: verify the most damaging claim yourself before relaying it. Reviewer agents are sometimes right and sometimes provably wrong about the same table.
- Lab or institutional facts: state only what the researcher has confirmed. Mark anything only the PI can confirm.

## Version everything

- Every deliverable gets a distinct new version: `_v<N>_<YYYY-MM-DD>_<HHMM>` or `rev<NN>_<slug>_<date>`.
- Back up before any destructive edit (`<file>.BEFORE-<ACTION>-<YYYYMMDD-HHMMSS>.<ext>`), and archive old versions to `_previous_versions/` or `_versions/`.
- Keep earlier images and figures where they are still relevant.
- Shared documents on OneDrive or SharePoint are live and others edit them. Edit a **copy**, keep the comment threads visible, and write in place rather than moving files over a shared link.

## Throttle agents

The most repeated correction: **keep two agents in flight by default, three at most**, and about four for a review panel. Token budgets run out otherwise. Use batch-prefixed scratch filenames so parallel agents never collide.

## Report status honestly

- When asked "is it done yet", report what has finished, what is running and what failed.
- Give time estimates calibrated to real pace (often 1.5 to 2 times an optimistic estimate).
- Before a usage limit or at a stopping point, write a handoff and save memory ("write a handoff and persist into memory").

## Hand back shareable artefacts

Almost every task ends in something the researcher can forward: a zip, a Word or PDF file, a short message, an email draft or a handoff document. Always:

- give **absolute paths** and say which file is the current one;
- say which zip to attach and from where;
- keep code, data and figures separate from document-generation scripts in anything sent to reviewers.

See [communication.md](communication.md) for message conventions.

## Handoffs

Keep a living `HANDOFF.md` (current state, invariants, gotchas, checks, next actions, decision log) in each active project, written so that any agent (Claude, Codex, Gemini) can continue the work. Update it after every major change.

## Scratch files

Session scratchpads are temporary. Copy every code file into the project's `Code/` folder and **apply fixes to the canonical file, never to a scratchpad copy**. A fix made to a copy leaves the shipped document right and the project's builder regenerating an older version.
