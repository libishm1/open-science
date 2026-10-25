# TopologicPy, building graphs and graph ML

For building topological models (rooms → Cells → CellComplex → graphs), energy models from them, ML and GNN surrogates, and teaching notebooks.

## Modelling chain

1. **Drawings to rooms.** Extract rooms from DWG or DXF (ezdxf, shapely) as clean, straight-edged polygons. Door openings are metadata, not part of room polygons. Stairs are distinct circulation cells.
2. **Topology.** Rooms become Cells; the building becomes a CellComplex at LOD1. **Never rotate drawing geometry**: keep plan north as drawn and pass the north axis to EnergyPlus.
3. **Graphs.** Build adjacency and circulation graphs through doors and stairs. Render floor by floor; the graph must lie on the floor and stay inside the building outline (check visually: a line leaving the building is a bug).
4. **Energy.** Simulate **as built** by default. Keep as-built and code-compliant (SBC) models apart and compare them as a "compliance gap"; never overwrite as-built assumptions with code values. Use Kiva for ground contact. Run door-open and door-closed variants where circulation matters.
5. **Learning.** Benchmark ML and GNN surrogates (GCN, GraphSAGE, GIN, GATv2; tabular baselines from linear models to gradient boosting) with Optuna and **grouped splits** (held-out storeys, walls or buildings). Verify the chain end to end: drawings → EnergyPlus → graph → model.

## Data hygiene

- Random splits within one object measure memorisation. Held-out object splits reveal true transfer. Check for leakage explicitly.
- Rerun competing models under the same split, metrics and timing protocol before claiming one is faster or better.
- Verify what the data encodes: quaternion order may be scalar-first in the data and `[x, y, z, w]` in TopologicPy; derive dimensions from the data, not from spacing assumptions.
- Pair R² with the target's spread, and check zoning-resolution artefacts before interpreting errors.
- Results can be non-deterministic at process level (MKL threads), not only per seed. Report multi-seed statistics.

## TopologicPy facts (check the current docs first)

- Use the latest stable `topologicpy` from pip. From 0.9, `topologic-core` is a separate package: pin both, or the first geometry call fails.
- The legacy `Graph.ShortestPath` is slow; use `TGraph` (build once, reweight with `edgeCostFunc`), pass `ontology=False` and prefer `ByMeshData`.
- `ByEdgeIndexPairs` ignores edge lengths, so routes count hops rather than distance.
- `Topology.Copy` and `ByJSONDictionary` can drop Cell dictionaries; re-attach them.
- Graph node order varies between runs: compare as sets or impose a canonical order. `ExportToCSV` ratio masks are contiguous by node id.
- Booleans can return invalid Cells: guard with `None` checks and Shell fallbacks.
- Parameter names change between versions; check the current documentation before writing calls.
- Licence: `topologicpy` is LGPL-3.0-or-later (verified on PyPI); check `topologic-core` separately.

## PyTorch Geometric notes

- Node-level training on whole graphs ignores `batch_size` (one graph per step) and logs NaN for graphs without training nodes; mask them.
- On some conda MKL builds, `import torch` before NumPy work avoids crashes on small float64 matrix products.

## Notebooks

- Follow the TopologicPy author's TDEA teaching style: imports → paths → build → `Plotly.DataByTopology` / `FigureByData` / `Show` → graph, with compact code.
- **Few notebooks, one per deliverable.** Each opens with Goal / Input / Output / Next and follows Import → Paths → steps → Draw → Export → Share.
- Heavy code lives in a small package; each notebook carries an "In software terms" note for a computer-science reader and a verification checklist for the architect.
- Keep figure previews in executed notebooks and save shareable PNGs as they run.
- Generated notebooks: **edit the builder script and re-execute; never edit the `.ipynb` directly.**
- Reproducibility: pinned requirements plus a lock file, a headless runner (nbclient), and a results check against `expected_results.json`, tested in a clean venv outside OneDrive.

## Web apps on Topologic

- Keep a demo-safe "Classic" line and develop on a separate "Next" branch and worktree; never modernise in place.
- Browser-test evidence is required for UI changes. Keep the backend's `topologicpy` and `topologic-core` pinned.
