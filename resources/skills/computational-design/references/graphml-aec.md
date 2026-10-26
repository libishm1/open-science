# GraphML and ML for AEC

Part of the computational-design skill. Load this file only for the topic you need. The router is `SKILL.md`.

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
