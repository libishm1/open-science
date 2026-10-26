# Optimization and mesh processing

Part of the computational-design skill. Load this file only for the topic you need. The router is `SKILL.md`.

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

## Skill 14 — Mesh Processing

**Subdivision:** Catmull-Clark (quad → smooth, organic facade), Loop (triangle → C², structural), Butterfly (triangle → interpolating, data-accurate).

**Half-edge structure:** O(1) neighbor traversal, boundary detection, edge collapse. Use `libigl` (Python) or `Trimesh`.

**Mesh quality targets for FEA:** aspect ratio <5, minimum angle >20°, Jacobian >0, no non-manifold edges, no self-intersections.

---
