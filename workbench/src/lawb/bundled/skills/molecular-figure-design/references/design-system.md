# The design system

One canvas, one coordinate system, one type scale, one palette. Everything
below is in `molfig/style.py`.

## Work in millimetres

```python
fig, ax = S.canvas(180, 132)   # data coordinates are now millimetres
```

A single axes spanning the whole figure, `set_aspect("equal")`, limits in mm.
Every position in the layout is then a real measurement you can reason about and
check, not a fraction of something that changes when the figure resizes.

Inset chart axes are placed by converting mm to figure fractions, so charts live
in the same coordinate system as the drawing.

## Decide the printed width first

Type is specified in points. Points are absolute. So the figure must be built at
the width it will be printed at, or every label changes size when the journal
scales it. Full column width for most journals is 180 mm. Build at 180 and grow
downward when you need more room. Never build at 240 and let it be shrunk.

## Type scale

Five sizes, one sans-serif family, no italics except where convention demands:

| Role | Size |
|---|---|
| Title | 10.5 pt |
| Zone heading | 6.6 pt |
| Label | 5.6 pt |
| Micro annotation | 4.8 pt |
| Chart tick | 4.4 pt |

Below about 4.5 pt at final size, nothing is reliably legible. If a label will
not fit at 4.8, the content is too long, not the type too big.

Set `pdf.fonttype = 42` and `svg.fonttype = "none"` so text stays text:
selectable in the PDF, editable in the SVG, and searchable in both.

## Palette

One hero hue for the subject, a small set of accents, a neutral ink ramp, and a
warm paper. Large areas take tints; saturation is reserved for small marks.

Warm off-white paper rather than pure white reads as print rather than screen,
and gives the pale tints something to sit against.

**Check accent pairs for colour-vision deficiency before committing.** The
method and a runnable check are in
[debugging-and-readability.md](debugging-and-readability.md). The palette
shipped here was revised twice after that check failed: rust against olive, teal
against slate, then amber against rust.

## Depth without outlines

This is the difference between a figure that looks drawn and one that looks
assembled from clip art. Three effects, all computed as blurred numpy masks:

- `soft_shadow` — rasterise the shape to a mask, Gaussian blur it, offset it,
  paint it under the shape. A contact shadow, not a drop shadow.
- `inner_shade` — blur the *inverse* mask and multiply by the mask, giving
  ambient occlusion just inside the edge. Reads as volume.
- `glow` — blur the mask and subtract the original, giving a soft halo. Use
  sparingly, on the one element that should be the focal point.

Fills are true gradients, not flat colours: build an RGBA array, `imshow` it
over the shape's bounding box, and clip it to the path.

`PX_PER_MM` controls the resolution of all of these. They are smooth by
construction, so it can drop a long way before it shows.

## Shapes

A cell is not an ellipse and a zone is not a rounded rectangle from a slide
template. Two generators:

- `blob(cx, cy, rx, ry, seed, jitter)` — radial noise smoothed and closed with a
  Catmull-Rom spline, for organic objects.
- `organic_rect(cx, cy, rx, ry, n)` — a superellipse with a little noise, which
  keeps the usable interior area of a rectangle while reading as a cell.

Both return matplotlib `Path` objects, so they clip gradients and accept the
same stroke and shadow treatment as anything else.

## Arrows

`taper_arrow` draws a quadratic Bezier whose shaft widens along its length. A
tapered shaft carries direction before the reader notices the head, which keeps
a pathway legible when the figure is shrunk. `inhibit_arrow` draws the blunt
T-bar.

Fix the arrow vocabulary before drawing and keep it: conversion, inhibition,
inference and binding must not share a glyph.

## Content separation

The drawing code contains no facts. A `content.py` holds every label, number,
claim and evidence grade; the layout interpolates from it. The figure then
cannot disagree with the manuscript without the change appearing in a diff, and
a co-author can review the claims without reading matplotlib.
