---
name: molecular-figure-design
description: 'Build publication-quality scientific figures programmatically in Python, including graphical abstracts and pathway diagrams that feature real protein structures rendered from deposited PDB coordinates without PyMOL. Covers the millimetre design system, cartoon ribbon geometry, skeletal chemistry glyphs, encoding evidence grade as line style, layout and connector routing for linear and radial figures, automated text-collision guards, and vector export for journal submission. Use when designing, drawing, revising or exporting any figure for a paper, poster or review in structural biology, biochemistry, pharmacology or molecular medicine, and whenever a figure needs to show a protein, a reaction, a pathway or a mechanism.'
license: Apache-2.0
author: libishm1
---

# Molecular figure design

Figures for molecular and structural papers, generated as code rather than drawn
by hand. The result is reproducible, diffable, and free of the flat
pastel-and-thick-outline house style that drag-and-drop tools impose.

The things this does that an icon library cannot: render the **actual protein**
from deposited coordinates, draw **correct chemistry**, and encode **how well
supported each claim is** as a visual property.

## Core rules

**1. Verify a structure before you cite it.** A PDB ID in a caption is a claim
repeated to every reader. Titles and deposited ligands do not always agree: one
entry's title described a complex with a reduced product, while its own HETNAM
record defined the deposited ligand as the unreduced substrate. Run
[`scripts/verify_pdb.py`](scripts/verify_pdb.py) and caption what the
coordinates contain, not what the title says.

**2. Facts live in a content module, never in drawing code.** One `content.py`
holds every label, number and claim; the layout interpolates from it. This is
the only way a figure and its manuscript stay in agreement through a revision,
and it makes the figure's claims reviewable as a diff.

**3. Never invent a number the source does not contain.** If the paper reports
no IC50, draw no potency chart. Mark the gap visibly instead. A fabricated
value in a figure is a fabricated result.

**4. Fix the sheet width to the journal's column width.** Type specified in
points only stays legible if the figure is printed at the width it was designed
for. Growing the canvas sideways to fit more content shrinks every label once
the journal scales it back. Grow downward instead.

**5. Depth comes from blurred masks, not outlines.** Soft contact shadows,
ambient occlusion inside edges, and true gradient fills are what stop a figure
looking like clip art. Thick uniform outlines are what make it look like clip
art.

**6. Encode evidence grade as line style.** Solid for demonstrated, dashed for
association, dotted for inference. See
[references/evidence-encoding.md](references/evidence-encoding.md).

**7. Order elements by destination, not by source numbering.** Connectors that
cross are the single biggest legibility cost in a pathway figure, and ordering
lanes by where they terminate usually removes every crossing at no cost.

**8. Guard text collisions with real geometry.** `get_window_extent` returns the
axis-aligned box of a rotated label, which for text at 60 degrees is about twice
the area the glyphs occupy. An axis-aligned test reported sixteen collisions in
a radial layout that did not exist.
[`scripts/check_overlaps.py`](scripts/check_overlaps.py) rotates each box about
its own anchor and clips the quadrilaterals.

**9. A guard that passes is not a figure that works.** Collision checks catch
text on text, never text on graphics. Render it and look at it.

**10. Keep it vector, and know what costs bytes.** Exported PDF size is
dominated by the number of vector paths, not by the raster gradient layers.
Halving the raster resolution of a figure full of ribbons changed almost
nothing.

## Task router

| Task | Read |
|---|---|
| Render a protein, pick a view, fix ribbon artefacts | [references/protein-rendering.md](references/protein-rendering.md) |
| Set up canvas, palette, type scale, depth effects | [references/design-system.md](references/design-system.md) |
| Arrange a pathway: linear, hourglass or radial | [references/layout-and-routing.md](references/layout-and-routing.md) |
| Show how well supported each claim is | [references/evidence-encoding.md](references/evidence-encoding.md) |
| Draw molecules, membranes, cells, organelles | [references/chemistry-and-glyphs.md](references/chemistry-and-glyphs.md) |
| Something looks wrong, or will not fit, or will not read | [references/debugging-and-readability.md](references/debugging-and-readability.md) |
| Nomenclature, arrow semantics, units, colour-vision safety | [references/debugging-and-readability.md](references/debugging-and-readability.md) |
| Check it, export it, meet submission limits | [references/verification-and-export.md](references/verification-and-export.md) |

## Scripts

- [`scripts/molfig/style.py`](scripts/molfig/style.py) design system: millimetre
  canvas, palette, type scale, organic shapes, gradient fills, soft shadows,
  tapered arrows.
- [`scripts/molfig/structure.py`](scripts/molfig/structure.py) PDB fetch and
  cache, C-alpha extraction, secondary-structure assignment, ribbon geometry,
  ball-and-stick ligands, optional PyMOL route.
- [`scripts/molfig/glyphs.py`](scripts/molfig/glyphs.py) generated biological
  and chemical glyphs, including correct skeletal structures.
- [`scripts/molfig/panels.py`](scripts/molfig/panels.py) evidence-grade key and
  census, and a way to mark a gap the source cannot fill.
- [`scripts/verify_pdb.py`](scripts/verify_pdb.py) confirm an entry is what you
  think before citing it.
- [`scripts/check_overlaps.py`](scripts/check_overlaps.py) text collision guard,
  exits non-zero so it can gate a build.
- [`templates/example_figure.py`](templates/example_figure.py) smallest figure
  that exercises the whole pipeline.

Dependencies are numpy, scipy, matplotlib, requests and pillow. No PyMOL, no
Inkscape, no cairo. On Windows without admin rights, install with
`py -3.11 -m pip install --user ...` and do not run scripts with `-I`, which
hides the user site-packages.

## Where this runs

Anywhere Python runs. The modules are plain matplotlib, so a figure built here
drops into a manuscript build chain, a notebook, or a CI job unchanged.
Structures are cached after first fetch, so later builds are offline and
byte-identical.

## Before handing a figure back

```
 1. structures verified    verify_pdb.py agrees with every caption
 2. facts from content     no number or claim typed into drawing code
 3. evidence grades        every connector styled; inferences not drawn solid
 4. no invented data       gaps marked, not filled
 5. collisions             check_overlaps.py passes on every layout
 6. read the render        text on graphics, crossings, orphaned labels
 7. width                  sheet matches the journal's column width
 8. export                 PDF with Type-42 fonts, SVG with live text, TIFF at 600 dpi
 9. size                   under the portal's upload limit
10. caption                states what the coordinates contain, not the entry title
```

Steps 1 to 5 are cheap and catch regressions. Step 6 catches what the others
cannot.
