# Debugging a diagram, and making it readable

A figure that renders is not a figure that works. Compilation proves the code
ran; it proves nothing about whether a reader can follow the picture. This is
the checklist for finding what is wrong, and the conventions that stop it being
wrong in the first place.

## The debugging loop

1. **Render it and look at it.** Every time. Most real defects are invisible to
   any automated check because they are text sitting on graphics, or a line
   whose meaning is ambiguous.
2. **Run the collision guard.** `check_overlaps.py module:build`. It exits
   non-zero, so it can gate a build.
3. **Read every label aloud in reading order.** If you cannot say what the
   figure claims in one sentence, the layout is wrong, not the wording.
4. **Shrink it to the final printed width and look again.** A figure designed at
   180 mm and printed at 85 mm loses every 4 pt label.
5. **Turn it greyscale.** If two categories become the same grey, colour is
   carrying information that nothing else carries.
6. **Fix the cause, then add a guard** so the defect cannot come back silently.

## Failure signatures and what causes them

| What you see | Cause | Fix |
|---|---|---|
| Labels overlapping near one corner | Several zones anchored at the same coordinate | Give each zone its own band; measure, do not nudge |
| Text running off a card or panel | String longer than the box, no wrap | `textwrap.wrap` at a measured character count, or shorten the content |
| A line drawn through its own label | Connector and label share an angle or a row | Move the label off the line, or drop the line and let adjacency carry the meaning |
| Triangular fans in a ribbon | Turn tighter than the ribbon is wide | Clamp half-width to the local radius of curvature |
| Connector spaghetti | Source order does not match destination order | Order lanes by destination; crossings usually fall to zero |
| Washed-out colours after export | Palette quantisation chose badly | Export full colour; if size forces quantisation, use octree, not median cut, and check the deviation |
| Banded halos | 256-colour palette cannot hold a smooth gradient | Keep gradients in full colour, or remove the halo from that export |
| Label reads bottom-up | Tangential text on the lower half of a circle | Flip rotation by hemisphere, or use horizontal labels |
| Figure looks cluttered but nothing is wrong | Too many elements competing at one weight | Remove a layer. Redundant connectors are the usual candidate |

## What guards can and cannot catch

`check_overlaps.py` measures every text artist, rotates its box about its own
anchor, and clips the quadrilaterals against each other for a true overlap area.

It catches: text on text, text off the canvas.

It does not catch: text on graphics, a connector crossing a panel, an arrowhead
landing in the wrong place, a label attached to the wrong object, a colour
collision, or a claim that is simply wrong. Those need eyes.

**Do not use axis-aligned bounding boxes for rotated text.** `get_window_extent`
returns the AABB of a rotated label, which at 60 degrees is roughly twice the
area the glyphs occupy. An AABB test on a radial layout reported sixteen
collisions that did not exist, and a guard that cries wolf gets switched off.

## Conventions that reviewers check

**Nomenclature.** Match the manuscript exactly, including whether gene symbols
are italicised. Conventions differ by journal and by organism; whatever the
paper does, the figure does. Protein and gene names are not interchangeable.

**Spelling.** One variety throughout, matching the manuscript. If the text says
"tumor", the figure does not say "tumour". Check the derived words too:
signaling, favorable, esophageal.

**Arrow semantics.** Fix a vocabulary and never break it:

- plain arrowhead: conversion, flux, or "leads to"
- blunt T-bar: inhibition
- open or dotted arrowhead: inferred or indirect
- double-headed: binding or reversible reaction
- an arrow through a membrane: transport, not signalling

Never use the same arrow for "A becomes B" and "A causes B". They are different
claims.

**Reaction direction.** Draw the direction the paper argues for. An enzyme that
runs reductively in the cell should not be drawn as an oxidation because the
classical assay was run that way. Say which direction is meant.

**Units and numbers.** Units on every axis and every value. SI, with the space
before the unit. No more significant figures than the measurement supports.
Percentages need a denominator somewhere.

**Chemistry.** Correct bond orders and substituent positions, or an explicitly
simplified skeleton labelled as simplified. A reviewer who knows the molecule
will look. Greek letters and subscripts set properly, not as plain text.

**Abbreviations.** Every one defined in the caption, even if defined in the
text. A figure is read on its own.

**Panel labels.** Bold, consistent corner, same size, in reading order.

**Scale.** A structure drawn beside a cell is not to scale. Either say so or do
not imply it.

## Readability

**Type scale.** One sans-serif family, four or five sizes, no exceptions. Below
about 5 pt at final printed size, nothing is reliably legible; 4.5 pt is the
floor for incidental annotation. Decide the printed width first, then set the
sizes, then never scale the figure.

**Line weights.** A small set, consistently applied: hairline for rules and
detail, medium for structure, heavy only for the one thing that matters most.
Thick uniform outlines on everything is what makes a figure look like clip art.

**Contrast and colour.** One hero hue carrying the subject, a small set of
accents, large areas in tints and saturation reserved for small marks. Never
encode anything in colour alone: pair it with position, shape or line style.

Check for colour-vision deficiency rather than assuming. Rust against olive, and
teal against grey, are the pairs that fail most often:

```python
# crude deuteranope check: collapse the red-green axis and compare
import numpy as np
from matplotlib.colors import to_rgb
def deuter(c):
    r, g, b = to_rgb(c)
    return (0.625*r + 0.375*g, 0.7*r + 0.3*g, b)
pairs = [("#B04A2C", "#6B7B3C"), ("#0F7A72", "#4A5862")]
for a, b in pairs:
    d = np.linalg.norm(np.array(deuter(a)) - np.array(deuter(b)))
    print(a, b, f"separation {d:.3f}", "OK" if d > 0.20 else "TOO CLOSE")
```

**Negative space.** Crowding is the commonest readability failure and the
easiest to fix: delete a layer rather than shrink the type.

**Reading order.** Decide where the eye starts and enters next, and make the
layout enforce it. Left to right for a causal argument; radial for a system with
no start. A reader should never have to search for the entry point.

**Label density.** If a zone needs more than about three lines of annotation, it
is doing too much; split it or move the detail to the caption.

**The caption carries the detail.** The figure carries the argument. Anything a
reader needs only once belongs in the caption.
