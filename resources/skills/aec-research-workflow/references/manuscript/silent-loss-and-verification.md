# Silent loss, and verification that actually catches it

The defect class that cost most in Project B (urban). Distinct from rendition drift: here the content
is lost or wrong **inside a single artefact**, and every check passes.

---

## 1. The four silent-loss pathways

### Layout that discards content
A markdown-to-LaTeX converter gated `\resizebox` on **column count**:

```python
if ncol >= 5:                       # width-blind
    tab = r"\resizebox{\textwidth}{!}{%" + tab + "}"
colspec = "l" * ncol                # non-wrapping
```

A four-column table containing one long cell therefore got a plain `llll` spec, ran **far past the
text block and off the physical paper edge**, and silently dropped **two thirds of its data cells**,
including two entire columns of the paper's defining table. `pdflatex` exited 0.

Fix: gate on **content width**, wrap, and shrink only if still too wide.

```python
widest = max((len(c) for r in rows for c in r), default=0)
if ncol >= 5 or widest > 40:
    colspec = (">{\\raggedright\\arraybackslash}p{0.20\\textwidth}"
               + ">{\\raggedright\\arraybackslash}X" * (ncol - 1))
    tab = (r"\begin{tabularx}{\textwidth}{" + colspec + "}" + ... +
           r"\end{tabularx}")
    tab = (r"\resizebox{\ifdim\width>\textwidth\textwidth\else\width\fi}{!}{%"
           + tab + "}")
```

**Guard:** `grep -c "Overfull \\\\hbox" main.log` must be **0**. Never accept "a few overfull boxes
are normal"; one of them is eating your data.

### A filter that can silently match nothing
The citation resolver only reached its lookup after a regex requiring a **4-digit year**:

```python
NARR = re.compile(r"\b([A-Z][\w'-]+(?: et al\.)?)\s*\((\d{4}[ab]?)\)")
```

`Author et al.`, written without a year, matched nothing, so it was never numbered **and never
appended to `unresolved`**. The script printed `UNRESOLVED: none`. It was the only citation
supporting the paper's entire Verification stage.

**Rule:** any code path that can decline to match must count its non-matches. A checker that can only
report problems it has already parsed is not a checker.

```python
# add the negative check
bare = re.findall(r"\b([A-Z][\w'-]+ et al\.)(?!\s*\()", body)
if bare:
    print("CITATIONS WITHOUT A YEAR (invisible to the resolver):", set(bare))
```

### A stale lookup table
`md2tex.py` held a hardcoded `FIGS` dict mapping figure number → filename. After a renumber it was
not regenerated, so most captions carried **the wrong artwork** in both PDF and DOCX. The document
was structurally perfect.

**Guard:** hash the source figure and the packaged/embedded copy and assert equality per number.

```python
for n, stem in FIGMAP.items():
    assert md5(f"figures/{stem}.png") == md5(f"package/Fig{n}.png"), n
```

Related: a hardcoded `for n in range(1, 13)` silently dropped every figure after the twelfth from
every PDF. Derive ranges **from the data**; never write a literal bound.

### Content moved out and never landed
Restructuring moved tables and figures from the supplement into the main text. The result:
- two supplementary sections became empty stubs,
- section numbering gained a gap (S1, S2, [gap], S4…),
- many main-text pointers still aimed at supplementary floats that had moved,
- several figures ended up **referenced in neither document** while their artwork sat on disk.

**Guard after any move or renumber:**

```python
# every pointer target must exist AND hold what the sentence claims
for m in re.finditer(r"(Table|Fig\.)\s*(S?\d+)", body):
    assert target_exists(m.group(0)), m.group(0)
# section numbering must be contiguous
assert sections == [f"S{i}" for i in range(1, len(sections) + 1)]
# every figure on disk is referenced somewhere, and vice versa
assert set(referenced) == set(on_disk_used)
```

---

## 2. Verification that works: recompute from raw data

