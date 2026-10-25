# Figure and diagram QA

Figures carry defect classes that no text check sees, and they are read more carefully than prose.
Everything below was a real defect found in one paper's figures plus its graphical abstract.

---

## Read every figure at reproduction size

A 9.5 pt label on an 18-inch canvas becomes ~3.5 pt when the figure is fitted to a column. Render at
the size it will print and look at it. Most "illegible figure" comments come from never doing this.

---

## Effective DPI is a compliance test, and metadata lies

Publishers require ≥ 300 dpi for combination art. **Judge by pixel width ÷ print width in inches**
(190 mm double column = 7.48 in), never by the DPI tag in the file. Project B had figures tagged at a
low DPI that were compliant and figures tagged higher that were not; about a third of its figures
were effectively below 300 dpi while looking perfectly sharp on screen.

```python
effective_dpi = Image.open(f).size[0] / 7.48
```

Matplotlib figures **re-render losslessly** at higher resolution, because figsize is specified in
inches: forcing `rcParams["savefig.dpi"] = 300` and re-running the generator produces the identical
figure with more pixels. Layout, fonts and content are untouched. **Never** upscale a raster.

Two traps when doing this:
- some figures come from a *different* generator than the rest and get missed
- a generator that writes to the repo root while the document reads from `figures/` leaves a stale
  low-resolution copy that ships

---

## Verify caption-to-artwork pairing after any renumbering

A hand-maintained figure-number → filename map went stale after a renumber and put the **wrong
artwork under most of the captions**, in both PDF and DOCX. Nothing failed. Hash the source against
the packaged or embedded copy, per number, every build.

---

## A figure can outlive its own content

A literature co-topic network rendered the full assembled corpus. After the review was trimmed, its
most prominent node was a source the paper no longer cited anywhere, and a large share of the labelled
nodes were uncited. The figure was not wrong when drawn; the paper moved. Re-check every figure's
content **against the current manuscript** after any substantial cut, and prefer regenerating
corpus-derived figures from the final citation set.

---

## Orphaned artwork

Restructuring left several figures referenced in **neither** the manuscript nor the supplement, with
their files still sitting on disk. Assert both directions:

```python
assert set(referenced_in_documents) == set(figures_shipped)
```

---

## Label collisions need geometry, not smaller fonts

**The wrong fix**, and why it fails: separating *nodes* by a fixed elliptical clearance as a proxy for
label size. Labels sit at a fixed offset from their node and vary in width from a short four-letter
citation key to an eighteen-character one, so well-separated nodes still collide. Many labels were
illegible.

**The right fix**: relax the *rendered label boxes*.

1. Draw everything, then `fig.canvas.draw()` and measure each label's actual bounding box.
2. A label's box only **translates** when its offset changes, so measure width/height once and do the
   whole relaxation arithmetically, redrawing only at the end. (Redrawing per iteration at 300 dpi is
   unusably slow.)
3. Use **Jacobi** updates: accumulate all pushes for a sweep and apply together. Sequential
   (Gauss–Seidel) updates oscillate and never converge.
4. Separate along the axis of **least penetration**, so wide labels move vertically and stacked labels
   move sideways.
5. Treat node markers as obstacles, **including a label's own marker**. A high-degree node's dot is
   larger than the default label offset. (Skipping the self-marker left labels sitting on their own dots.)
6. Let a boxed-in label **escape sideways**, not only vertically, or it deadlocks.
7. Tether labels to their node with a maximum offset, and draw a **leader line** when a label moves far.
8. Seed a handful of crowded labels in **distinct directions**; symmetric starts deadlock. If needed,
   search a few seeds and pick one that converges.
9. Report residual overlaps **as a number** so the fix is verifiable: `0 true label-label overlaps`.
   Distinguish true overlap from padding: a residual smaller than your pad is not a collision.

If it still will not converge, you are out of space: enlarge the canvas, spread the layout, or reduce
the font. Reducing the font is legitimate: an unreadable 10.5 pt label is worse than a clean 9.5 pt one.

---

## Legends must not sit on data

A legend placed "lower left" sat on a curve that descends to zero at lower left. Nudging inside the
axes just moves the problem. Put it **outside** (`bbox_to_anchor` below the axes, `ncol=3`).

---

## "To scale" is a claim, and gets checked

A section captioned *to-scale* was drawn with a window noticeably shorter than the simulated one,
while two other figures stated the window dimensions correctly. If a caption says "to scale",
"dimensioned", or "1:1", every dimension must come from, or be checked against, the model.

Watch for **knock-on effects**: raising the window height pushed an annotation into a dimension label.
Re-read the figure after every geometric change.

---

## A figure must not contradict the paper

The worst figure defect found was not visual. A graphical abstract's design rule recommended
"exhaust-air night venting", the sink the paper's own section proves unavailable. It had been
generated several revisions earlier and never regenerated.

Figures need the same **regression guards** as prose. Assert, in the generator source:
- superseded recommendations appear nowhere
- current framing appears
- claimed counts match their real source (run the thing and read its number)

---

## Make every number on a figure live

Half-live figures are a trap: bar **widths** read from JSON while bar **captions** were literal
strings. A data change would have moved the bars and left the captions asserting old values.

Proof this is safe: after converting the literals to live reads, the regenerated PNG was
**byte-identical**. The literals were correct, and now they cannot silently stop being correct.

---

## Filenames are an interface

A regenerated bar chart silently overwrote a hand-built time series because both were
`fig_nightvent_a.png`. Name deliberately, `(a)`, `(b)`, `(c)`, and check what a generator writes
before running it.

---

## Verify automated figure reviews before acting

An agent review of the paper's figures returned five findings:

| Finding | Verdict |
|---|---|
| Label collisions | **Real**, fixed |
| Legend over data | **Real**, fixed |
| Dimension inconsistency | **Real**, fixed |
| "Control logic contradicts the figure" | **Real, but misdiagnosed**: the code was correct; an undocumented threshold made the figure the only evidence available. Fixed the *documentation* |
| "Suspicious duplicate values" | **Correct physics**: two PCMs already fully re-solidify overnight, so an extra night sink cannot help. Explained in the text rather than "fixed" |

It also cited node names that **did not exist** in the reference list: misreadings *caused by* the
overlap it was reporting. The finding can be real while the specifics are wrong. Check each against
the source before changing anything, and be willing to conclude "correct, but needs explaining".

---

## Figure-only pages

Detect them: a page with very few words and one or more images.

```python
words = len(page.get_text().split()); imgs = len(page.get_images())
figure_only = words < 60 and imgs > 0
```

A *single* full-page figure is fine for a portrait-aspect diagram. A **run** of consecutive figure-only
pages is the defect: interleave text, relax float parameters, or use `[!htbp]`.

---

## Checklist

```
[ ] read at reproduction size
[ ] no text overlapping text; residual overlap reported as a number
[ ] no legend over data
[ ] every dimension traceable to the model, if "to scale" is claimed
[ ] every number live from data, captions included
[ ] no recommendation the paper contradicts
[ ] axis labels, units and a self-contained caption
[ ] 300 dpi, colour-blind-safe palette, greyscale-legible
[ ] filenames unique across all generators
[ ] no runs of figure-only pages in the compiled PDF
```
