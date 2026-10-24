# Topologic, IFC and BIM

Part of the computational-design skill. Load this file only for the topic you need. The router is `SKILL.md`.

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