Cross-checking prose against the table that reports it only confirms that a wrong number appears
consistently in both. The only verification that caught real errors in Project B recomputed each
claim from the simulation outputs.

What it found, none of which crashed anything:

| Claim as written | Recomputed | Consequence |
|---|---|---|
| "a difference of at most X %" in sensible capacity | matched on the solid branch, but more than twice as large, with the opposite sign, on the liquid branch | The stated justification that the control was clean was understated by more than 2× |
| control cooling falls within a stated band | one of the recomputed values lay above the band | Upper bound outside the stated band |
| latent grows by a stated amount to two decimals | the recomputed value rounds one unit lower in the second decimal | Stated precision was wrong |
| "a **constant**" contribution from resistance | roughly halved across the sweep | "Constant" is wrong |
| a table row's state range | computed on **N − 1** nodes inside a table whose own footnote said **N** | Internally contradictory |

**Protocol:**
1. Re-derive the number from the primary output file, not from any intermediate.
2. Compare to the manuscript at full precision, then at stated precision.
3. If they differ, decide which is right *before* editing; sometimes the manuscript is correct and
   the "correction" is the error (this happened, on the node-basis question).
4. Record the recomputation so the next round does not repeat it.

---

## 3. Derived metrics: where wrong numbers hide

Several of Project B's reported metrics were wrong by *definition*, not by arithmetic.

**The clamp.** `recharge_efficiency = min(1.0, discharge / charge)` reported exactly `1.00` for
several cases. Uncapped, those cases were well above 1: net discharge, the opposite of what
"efficiency 1.0" implies. *A metric sitting exactly on a round bound is a bug signal.*

**The sample size.** "A recharge efficiency of zero" rested on **a single day**. Check n before a
number becomes a finding.

**The competing definition.** Decrement factor computed as a whole-period swing ratio gave a
noticeably different range from the standard per-diurnal-cycle definition in the established
literature, for the same cases. The first is not the classical quantity and is **not comparable with
published values**. The direction of the effect survived; the numbers did not.

**Derived when the tool computes it directly.** Melt–freeze cycle counts derived from a layer-mean
liquid fraction produced **both** false negatives (zero cycles reported where nodes were in fact
alternating) and false positives (cycles reported where there was no phase activity). The solver
exposes its own discrete phase state in a separate code path; counting from that fixed it *and* made
the cross-check meaningful, because the two derivations are genuinely independent.

**The inferred member set.** The PCM layer spans a fixed set of N nodes. Inferring the set from
"which nodes vary" drops a node that is constant across the window, giving an N − 1 basis. The first
"correction" went the wrong way. Derive membership **from geometry** and state it in the caption.

**The unstated aggregation basis.** All-hours vs occupied-hours comfort **flipped the sign** in a
substantial share of scenarios. State the basis wherever the metric appears.

### The checklist for any derived quantity

```
definition   which of the competing definitions, and why
n            how many samples stand behind it
basis        what it is aggregated over (hours, nodes, cases, season)
independent  what estimator it was checked against, and the agreement
clamps       none, or justified and reported uncapped alongside
```

Project B put exactly this in a supplementary section. A supervisor had asked for verification to be
distinguished from validation; publishing the estimator comparison turned a weakness into one of the
paper's strongest sections.

---

## 4. Generalised rules

1. "No errors reported" is **not** "no errors". Ask what each check *cannot* see.
2. Every **silent pathway** is a defect waiting to happen: a clamp, a hardcoded bound, a filter that
   can match nothing, a width-blind layout rule, a lookup table maintained by hand.
3. **Render and inspect.** Page count, overfull boxes, and whether the tables contain their data.
4. **Recompute**, don't cross-check.
5. A metric's **definition** is part of the result. Publish it.
6. After any structural move, re-verify **semantics, not just existence**. A pointer that resolves to
   the wrong content is worse than a broken one, because nothing flags it.
