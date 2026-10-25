# Verification and export

## The collision guard

```
py -3.11 scripts/check_overlaps.py my_figure:build
```

Builds the figure, measures every `Text` artist, and reports overlaps and
anything off the canvas. Exit status 1 if anything is found, so it gates a
build.

**It measures rotated boxes, not bounding boxes.** `get_window_extent` returns
the axis-aligned box of a rotated label, which at 60 degrees is about twice the
area the glyphs occupy. The guard instead measures each label unrotated, rotates
the rectangle about its own anchor, and clips the two convex quadrilaterals
(Sutherland-Hodgman) for a true intersection area.

This matters: an axis-aligned version of this guard reported sixteen collisions
in a radial layout, every one of them false. The rotated version reported none,
and reported the same result as the AABB version on a layout with no rotated
text, which is the cross-check that it is correct.

Tune with `--pad` (clearance demanded around each label, mm) and `--min-area`
(ignore slivers).

## What verification cannot do

The guard sees text against text. It does not see:

- text sitting on a graphic
- a connector crossing a panel it should not
- an arrowhead landing on the wrong object
- a label attached to the wrong thing
- a colour collision
- a claim that is simply wrong

Render it and read it. Then shrink it to final printed width and read it again.

## Export formats

| Format | Setting | For |
|---|---|---|
| PDF | `pdf.fonttype = 42` | submission, vector, text selectable |
| SVG | `svg.fonttype = "none"` | editing, text stays live |
| TIFF | 600 dpi, LZW | journals that demand raster |
| PNG | 300 to 600 dpi | preview, slides, email |

Write TIFF by rendering a PNG at the target dpi and converting with Pillow:
matplotlib has no TIFF writer, and going through PIL lets you set LZW
compression and embed the dpi.

Keep the figure vector. The only raster elements should be the gradient and
shadow layers, which are images by nature.

## File size

Two independent terms, and the intuition is usually wrong:

- **Raster layers**: controlled by `PX_PER_MM`. Smooth, so they tolerate low
  resolution well.
- **Vector paths**: the number of path segments. A figure containing eight
  protein ribbons has tens of thousands of segments, and *this* dominates.

On a real figure, halving the raster resolution changed a 733 kB PDF to 732 kB.
If a PDF is too large, reduce ribbon resampling (`per_seg`) or the number of
structures, not the raster resolution.

If a submission portal caps upload size, export PNG at 200 dpi and quantise with
**octree**, not median cut. Median cut allocates its palette by volume and
strips saturation from small coloured regions, which washes out exactly the
ligands and highlights you care about. Octree held a mean deviation of 1.67 of
255 on a real figure, though it does band smooth halos; check before shipping.

## Reproducibility

Cache the structures. After the first fetch, every build is offline and
byte-identical, which means the figure rebuilds years later when the fetch
endpoint has changed.

Pin the content in one module, keep the drawing code free of facts, and the
figure becomes reviewable as a diff. That is the real argument for generating
figures as code rather than drawing them: not that it is faster the first time,
because it is not, but that revision two is cheap and revision ten is still
correct.

## Before handing back

Run the checklist at the end of [../SKILL.md](../SKILL.md). Steps 1 to 5 are
cheap and catch regressions; step 6, reading the render, catches what the others
cannot.
