# Chemistry and biological glyphs

`molfig/glyphs.py` generates these from parameters rather than importing an icon
set. Bioicons, SciDraw and the NIH BioArt collections are all good sources, but
a downloaded icon fixes its line weight, palette and level of abstraction before
your layout exists, licences differ per icon, and you cannot restyle the set
from one place. Generated glyphs take the figure's stroke weight and palette by
construction.

## Draw real structures

A reviewer who knows the molecule will look at it. Either draw it correctly, or
draw an explicitly simplified skeleton and say so in the caption. A
nearly-correct structure is worse than an obviously schematic one, because it
asserts detail it has not earned.

`draw_bonds` takes `(i, j, order)` triples over a vertex array, so correct bond
orders cost nothing:

```python
pts = zigzag(x, y, 9, L=1.25)          # standard skeletal chain
bonds = [(i, i + 1, 1) for i in range(8)]
bonds[1] = (1, 2, 2)                   # the C2=C3 alkene
draw_bonds(ax, pts, bonds)
```

`atom_label` puts a paper-coloured halo behind heteroatom labels so bonds read
cleanly behind them. Carbons stay implicit, as in any skeletal formula.

## Before and after pairs

A reaction is far clearer as two structures that differ in one place than as an
arrow with text. `hne(reduced=False)` and `hne(reduced=True)` differ only in the
C1 group, which is exactly what the reduction changes: the alkene is untouched
and visibly so. Build reaction glyphs as parameterised pairs for this reason.

## Fused rings

`hexagon(cx, cy, r, pointy_top=True)` puts vertices at 30, 90, ... degrees, which
gives vertical left and right edges, so rings fuse horizontally by sharing an
edge at a centre spacing of `r * sqrt(3)`. That is the basis for anthracene-like
tetracyclic cores and most drug scaffolds you will need to sketch.

## Cells and membranes

- `cell(ax, path)` — gradient cytoplasm, occluded rim, double membrane line.
  Takes a `Path`, so use `organic_rect` for a cell with usable interior area.
- `nucleus(...)` — envelope, pores spaced along the real outline, chromatin tint.
- `bilayer(x0, x1, y, oxidised=(3, 7))` — phospholipid strip where named indices
  are drawn kinked and peroxide-capped. Lipid peroxidation drawn as geometry
  rather than as a red arrow.
- `immune_cell(...)` — ruffled outline, large nucleus.
- `ros(...)` — radiating burst for reactive species.
- `zoom_callout(src, dst_rect)` — marker plus leader lines to a detail panel.
  A magnified membrane patch beside a whole cell is the cheapest way to show
  two scales at once without implying the cell is drawn to scale.

## Cofactor cycles

`cofactor_cycle(cx, cy, r)` draws the circular arrow for a shared, finite pool
such as NADPH. Worth drawing explicitly whenever the argument depends on
competition for a cofactor, because the competition is invisible otherwise.

## Keep the vocabulary small

Every new glyph shape is a symbol the reader must learn. Reuse before you
invent, and make sure each shape means exactly one thing across the whole
figure set. Two glyphs that look similar but mean different things cost more
than a crowded panel.
