# Anti-patterns, pioneers, tools and reference files

Part of the computational-design skill. Load this file only for the topic you need. The router is `SKILL.md`.

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
