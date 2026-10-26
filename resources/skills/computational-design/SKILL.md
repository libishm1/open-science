---
name: computational-design
description: Use this skill for any question about computational design, parametric modeling (Grasshopper, Dynamo, sliders, data trees, GH definition, teaching Grasshopper, student errors), generative design (evolutionary algorithms, Galapagos, Octopus, Wallacei, NSGA-II, fitness functions), GraphML for AEC (graph neural networks, GNN, heterogeneous graphs, IFC as graph, message passing, node classification, link prediction, GraphML, GML, DGCNN, graph machine learning, Bridge to GNN, Categories A-D, PRISMA systematic review AEC), Topologic (TopologicPy, IFC cell complex, spatial topology, fire egress, shortest path, face adjacency, CellComplex), algorithmic patterns (tessellation, L-systems, Voronoi, Penrose, Islamic geometry), structural computation (Karamba3D, Kangaroo, form-finding, FEA, topology optimization), environmental simulation in hot-arid climate (Ladybug, Honeybee, solar, daylight, EnergyPlus, Riyadh, Gulf, ASHRAE), facade computation (panelization, rationalization, curtain wall, kinetic facades), digital fabrication (CNC, 3D printing, laser cutting), BIM scripting (Revit API, pyRevit, IFC, IfcOpenShell), interoperability (Speckle, Rhino.Inside, IFC pipelines), scripting (GhPython, RhinoCommon, C# Grasshopper, pyRevit), optimization, data-driven design, mesh processing, design automation, ML for AEC (GNN, GANs, CV, SAM, GroundedSAM, LLM task planning).
compatibility: Claude, Codex, local models, Ubuntu with ROS 2, Herdr and Omarchy. Rhino and Grasshopper steps need Windows or macOS (or a remote Rhino host); Python, IFC and scripting steps run on all platforms.
---

# Computational Design Skills for AEC
*Extended for: GraphML/GNN research, Topologic IFC spatial reasoning, Grasshopper teaching, hot-arid climate, robotic fabrication (UR10e stack)*

---

## Quick start (for small local models)

1. Read this file only. It is the router.
2. Find your topic in the table below.
3. Read only that reference file. Use `Read` with `offset` and `limit` if it is long.
4. Follow the steps in that section. Check the output against the section's checklist.
5. If no topic fits, read `references/catalog.md` for the tool list.

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

## Topics

| Topic | File |
|---|---|
| GraphML and ML for AEC (GNN, Bridge-to-GNN, PRISMA, ML surrogates) | `references/graphml-aec.md` |
| Topologic, IFC and BIM scripting (CellComplex, fire egress, Revit, interoperability) | `references/topologic-ifc-bim.md` |
| Grasshopper parametric, generative and data-driven design (teaching, data trees, scripting) | `references/grasshopper-parametric.md` |
| Environmental simulation, structure and facades (hot-arid examples, FEA, panelization) | `references/environment-structure-facade.md` |
| Robotic fabrication (UR10e, ABB, KUKA, Fanuc) | `references/robotic-fabrication.md` |
| Optimization and mesh processing | `references/optimization-mesh.md` |
| Anti-patterns, pioneers, tool ecosystem, reference files | `references/catalog.md` |
| Design framing: top-down versus bottom-up design flows | `references/design-framing.md` |

The original tables of components, fabrication specs, environmental benchmarks, structural rules and scripting patterns are in the `references/` files listed under Reference Files in `references/catalog.md`.

## Platforms and orchestrators

This skill runs on Claude, Codex, local models, Herdr and Omarchy. Read
`references/platform-compatibility.md` for which steps need which operating system, how to
name paths, and how to give each agent pane its inputs.
