---
name: computational-design
description: Use this skill for any question about computational design, parametric modeling (Grasshopper, Dynamo, sliders, data trees, GH definition, teaching Grasshopper, student errors), generative design (evolutionary algorithms, Galapagos, Octopus, Wallacei, NSGA-II, fitness functions), GraphML for AEC (graph neural networks, GNN, heterogeneous graphs, IFC as graph, message passing, node classification, link prediction, GraphML, GML, DGCNN, graph machine learning, Bridge to GNN, Categories A-D, PRISMA systematic review AEC), Topologic (TopologicPy, IFC cell complex, spatial topology, fire egress, shortest path, face adjacency, CellComplex), algorithmic patterns (tessellation, L-systems, Voronoi, Penrose, Islamic geometry), structural computation (Karamba3D, Kangaroo, form-finding, FEA, topology optimization), environmental simulation in hot-arid climate (Ladybug, Honeybee, solar, daylight, EnergyPlus, Riyadh, Gulf, ASHRAE), facade computation (panelization, rationalization, curtain wall, kinetic facades), digital fabrication (CNC, 3D printing, laser cutting), BIM scripting (Revit API, pyRevit, IFC, IfcOpenShell), interoperability (Speckle, Rhino.Inside, IFC pipelines), scripting (GhPython, RhinoCommon, C# Grasshopper, pyRevit), optimization, data-driven design, mesh processing, design automation, ML for AEC (GNN, GANs, CV, SAM, GroundedSAM, LLM task planning).
license: see repository LICENSE
---

# Computational Design Skills for AEC
*Extended for: GraphML/GNN research, Topologic IFC spatial reasoning, Grasshopper teaching, hot-arid climate, robotic fabrication (UR10e stack)*

---

## Paradigm Overview

| Paradigm | When to Use | Primary Tools |
|---|---|---|
| **Parametric** | Constrained design space, well-defined variables | Grasshopper, Dynamo |
| **Generative** | Multiple conflicting objectives, large solution space | Galapagos, Octopus, Wallacei |
| **Algorithmic** | Rules-driven: shape grammars, L-systems, cellular automata | Grasshopper, Python |
| **Data-Driven** | Site conditions, sensor, GIS layers drive form | Elk, Heron, Ladybug, Pandas |
| **Performance-Driven** | Simulation-in-the-loop: structural, energy, daylight, wind | Karamba3D, Honeybee |
| **Graph-Based** | Spatial topology, relational reasoning, GNN on buildings | TopologicPy, PyTorch Geometric |

---

## Skill 1 — GraphML for AEC (Research Domain)

### Why Buildings Are Graphs

Buildings have natural graph structure: rooms are nodes, adjacencies are edges, IFC entity relationships are typed edges. GraphML is the correct representation for spatial reasoning, fire egress, energy zone interaction, structural load paths, and BIM classification.

GraphML/GML (Graph Machine Learning) applies ML directly to this graph structure. GNN (Graph Neural Network) is the primary model class.

### Bridge-to-GNN Framework (Categories A–D)

This inclusion framework classifies AEC GraphML papers by proximity to core AEC tasks:

| Category | Definition | Example |
|---|---|---|
| **A** | GNN directly on AEC geometry or topology | GNN for floor plan generation from adjacency graph |
| **B** | GNN for AEC performance prediction | Structural load path prediction from building graph |
| **C** | GraphML on AEC process/workflow | Graph-based construction scheduling |
| **D** | Graph representation only — no ML | Space syntax as graph; IFC as graph without learning |

A and B are core inclusions. C is context. D is excluded unless it establishes foundational representation used by later ML work.

### IFC → Graph Representation

```python
import ifcopenshell
import networkx as nx

def ifc_to_spatial_graph(ifc_path):
    model = ifcopenshell.open(ifc_path)
    G = nx.Graph()

    for space in model.by_type("IfcSpace"):
        area = 0.0
        for rel in space.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                if hasattr(pset, "HasProperties"):
                    for prop in pset.HasProperties:
                        if prop.Name == "NetFloorArea":
                            area = float(prop.NominalValue.wrappedValue)
        G.add_node(space.GlobalId,
                   name=space.LongName or space.Name or "",
                   area=area)

    for rel in model.by_type("IfcRelAdjacentSpace"):
        if hasattr(rel, "RelatingSpace") and hasattr(rel, "RelatedSpaces"):
            for related in rel.RelatedSpaces:
                G.add_edge(rel.RelatingSpace.GlobalId,
                           related.GlobalId, type="adjacent")
    return G
```

**Heterogeneous graph (PyTorch Geometric):**
```python
from torch_geometric.data import HeteroData
data = HeteroData()
data['space'].x = space_features       # [N_spaces, d]
data['wall'].x  = wall_features        # [N_walls, d]
data['space', 'bounded_by', 'wall'].edge_index = space_wall_edges   # [2, E]
data['space', 'connected_by', 'door'].edge_index = space_door_edges
```

### GNN Architectures for AEC Tasks

| Task | Architecture | Reason |
|---|---|---|
| Room type classification | GCN, GraphSAGE | Node-level; inductive across buildings |
| Structural load path | GAT | Attention weights model force distribution |
| Fire egress optimization | Dijkstra + GNN heuristic | Shortest path on cell adjacency graph |
| Space layout generation | GGNN | Sequential room placement |
| Energy zone interaction | GCN on zone graph | Zone=node, shared surface=edge with U-value |
| BIM element classification | DGCNN | Point cloud + dynamic edge construction |

### Message Passing (GCN)

```python
import torch, torch.nn.functional as F
from torch_geometric.nn import GCNConv

class BuildingGCN(torch.nn.Module):
    def __init__(self, in_ch, hidden_ch, out_ch):
        super().__init__()
        self.conv1 = GCNConv(in_ch, hidden_ch)
        self.conv2 = GCNConv(hidden_ch, out_ch)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.5, training=self.training)
        return F.log_softmax(self.conv2(x, edge_index), dim=1)

# GCN update: h_v^k = σ( W · MEAN({ h_u^(k-1) : u ∈ N(v) ∪ {v} }) )
# GAT replaces uniform mean with attention weights α_vu
```

### Node Feature Design (Transferable Across Buildings)

**Space nodes:** normalized area (÷ building total), aspect ratio, floor level (normalized), perimeter-to-area ratio, WWR if available, one-hot program type.

**Wall edges:** shared length, is-exterior flag, U-value, contains-opening flag.

**Never use absolute coordinates** — breaks transferability across different buildings.

### PRISMA Search Methodology (Exact as Executed)

Individual search terms (no inferred Boolean operators):
`Graph Machine Learning` · `GML` · `DGCNN` · `GNN` · `AEC` · `Architecture Engineering Construction`

Databases: Scopus, Web of Science, IEEE Xplore, ACM Digital Library.

Inclusion decision follows Bridge-to-GNN Categories A–D above.

---

## Skill 2 — Topologic + IFC Spatial Reasoning

### What Topologic Does

Topologic (TopologicPy) models buildings as **CellComplexes** — topologically consistent 3D partitions where cells share faces. This gives:
- Fire egress routing (cells connected by navigable door faces)
- Energy zone interaction (cells sharing thermal boundary faces)
- Room adjacency analysis (cells sharing interior faces)
- Structural load tracing

Standard IFC loaders give geometry. Topologic gives **topology** — which spaces touch which, through which boundary.

### Core Object Hierarchy

```
Vertex → Edge → Wire → Face → Shell → Cell → CellComplex → Cluster
```

Key methods:
- `Cell.Faces(cell)` — all bounding faces
- `Face.Cells(face, complex)` — cells on both sides (returns 2 if shared)
- `CellComplex.Cells(complex)` — all cells
- `Topology.SharedFaces(cellA, cellB)` — faces shared between two cells

### Fire Egress on CellComplex

```python
import networkx as nx
import topologic

def build_egress_graph(cell_complex, door_faces):
    G = nx.Graph()
    for cell in topologic.CellComplex.Cells(cell_complex):
        G.add_node(topologic.Topology.GUID(cell))

    for face in door_faces:
        adj = topologic.Face.Cells(face, cell_complex)
        if len(adj) == 2:
            a, b = topologic.Topology.GUID(adj[0]), topologic.Topology.GUID(adj[1])
            area = topologic.Face.Area(face)
            G.add_edge(a, b, weight=1.0 / max(area, 0.01))
    return G

def shortest_egress(G, start_id, exit_ids):
    best_path, best_cost = None, float('inf')
    for exit_id in exit_ids:
        try:
            cost = nx.shortest_path_length(G, start_id, exit_id, weight='weight')
            if cost < best_cost:
                best_cost = cost
                best_path = nx.shortest_path(G, start_id, exit_id, weight='weight')
        except nx.NetworkXNoPath:
            continue
    return best_path, best_cost
```

### RL Evacuation Agent

```python
import gymnasium as gym
import numpy as np

class EvacuationEnv(gym.Env):
    """Agent navigates CellComplex graph to exit. +100 exit, -1/step, -50 dead end."""
    def __init__(self, G, start_id, exit_ids):
        self.G = G
        self.start_id = start_id
        self.exit_ids = set(exit_ids)
        self.nodes = list(G.nodes())
        self.node_idx = {n: i for i, n in enumerate(self.nodes)}
        n = len(self.nodes)
        self.observation_space = gym.spaces.Discrete(n)
        self.action_space = gym.spaces.Discrete(n)

    def reset(self):
        self.current = self.start_id
        return self.node_idx[self.current], {}

    def step(self, action):
        target = self.nodes[action]
        if target in self.G.neighbors(self.current):
            self.current = target
        done = self.current in self.exit_ids
        reward = 100 if done else -1
        return self.node_idx[self.current], reward, done, False, {}
```

---

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

## Skill 5 — Environmental Simulation (Hot-Arid / Riyadh)

### Design Priorities for Hot-Arid Climate

Generic temperate benchmarks don't apply. Hot-arid design is cooling-dominant.

| Issue | Riyadh Context | Response |
|---|---|---|
| Cooling season | 7–9 months | Minimize solar gain on E/W/roof; maximize thermal mass |
| Solar radiation | 5.5–6.5 kWh/m²/day | External shading mandatory on all orientations except N |
| Glare | High sun altitude + white landscape | Diffuse light preferred; direct sun = glare AND heat |
| Wind | Shamal (NW) prevailing; summer dust | Minimize NW openings; use for night cooling |
| Humidity | 10–30% (low, except coastal) | Evaporative cooling viable; night-flush works |

### Ladybug Tools Stack

```
EPW: SAU_Riyadh.411380_IWEC.epw
       ↓
Ladybug: sun path, radiation rose, wind rose, outdoor thermal comfort (UTCI)
       ↓
Honeybee: daylight (Radiance/DAYSIM), energy (EnergyPlus)
       ↓
Dragonfly: urban-scale UHI, street microclimate
       ↓
Butterfly / Eddy3D: CFD wind
```

### Performance Benchmarks — Hot-Arid

**Energy (ASHRAE 90.1):**
- Office EUI target: <120 kWh/m²/yr (Riyadh, mechanical-dominant)
- High-performance: <80 kWh/m²/yr
- Cooling load for high-performance hot-arid: <15 kWh/m²/yr (aggressive)

**Glazing for Riyadh:**
- North: low-e IGU, U ≤ 1.8 W/m²K, SHGC 0.35–0.45
- South/East/West: SHGC ≤ 0.25; external shading essential
- Summer solar altitude at noon (lat 24.7°N): ≈ 88° — horizontal overhangs nearly ineffective; vertical fins on E/W are more effective

**Daylight:**
- sDA₃₀₀/₅₀% ≥ 55% (LEED v4) — but shade aggressively to control ASE
- ASE₁₀₀₀/₂₅₀h < 10% — critical: direct sun = glare AND heat gain
- Use deep reveals, fritted glass, light shelves to diffuse high-altitude sun

**Outdoor comfort (UTCI):**
- Riyadh summer: UTCI routinely >46°C outdoors (extreme stress)
- Usable outdoor hours: before 9am and after 7pm only without intervention
- Shade + spray cooling required for any usable outdoor space

### Shading Fin Depth Calculation

```python
import math

lat = 24.7  # Riyadh
dec = 23.45  # summer solstice

def solar_altitude(lat, dec, hour_angle):
    lr, dr, hr = map(math.radians, [lat, dec, hour_angle])
    return math.degrees(math.asin(
        math.sin(lr)*math.sin(dr) + math.cos(lr)*math.cos(dr)*math.cos(hr)))

# Worst case: lowest sun on E/W facade during occupied hours
hour_angles = [(h - 12) * 15 for h in range(8, 18)]
min_alt = min(a for h in hour_angles
              if (a := solar_altitude(lat, dec, h)) > 0)

window_height = 1.2  # m
fin_depth = window_height / math.tan(math.radians(min_alt))
print(f"Minimum E/W fin depth: {fin_depth:.2f}m")
```

---

## Skill 6 — Structural Computation

**Form-finding:** Kangaroo 2 (dynamic relaxation), COMPAS TNA (thrust network analysis for masonry vaults), Force Density Method (precise cable nets).

**Karamba3D workflow:** `LineToBeam` → `CrossSection` → `Support` → `Load` → `Assemble` → `Analyze`. Key outputs: `Utilization` (must be <1.0), `MaxDisp`, `BeamForces`.

**Span-to-depth rules:** Steel beam L/20, continuous steel L/25, flat concrete slab L/30, PT slab L/40, timber beam L/15, gridshell R/400–600.

**Topology optimization (SIMP):** E(ρ) = E₀·ρᵖ (p=3). Tools: `Millipede`, `Ameba`. Inputs: design domain, supports, loads, volume fraction target.

---

## Skill 7 — Facade Computation

**Panelization strategies:** Planar quad (PQ mesh, lowest cost) → planar triangle → single-curved → cold-bent glass → double-curved mold (highest cost). Clustering by ±10mm tolerance reduces unique panel types dramatically.

**PQ Mesh:** `Evolute Tools` or `Kangaroo + PlanarizeQuads`. Target planarity: <5mm deviation.

**Hot-arid facade principle:** external shading always outperforms glazing spec. Computational mashrabiya patterns (aperture variation by solar exposure) achieve cultural resonance and performance simultaneously.

---

## Skill 8 — BIM Scripting

```python
# pyRevit — collect walls, read/write parameters
from pyrevit import revit, DB
doc = revit.doc
walls = DB.FilteredElementCollector(doc).OfClass(DB.Wall).ToElements()
with revit.Transaction("Update"):
    for w in walls:
        p = w.LookupParameter("Comments")
        if p and not p.IsReadOnly:
            p.Set("Processed")

# Room areas in m²
rooms = (DB.FilteredElementCollector(doc)
           .OfCategory(DB.BuiltInCategory.OST_Rooms)
           .WhereElementIsNotElementType().ToElements())
for r in rooms:
    m2 = DB.UnitUtils.ConvertFromInternalUnits(r.Area, DB.UnitTypeId.SquareMeters)
```

```python
# IfcOpenShell — read property sets
import ifcopenshell
model = ifcopenshell.open("building.ifc")
for wall in model.by_type("IfcWall"):
    for rel in wall.IsDefinedBy:
        if rel.is_a("IfcRelDefinesByProperties"):
            pset = rel.RelatingPropertyDefinition
            if pset.is_a("IfcPropertySet"):
                for prop in pset.HasProperties:
                    print(prop.Name, prop.NominalValue)
```

IFC spatial hierarchy: `IfcProject` → `IfcSite` → `IfcBuilding` → `IfcBuildingStorey` → `IfcSpace`

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

## Skill 10 — Robotic Fabrication

> **Stack split:** For UR10e + RG6 + ROS2 specifics (ur_rtde, MoveIt2, FastAPI bridge, QoS matrices, Docker-compose, ROS2 action servers), use the `robotics-in-architecture` skill. This section covers fabrication concepts, robot selection, Grasshopper plugins, motion types, and native robot languages — applicable across all brands.

### Robot Selection Reference

| Robot | Reach (mm) | Payload (kg) | Repeatability (mm) | AEC Use |
|---|---|---|---|---|
| **UR10e** *(primary stack)* | 1300 | 12.5 | ±0.03 | Light assembly, collaborative, lab fab |
| UR16e | 900 | 16 | ±0.03 | Heavier collaborative tasks |
| ABB IRB 4600-60 | 2050 | 60 | ±0.05 | Milling, medium assembly |
| ABB IRB 6700-235 | 2650 | 235 | ±0.05 | Heavy assembly, large milling |
| KUKA KR 120 R2700 | 2701 | 120 | ±0.05 | General fabrication |
| KUKA KR 210 R3100 | 3100 | 210 | ±0.06 | Timber assembly, large components |
| Fanuc M-20iD/25 | 1831 | 25 | ±0.02 | Precision assembly, welding |
| Fanuc M-710iC/50 | 2050 | 50 | ±0.07 | General fabrication |

**Repeatability vs. Accuracy:** Repeatability (±0.03–0.08mm) = how consistently the robot returns to a taught point. Accuracy (±0.2–2.0mm) = how close it gets to a commanded Cartesian point. Accuracy is worse due to kinematic model errors and backlash. Calibration improves accuracy to ±0.2–0.5mm.

**Payload includes end effector mass.** Check both mass AND moment of inertia at the tool flange — capacity decreases with distance from J6 axis.

### End Effectors

| Effector | Application | Notes |
|---|---|---|
| Spindle (HSD, Hiteco) | Robotic milling (foam, timber, GFRP) | 1–24kW, 1k–40k RPM; needs ATC for multi-tool |
| Extruder (auger/piston) | Concrete/clay/polymer printing | Temperature-controlled for thermoplastics |
| Gripper (parallel/vacuum) | Pick-and-place: bricks, panels, timber | Vacuum for flat panels; mechanical for irregular |
| Hot-wire cutter | EPS/XPS foam cutting | Wire temp 200–400°C; smooth foam surfaces |
| Welding torch (MIG/MAG) | WAAM steel nodes, structural welding | Fronius CMT preferred for WAAM |
| **OnRobot RG6** *(primary stack)* | Collaborative gripping; adaptive fingers | ±0.1mm repeatability; 0–160mm stroke |

### Grasshopper Plugins (Multi-Brand)

**HAL Robotics** (multi-brand — ABB, KUKA, UR, Fanuc, Staubli):
- Procedure + Target + Solver components in GH
- Inverse kinematics, collision detection, singularity checking
- Exports to RAPID, KRL, URScript, and others
- Real-time control mode for adaptive fabrication

**KUKA|prc** (KUKA-specific):
- LIN / PTP / CIRC / SPLINE motion commands
- I/O control for end effectors; SRC/DAT file generation
- Virtual 7th axis (linear track) support

**Robots by Visose** (open-source, multi-brand):
- Supports ABB, KUKA, UR, Fanuc, Staubli
- Robot cell → target generation → simulation → native code
- Flexible architecture; good for research and teaching

### Motion Types (All Brands)

| Motion | Path | Use |
|---|---|---|
| PTP / MoveJ / movej | Joint space; not straight line in Cartesian | Large repositioning moves |
| LIN / MoveL / movel | Straight line in Cartesian | All fabrication operations |
| CIRC / MoveC / movec | Arc through via point | Circular toolpaths |
| SPLINE | Smooth continuous | Extrusion, painting, continuous processes |

**Singularity types:** Overhead (J5=0), Extended (full reach), Base (TCP above J1). Avoid by: offsetting tool orientation ≠ 0° at J5, limiting workspace from full extension, using PTP through singular zones.

### Coordinate Systems

- **World** — fixed workcell reference; all frames reference this
- **Base** — origin at J1; differs from World if robot is on a track
- **TCP (Tool)** — active end-effector point; must be calibrated precisely
- **Workpiece / Work Object** — part coordinate system; defined by 3-point touch-up on physical workpiece
- **User Frame** — arbitrary reference for organizing targets across multiple workpieces

### Native Robot Languages

**URScript (UR10e — primary stack):**
```python
def main():
  set_tcp(p[0, 0, 0.200, 0, 0, 0])          # TCP 200mm from flange
  movej([0,-1.57,1.57,-1.57,-1.57,0], a=1.0, v=0.5)   # home
  movel(p[0.5, 0.0, 0.3, 0, 3.14, 0], a=0.5, v=0.2)   # approach
  movel(p[0.5, 0.1, 0.05, 0, 3.14, 0], a=0.3, v=0.1)  # fab start
  movel(p[0.6, 0.1, 0.05, 0, 3.14, 0], a=0.3, v=0.1)  # fab end
  movel(p[0.5, 0.0, 0.3, 0, 3.14, 0], a=0.5, v=0.2)   # retract
  movej([0,-1.57,1.57,-1.57,-1.57,0], a=1.0, v=0.5)   # home
end
# p[x,y,z,rx,ry,rz] in meters + axis-angle radians
# a = acceleration (m/s²), v = velocity (m/s)
```

**RAPID (ABB):**
```rapid
PROC main()
  MoveJ pHome, v1000, z50, myTool;
  MoveL pApproach, v500, z10, myTool \WObj:=myWobj;
  MoveL p1, v100, fine, myTool \WObj:=myWobj;  ! fine = stop exactly
  MoveL p2, v100, fine, myTool \WObj:=myWobj;
  MoveL pApproach, v500, z10, myTool \WObj:=myWobj;
  MoveJ pHome, v1000, z50, myTool;
ENDPROC
! v100 = velocity mm/s | z10 = blend radius mm
```

**KRL (KUKA):**
```krl
DEF main()
  $TOOL = TOOL_DATA[1]
  $BASE = BASE_DATA[1]
  $VEL.CP = 0.5   ; m/s Cartesian
  PTP HOME
  LIN {X 500, Y 0,   Z 200, A 0, B 90, C 0}
  LIN {X 500, Y 100, Z 50,  A 0, B 90, C 0} C_DIS  ; C_DIS = blend
  LIN {X 600, Y 100, Z 50,  A 0, B 90, C 0} C_DIS
  LIN {X 500, Y 0,   Z 200, A 0, B 90, C 0}
  PTP HOME
END
```

### AEC Robotic Applications

| Application | Brands Used | Notes |
|---|---|---|
| Robotic milling (foam, timber) | KUKA, ABB | Extended reach; high payload for spindle |
| Collaborative assembly | UR10e, UR16e | ISO/TS 15066 force limits; no fencing required |
| Concrete/clay printing | ABB, KUKA, custom | Extruder end effector; path = Grasshopper contour |
| WAAM steel nodes | Fanuc, ABB | Fronius CMT torch; wire feedstock |
| Bricklaying | UR, KUKA | Vacuum or mechanical gripper; adhesive dispenser |
| Hot-wire foam cutting | UR, custom | Wire on 2-point frame; ruled surface toolpaths |
| Fiber winding | KUKA, ABB | ICD/ITKE pavilion method; anchor-to-anchor paths |

### File-to-Factory Pipeline

```
Grasshopper geometry (toolpath curves)
       ↓
Target frames (Plane per point: position + normal = TCP orientation)
       ↓
Robot plugin (HAL / KUKA|prc / Robots): IK solve + collision check
       ↓
Simulate in GH (verify reach, singularities, joint limits)
       ↓
Export native code (URScript / RAPID / KRL / Fanuc TP)
       ↓
Upload to controller (TCP/IP network for UR; FTP/USB for KUKA/ABB)
       ↓
Air-cut dry run → scrap trial → production
```

### Pre-Flight Checklist

Before running any robot program:
1. Geometry verified in simulation — no collisions, no singularities
2. TCP calibrated and matches program definition
3. Workpiece zeroed — touch-up on physical workpiece matches workobject definition
4. Payload set in controller — mass + center of gravity
5. Velocity limited for first run (25–50% of programmed speed)
6. Safety perimeter clear; E-stop accessible
7. Dry run at reduced speed with spindle/effector off
8. First article on scrap material before production run

**For UR10e ROS2/ur_rtde integration** → see `robotics-in-architecture` skill.

---

## Skill 11 — ML for AEC

**Energy prediction surrogate:**
```python
import xgboost as xgb
# Features: orientation, WWR, floor count, U-value, SHGC → Target: EUI
model = xgb.XGBRegressor(n_estimators=500, max_depth=6, learning_rate=0.05)
model.fit(X_train, y_train)
# R² > 0.95 typical | 20min EnergyPlus → <1ms
```

**SAM / GroundedSAM for construction CV:** zero-shot segmentation; text prompt → mask; no training data required.

**LLM task planning for robotic assembly:** Claude/GPT-4 as task planner → JSON-schema-validated action sequence → ROS2 action server. Constraint checking before dispatch. See `robotics-in-architecture` skill for execution layer.

**PointNet++ for scan-to-BIM:** (N,3) XYZ → per-point labels (wall/floor/ceiling/column). Framework: Open3D + PyTorch3D. Training: S3DIS, ScanNet.

---

## Skill 12 — Optimization Methods

| Problem | Algorithm | Tool |
|---|---|---|
| Single-objective smooth | BFGS / L-BFGS | SciPy |
| Single-objective discontinuous | Simulated Annealing | Custom Python |
| Multi-objective AEC 2–4 obj | NSGA-II | Octopus, Wallacei, pymoo |
| Surrogate-assisted | Bayesian Optimization | Opossum (GH) |
| Topology | SIMP | Millipede, Ameba |

```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
import numpy as np

class BuildingOpt(Problem):
    def __init__(self):
        super().__init__(n_var=5, n_obj=3, n_constr=2,
                         xl=[0.2,10,0.1,0,0], xu=[0.8,50,0.9,1,1])
    def _evaluate(self, X, out, *args, **kwargs):
        out["F"] = np.column_stack([
            self.energy(X), -self.daylight(X), self.cost(X)])
        out["G"] = np.column_stack([X[:,1]/1000-2.5, X[:,0]-0.7])
```

---

## Skill 13 — Interoperability

**Rhino → Revit (ranked by fidelity):**
1. Rhino.Inside.Revit — live GH inside Revit; full bidirectional
2. Speckle — version-controlled geometry streams; multi-platform
3. Direct Rhino Importer — geometry only; quick one-way
4. IFC roundtrip — full BIM data, some geometry degradation
5. DXF/DWG — last resort

| Format | NURBS | BIM Data | Open |
|---|---|---|---|
| .ifc | Solid/mesh | Full | Yes |
| .step | Yes | No | Yes |
| .3dm | Full | No | No |
| .glb | Mesh | No | Yes |
| gbXML | Box | Thermal | Yes |

---

## Skill 14 — Mesh Processing

**Subdivision:** Catmull-Clark (quad → smooth, organic facade), Loop (triangle → C², structural), Butterfly (triangle → interpolating, data-accurate).

**Half-edge structure:** O(1) neighbor traversal, boundary detection, edge collapse. Use `libigl` (Python) or `Trimesh`.

**Mesh quality targets for FEA:** aspect ratio <5, minimum angle >20°, Jacobian >0, no non-manifold edges, no self-intersections.

---

## Skill 15 — Data-Driven Design

**GIS (Grasshopper):** `Elk` (OSM: roads, buildings) + `Heron` (raster GIS, shapefiles, WMS). Set `Rhino EarthAnchorPoint` for correct CRS projection.

**Space syntax:** integration = global connectivity (high = public); choice = movement attractor (many shortest paths pass through). Tools: DepthmapX, `Decoding Spaces` GH plugin, custom Python with NetworkX.

---

## Skill 16 — Design Automation

**Rule-based space planning:** `python-constraint` or `OR-Tools`. Rooms as nodes, adjacency requirements as hard constraints, solve for valid layout.

**Drawing automation (Rhino):** `rs.AddLayout()` → `rs.AddDetail()` → `rs.DetailScale()` → `rs.SetDetailLock(detail, True)`.

---

## Anti-Pattern Catalog

| # | Anti-Pattern | Symptom | Remedy |
|---|---|---|---|
| 1 | Over-parametrization | 50+ sliders, chaotic | Min viable params; sensitivity analysis |
| 2 | Black-box optimization | Accept first solver result | Colibri/Design Explorer; re-run multiple seeds |
| 3 | Geometry without structure | Can't be built | Karamba3D from day 1 |
| 4 | Fabrication ignored | Thousands of unique panels | Rationalize early; max-N-unique as design constraint |
| 5 | Data tree mismatch | Nulls, wrong counts, geometry in wrong place | Param Viewer everywhere; deliberate Graft/Flatten |
| 6 | Hot-climate generic benchmarks | Passive House targets in Riyadh | ASHRAE 90.1 + local EPW; recalibrate all metrics |
| 7 | GNN with absolute coordinates | Model fails on unseen buildings | Normalize features; use relative/topological |
| 8 | IFC graph without edge types | Lost structural/spatial semantics | HeteroData in PyG; typed edges are essential |
| 9 | Tool-driven design | Everything is Voronoi | Start with design question, not tool capability |
| 10 | Undocumented definitions | Only author can use it | Group, color-code, label all inputs with ranges |

---

## Pioneers

| Pioneer | Domain | Key Contribution |
|---|---|---|
| Frei Otto | Form-finding | Soap film minimal surfaces; Munich Olympic Stadium |
| Greg Lynn | Morphogenesis | Animate Form; NURBS blob architecture |
| Achim Menges | Material Computation | ICD/ITKE pavilions; robotic fabrication |
| Philippe Block | Form-finding | Thrust Network Analysis; COMPAS; masonry vaults |
| Caitlin Mueller | Structural ML | Digital Structures MIT; ML + structural optimization |
| Helmut Pottmann | Geometry | Architectural geometry; discrete differential geometry |
| Neri Oxman | Bio-design | Material ecology; multi-material 3D printing |
| Skylar Tibbits | Self-assembly | 4D printing; programmable materials |

---

## Tool Ecosystem

| Category | Tools |
|---|---|
| Parametric | Grasshopper (Rhino), Dynamo (Revit), Houdini |
| Environmental | Ladybug, Honeybee, Butterfly, Dragonfly, ClimateStudio |
| Structural | Karamba3D, Kangaroo, Millipede, Ameba |
| GraphML / GNN | PyTorch Geometric, DGL, NetworkX, TopologicPy |
| BIM / IFC | Revit API, pyRevit, IfcOpenShell |
| Optimization | Galapagos, Octopus, Wallacei, pymoo, Opossum |
| Interoperability | Speckle, Rhino.Inside.Revit, COMPAS |
| CV / ML | SAM, GroundedSAM, Open3D, PyTorch3D, XGBoost |
| Robotics | → See robotics-in-architecture skill |

---

## Reference Files

| File | Contents |
|---|---|
| `references/gh-component-index.md` | 200+ Grasshopper components, input/output signatures |
| `references/fabrication-specs.md` | CNC, laser, robotic tolerances and process parameters |
| `references/environmental-benchmarks.md` | Daylight, energy, wind, thermal thresholds (hot-arid context) |
| `references/structural-rules-of-thumb.md` | Span/depth ratios, load cases, material strengths |
| `references/scripting-patterns.md` | GhPython, RhinoCommon, pyRevit code patterns |

---

*Base: Amanbh997/Claude-skills-for-Computational-Designers (MIT). Extended for GraphML, Topologic, Grasshopper teaching, hot-arid climate and robotic fabrication. Examples use Riyadh climate data as a sample hot-arid site.*
