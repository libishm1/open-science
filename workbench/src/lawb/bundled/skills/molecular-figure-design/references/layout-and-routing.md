# Layout and connector routing

The layout is the argument. Pick the arrangement that matches the claim, then
make the geometry enforce the reading order.

## Choosing an arrangement

**Linear, left to right** when the claim is causal and has a beginning: cause,
mechanism, consequence, limitation. Reads as a sentence. This is the right
choice for a submission-portal graphical abstract, which is displayed small and
wide.

**Hourglass** when many inputs converge on one node and then fan out again, or
the reverse. Divergence and convergence become visible as the silhouette.

**Radial** when the subject is a system with no natural start: one centre, many
peripheral categories, groups that close back into a ring. Good as a full-page
figure. Poor as a portal graphical abstract, because portals display small and
radial figures need area.

**Small multiples** when the claim is "same thing, different conditions". Seven
copies of one fold with different ligands argues "one architecture, different
selection" more convincingly than any amount of prose.

## Routing connectors

Crossing connectors are the biggest legibility cost in a pathway figure, and
most crossings are free to remove.

**Order sources by destination.** If ten lanes feed six nodes, sort the lanes by
which node they terminate at, keeping the original numbering visible on a badge.
In a real case this took a tangle of ten crossing curves to zero crossings with
no loss of information.

**Let arrival do the converging.** Several connectors ending at the same point
read as a merge. You rarely need a separate collector or bus.

**Delete redundant connectors.** In a radial layout where each sector sits
directly inside its own group arc, spokes between them carry no information that
adjacency does not. They also tend to be drawn collinear with their own labels,
putting a line through the text. Removing them removed a whole layer of clutter;
the evidence grade moved onto the wedge outline instead.

**A route that must not touch anything should be drawn not touching anything.**
To show a mechanism that bypasses an intermediate step, run it along a boundary
between sectors, crossing the whole ring without entering any of it. The
geometry then makes the argument without a caption.

## Text in a radial layout

The constraint that governs everything: a sector has **width along the arc** and
**length along the radius**, and they are different sizes.

- At radius r, a sector of angle t degrees gives an arc of `r * t * pi / 180` mm.
  At r = 34 and t = 36 degrees that is about 21 mm.
- Along the radius you have whatever gap you left between rings.

So: **short labels run along the arc, long labels run along the radius.** Put
the number and the short name tangentially inside the wedge, and the longer
reaction radially in the gap outside it, or compress the reaction to fit the arc
and keep the annulus clear.

**Anchor long radial labels at their outer end and let them grow inward.** A
label anchored at the inner end and growing outward will eventually run through
whatever ring sits beyond it, and the length varies with the string.

**Keep text upright.** For radial text, flip the rotation by 180 degrees on the
left half and swap the horizontal alignment. For tangential text, flip by
hemisphere so nothing reads bottom-up.

**Prefer horizontal labels on the outside of a ring.** They read the same way
all the way round. Stack multi-line blocks in screen-vertical, not along the
radius: stacking radially puts the lines side by side at east and west, where
they collide. Choose the side by hemisphere so the block always sits outside the
ring.

## Bands and zones

Divide the sheet into horizontal bands with explicit coordinates: title band,
stage, footer. Give every zone its own band and its own x-range, and derive
every element position from those constants rather than typing numbers. When a
collision appears, change the band, not the label.

Leave a rule between bands that change register, for example between a mechanism
diagram and a discussion of why trials failed. A change of visual register tells
the reader the kind of claim has changed.

## Negative space

Crowding is the commonest failure. The fix is to remove an element, not to
shrink the type. If a zone needs more than about three lines of annotation, it is
carrying too much; split it or move the detail to the caption.
