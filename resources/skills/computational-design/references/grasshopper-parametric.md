# Grasshopper parametric, generative and data-driven design

Part of the computational-design skill. Load this file only for the topic you need. The router is `SKILL.md`.

## Skill 3 — Parametric Modeling (Grasshopper Teaching)

### Core Pipeline

```
INPUTS → LOGIC → OUTPUTS
Sliders, curves, refs → Transformations, conditionals → Geometry, data, fabrication output
```

Parameter tiers: Independent (sliders) → Intermediate (computed) → Dependent (final). Identify all three before building.

### Data Trees

| Operation | Effect | When to Use |
|---|---|---|
| `Graft` | List → tree of single-item branches | Act on each item independently |
| `Flatten` | Collapse all nesting to flat list | Downstream needs one list |
| `Simplify` | Remove unnecessary nesting | Post-operation cleanup |
| `Path Mapper` | `{A;B}(i) → {A}(B)` custom remap | Complex restructuring |
| `Flip Matrix` | Transpose rows/columns | Switch branching dimension |

Matching rule: **longest list** (repeats last item). Use `Cross Reference` for full combinatorial pairing.

### Student Error Catalog

| # | Error | What Student Sees | Cause | Fix |
|---|---|---|---|---|
| 1 | Data tree mismatch | Nulls, wrong output count | Incompatible tree structures | Param Viewer on both inputs; adjust Graft/Flatten |
| 2 | Domain confusion | Remap outputs all 0 or all 1 | Domain min = max, or inverted | `Bounds` before Remap; check min ≠ max |
| 3 | Forgotten internalize | Works on one machine, breaks on another | Referenced geometry not internalized | Right-click param → Internalise Data |
| 4 | Surface UV confusion | Points appear in wrong position | Mixing world coords with UV params | `Surface CP` to get UV; `Evaluate Surface` with UV |
| 5 | Null propagation | Everything downstream is red/null | One upstream component returns null | Param Viewer backward from first null |
| 6 | Divide Surface mismatch | Pattern doesn't align to surface | UV count wrong; surface has seam | Rebuild surface first; check Count inputs |
| 7 | Wrong plane orientation | Geometry mirrored or rotated | Plane Z-axis pointing wrong direction | `Plane Normal` or `Plane 3Pt` explicitly |
| 8 | Unit confusion | Model appears tiny or enormous | Rhino units ≠ expected | Set Document Units before starting |
| 9 | Baking overwrites | Duplicate geometry accumulates | Baking again without deleting old | Use Elefront + layer system; delete before re-bake |
| 10 | List vs item mismatch | Single result instead of per-item | Wrong input type | Check input type; use `List Item` if needed |

### Explanation Scaffolds

**Data trees:** "A data tree is a filing cabinet. Each drawer (branch) holds files (items). When two components have different filing systems, Grasshopper can't connect them. Param Viewer shows you the system. Graft adds a drawer per file. Flatten puts everything in one drawer."

**Attractor fields:** "An attractor measures distance. For each grid point: how far from the reference? That distance becomes a number. That number drives something — aperture size, rotation, density. Always: grid → distance → remap → apply."

**Graft:** "Graft means 'treat each item independently.' Without it: 10 curves + 10 values = 1 operation on all. With it: 10 separate operations, one per pair."

---

## Skill 4 — Generative Design

**Galapagos:** Genome = sliders. Fitness = numeric output. Population 50–200, generations 100–500. Re-run from multiple seeds — first result is rarely global optimum.

**Octopus / Wallacei:** 2–8 objectives, SPEA-2 / NSGA-II, Pareto front visualization. Wallacei adds statistical analytics and genome reintegration.

**Fitness function rules:** Normalize to 0–1. Penalize constraint violations heavily. Minimize by convention (negate maximize objectives).

**Kangaroo 2 goals:** `Length` (spring), `Anchor` (fixed), `Load` (force), `Pressure` (inflation), `Planarize` (flatten quads). Funicular: anchor boundary + gravity → catenary net → invert = compression shell.

---

## Skill 9 — Scripting Reference

```python
# GhPython component template
import Rhino.Geometry as rg

if x and t:
    curve = x if isinstance(x, rg.Curve) else None
    if curve:
        offsets = curve.Offset(rg.Plane.WorldXY, t, 0.01,
                               rg.CurveOffsetCornerStyle.Sharp)
        a = list(offsets) if offsets else None
```

**RhinoCommon geometry hierarchy:** `GeometryBase` → `Curve` (LineCurve, NurbsCurve, PolyCurve) | `Surface` (NurbsSurface, RevSurface) | `Brep` | `Mesh`

```python
mesh = rg.Mesh.CreateFromBrep(brep, rg.MeshingParameters.FastRenderMesh)
nurbs = curve.ToNurbsCurve()
u_domain = srf.Domain(0)
```

---

## Skill 15 — Data-Driven Design

**GIS (Grasshopper):** `Elk` (OSM: roads, buildings) + `Heron` (raster GIS, shapefiles, WMS). Set `Rhino EarthAnchorPoint` for correct CRS projection.

**Space syntax:** integration = global connectivity (high = public); choice = movement attractor (many shortest paths pass through). Tools: DepthmapX, `Decoding Spaces` GH plugin, custom Python with NetworkX.

---

## Skill 16 — Design Automation

**Rule-based space planning:** `python-constraint` or `OR-Tools`. Rooms as nodes, adjacency requirements as hard constraints, solve for valid layout.

**Drawing automation (Rhino):** `rs.AddLayout()` → `rs.AddDetail()` → `rs.DetailScale()` → `rs.SetDetailLock(detail, True)`.

---
