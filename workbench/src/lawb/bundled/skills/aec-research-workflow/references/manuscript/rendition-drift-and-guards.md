# Rendition drift, and the guards that catch it

The defect class that cost the most time on this project, produced zero error messages, and would
have reached a journal editor.

---

## The problem

A finding gets stated in more than one artefact. Each is built by different code. Only the *numbers*
are shared; the *sentences* are duplicated. Change one, and nothing tells you the others are stale.

Observed renditions and how each drifted:

| Rendition | How it drifted | How it was caught |
|---|---|---|
| DOCX | Ran several revisions **ahead** of the LaTeX | Comparing marker strings between builders |
| LaTeX submission | Carried a **superseded**, larger coupling-error range instead of the measured per-case one, and said "validated" where no experiment existed | Same comparison |
| LaTeX submission | **Missing two whole tables** the DOCX had, one of them a reviewer's explicit request | Comparing table header sets |
| Graphical abstract | Several revisions stale; recommended a night sink the paper **proves unavailable** | Being asked "is it up to date?" |
| Graphical abstract | Bar *widths* live from JSON, bar *captions* hard-coded | Auditing every number against its source |
| Abstract | Grew past the publisher word limit when a revision added a sentence | Compliance audit |
| Canonical builders | Fix scripts edited **scratchpad copies**; the project's own builder would regenerate an older paper | Noticing prose in the source that was absent from the output |

None of these produced an error. Every stale artefact compiled cleanly and passed structural checks.

---

## Root causes, in order of danger

1. **Duplicated prose across builders.** The deepest cause. Numbers were centralised; sentences weren't.
2. **Editing a copy instead of the canonical file.** Output correct, source stale: invisible to tests.
3. **Half-live artefacts.** Part of a figure reads from data, part is a literal. The literal lies later.
4. **Auto-numbering in one rendition, manual in another.** `\ref` is always right, so the bug lives
   entirely in the hand-numbered rendition and only appears on comparison.
5. **An incomplete mental list of deliverables.** "Regenerate the figures" ran three scripts; a fourth
   existed.

---

## Guard architecture

Four checks, each catching a different class. All are cheap and run in seconds.

### 1. Reviewer regression: `verify_all_comments.py`
One assertion per past comment, testing a marker that can only survive if the fix is intact.

```python
SUPERVISOR_ROUND_1 = [
 ("no first person", lambda: not re.search(r"\b[Ww]e\b|\bour\b", body)),
 ("verdict tables removed", lambda: "SUBSTANTIATED" not in allt),
 ("tables introduced before they appear",
  lambda: "Table 1 lists" in allt or "lists the parameters held constant" in allt),
]
```

**Design note:** give each check an `or` fallback on a phrase that survives renumbering, or your own
later edits will trip it. The example above survived a full table renumber because of the second clause.

### 2. Structure: `check_latex.py`
Environment balance, brace balance, citation and label resolution, figure-file existence, **tabular
row/column consistency**, and escaping artefacts. Must exit non-zero.

```python
def brace_group(s, i):
    """Read the balanced {...} at s[i]. A column spec contains p{2cm}, so a
       non-greedy [^}]* stops inside the first p{...} and mis-parses the spec."""
    d = 0
    for j in range(i, len(s)):
        if s[j] == "{": d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0: return s[i+1:j], j+1
```

### 3. Parity: `check_docx_latex_parity.py`
The important one. Three layers:

```python
# (a) substantive claims, normalised so LaTeX markup does not defeat matching
def norm(t):
    t = t.replace("{,}", ",")                        # 12{,}345 -> 12,345
    t = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", t)  # strip one markup level
    t = re.sub(r"\\[a-zA-Z]+|[{}$~\\]", " ", t)
    return re.sub(r"\s+", " ", t).lower()

ITEMS = [("coupling error is the measured per-case value", CURRENT_RANGE, CURRENT_RANGE), ...]

# (b) NEGATIVE assertions - superseded content must appear in NEITHER
NEGATIVE = {"superseded coupling range": SUPERSEDED_RANGE}

# (c) table SETS, by a distinctive header cell
TABLES = [("PCM glazing assembly", "Assembly U-value", "Assembly U-value"), ...]
```

Layer (c) exists because layers (a) and (b) passed while two entire tables were missing.

### 4. Figure claims: `check_graphical_abstract.py`
Every number rendered on a figure, checked against its source JSON; plus assertions that its numbers
are **live reads, not literals**; plus prose claims that must track their sources.

```python
chk("bar captions derive from JSON", 'f"{LAT_CODE:.0f} kWh/yr' in src)
chk("does not recommend the unavailable sink", "exhaust-air night venting" not in src)
```

For a claim that cannot be counted statically (a figure citing "N-check harness" where several checks
sit inside loops), run the harness and **read its own reported total**.

---

## Rules

1. **Every claim in every rendition.** When you add a claim to one rendition, add it to the others
   and add a parity line.
2. **Canonical file first.** Patch it, then verify the artefact and its source agree.
3. **Negative assertions for superseded content.** "The superseded range must appear nowhere"
   is stronger than "the current range must appear somewhere".
4. **Live numbers.** If a caption states a value, interpolate it. Proof that this is safe:
   after converting the literals to live reads, the regenerated PNG was **byte-identical**. The
   literals were right, and now they cannot silently stop being right.
5. **An explicit list of deliverables.** Manuscript, submission source, each figure script, graphical
   abstract, abstract, highlights, supplementary, README. Anything that states a finding is a rendition.
6. **A guard for every fixed defect.** The log of guards is the real asset.

---

## Patch-script discipline

```python
# atomic: build the whole string, write once at the end
s = open(P, encoding="utf-8").read()
def sub(old, new, tag):
    global s
    assert old in s, "anchor missing: " + tag   # loud, not silent
    s = s.replace(old, new, 1)
open(P, "w", encoding="utf-8").write(s)
```

- Assert **every anchor**. A silent no-op is worse than a crash.
- Write patches as **`.py` files with raw strings**, never shell heredocs, which mangle backslashes.
- **Atomic write** means a failed assert leaves the file untouched; you can fix and re-run.
- Make patches **idempotent** where possible (`if new in s: skip`) so a partial run can be resumed.
