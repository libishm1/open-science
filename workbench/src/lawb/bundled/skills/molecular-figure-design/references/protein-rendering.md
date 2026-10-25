# Rendering a protein as vector cartoon, without PyMOL

PyMOL is the default answer and it is a good one, but it is a heavy install and
it rasterises. For a figure whose other elements are vector, a rasterised
protein is the one blurry object on the page, and it cannot be recoloured to
match the palette without re-rendering.

`molfig/structure.py` does it in numpy: fetch, parse, assign secondary
structure, build ribbon polygons, depth-sort, draw. The output is matplotlib
paths, so it stays vector in the PDF and SVG.

## Verify the entry first

Always, before the ID reaches a caption:

```
py -3.11 scripts/verify_pdb.py 1AH3 3BUR --expect "1AH3=ALDOSE REDUCTASE"
```

It prints the `COMPND` molecule name, the chain with the most residues, and
every ligand with the chemical name from its own `HETNAM` record.

A case that actually occurred: an entry's title described a ternary complex with
a reduced steroid *product*, but the deposited ligand's `HETNAM` record named
the unreduced *substrate*. Both cannot be true. The figure captioned what the
coordinates contained and flagged the discrepancy to the authors.

Ligand codes are also worth reading for free material: inhibitor-bound entries
let a figure show the drug in the pocket rather than asserting it in a label.

## Chain selection

Do not assume chain A. Some entries start at B, and some have the biological
unit split across chains. `parse_pdb(path, chain="auto")` takes the chain with
the most C-alpha atoms, which is right for a cartoon almost always. Pass an
explicit chain when the point of the figure is an interface.

## Secondary structure from geometry

A full DSSP run needs backbone N and O and a hydrogen-bond energy term. For a
cartoon, the C-alpha distance signature separates helix from strand well enough:

- helix: `d(i, i+3)` about 5 to 6.6 A **and** `d(i, i+4)` about 5.4 to 7.6 A
- strand: `d(i, i+2)` above 6.2 A, `d(i, i+3)` above 9 A, `d(i, i+4)` above 11.5 A

with a minimum run length (4 for helix, 2 for strand) to suppress noise. A
misassignment costs one ribbon segment of visual noise, not a wrong figure. If
the fold matters to the argument, run real DSSP and pass the result in.

## The three geometry problems, and their fixes

**Helices render as corkscrews.** Cartoon renderers draw the helix *axis*, not
the C-alpha spiral. A 5-residue running mean over helical stretches cancels the
3.6-residue repeat and gives a clean ribbon. Leave loops unsmoothed.

**Tight turns render as triangular fans.** When a turn is tighter than the
ribbon is wide, the offset edge folds through itself. Clamp the half-width to
the local radius of curvature, computed as the circumradius of each vertex
triple, at about 0.72 of it. This is the single fix that makes the output look
professional.

**Seams between segments.** Drawing one quad per residue and stroking each
leaves visible seams. Build one closed polygon per secondary-structure element
(left edge plus reversed right edge), stroke it once, and depth-sort elements
back to front. Loops look better as stroked round-capped polylines than as thin
ribbons.

## Orientation

PCA on the C-alpha coordinates puts the widest face in the picture plane, which
is usually the view that most looks like the fold. Then hand-tune with
`roll`, `tilt`, `spin` in degrees. Render a grid of six candidates and pick one:
it takes a minute and the difference between a readable fold and a tangle is
large. For a barrel, a view slightly down the axis with the cofactor visible in
the mouth reads best.

## Depth

Map each element's mean depth to lightness, with near elements lighter and more
saturated. That alone gives the fold legible three-dimensionality without any
lighting model. Add a blurred silhouette behind it for a contact shadow, and a
subtracted-mask halo for a soft glow, computed from the union of the ribbon
polygons rather than a convex hull, which looks angular.

## Ligands

Draw bonds from a 3D distance cutoff of about 1.85 A, never from atom order:
PDB atom order zigzags across a molecule and a polyline through it looks like
noise. Sanity-check the count. For NADP, 48 atoms should give 52 bonds, because
a connected molecule with three rings has `atoms + rings - 1` bonds. A count far
above that means spurious bonds and a wrong cutoff.

Set the atom radius in millimetres and convert to points, so the ligand stays in
scale whatever box the structure is drawn in. Filter solvent: water, glycerol,
ethylene glycol, sulfate, DMSO and friends are crystallisation artefacts, not
biology.

## Thumbnails

Small multiples of the same fold with different ligands make an argument that no
amount of prose does: same architecture, different pocket occupant. At 17 to 20
mm each, drop the ribbon outline weight to about 0.05 and skip the halo, or the
strokes close up the detail.
