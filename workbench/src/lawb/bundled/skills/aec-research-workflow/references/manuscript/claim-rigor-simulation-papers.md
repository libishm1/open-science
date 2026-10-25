# Claim rigour for simulation-based papers

What separates a claim that survives review from one that does not, worked through real examples.

---

## 1. The availability trap: the highest-value check in the whole project

**Pattern:** a model uses a resource as a boundary condition. Nobody asks whether the simulated system
actually produces that resource.

**What happened.** Night ventilation of a PCM cavity used building exhaust air at a fixed,
conditioned-zone temperature as the sink, inherited from an early assumption. It drove a headline
recommendation. The office is conditioned only during occupied hours and free-floats overnight, so
its extract air is not a stream at that temperature. The model's own output: the night zone
temperature averaged far above the assumed sink temperature in summer and never reached it in any
night hour.

Re-running with the actual free-floating zone air collapsed latent throughput by more than an order
of magnitude, close to a sealed cavity. The entire recommendation was rebuilt around a dedicated
sink instead, with the fan energy accounted.

**Why nothing caught it.** It was an *input*, not a bug. Every unit test, checksum and structural check
passed. Only asking "does the model itself say this exists?" surfaces it.

**Rule.** For every boundary condition that represents a *resource* (cool air, waste heat, a sink, a
source, a schedule), extract the corresponding quantity from the simulation output and confirm it is
available in the hours you use it. State the finding in the paper even when it is negative; it is
often more interesting than the original claim.

---

## 2. Decompose before attributing

**Pattern:** a saving is credited to the mechanism the paper is about, because that is the mechanism
the paper is about.

**What happened.** PCM glazing alone produced a clear reduction in annual cooling. Presented alongside
latent-storage discussion, that reads as a latent-heat result. A **matched control** (identical
assembly, identical optical gate, latent term removed from the effective heat capacity, so phase
change is the *only* difference) split it into an optical and sensible part that carried almost all
of the saving, and a latent part that was a small fraction of it.

Roughly one twentieth of the headline was the mechanism the paper was named after.

**Rules.**
- Build the matched control as a **named case in the results table**, not a footnote.
- Confirm the decomposition holds under the other scenarios (it did: under future weather the latent
  contribution was essentially unchanged).
- Say explicitly what the number should **not** be reported as.
- Prefer two simulations over an argument. A control case ends the discussion; reasoning invites it.

---

## 3. Verification is not validation

| Claim | Requires |
|---|---|
| *validated* | physical measurement of the thing being modelled |
| *verified* | agreement with another model or a higher-fidelity run |
| *checked against datasheets* | manufacturer data for material inputs |
| *calibrated* | a fitted factor, with its anchor disclosed |

State how many levels were possible and why the rest were not. If no experiment was performed, say so
in the methods, once, plainly; it pre-empts the whole thread.

**Verify per case**, not once. A fidelity ladder demonstrated on one configuration does not license the
claim for every other configuration. Per-case re-runs replaced an inherited coupling-error range with a smaller measured
one, and the inherited figure was still sitting in the LaTeX rendition.

---

## 4. Uncertainty is what licenses a ranking

If your cases differ by a fraction of a percentage point, the ranking is meaningless unless model
uncertainty is smaller than that. Perturb what could plausibly move the answer:

- the calibration factor (±10 %)
- spatial discretisation (halve and double the node count)
- timestep (finer and coarser)

Report the **largest** shift as a single number, then say which cases are equivalent within it and stop
ranking them. Here the largest shift was larger than the spread across three cases, so those three
were declared equivalent rather than ordered.

---

## 5. Sign conventions and geometry must be derived, not assumed

A slat-angle sign convention was drawn inverted. It was caught by a domain expert's eye, then settled
by **ray-tracing the geometry numerically** and confirming the transmittance went to zero in the
deployed state. Two conventions were in play (the drawing's and ISO 15099's) with opposite signs.

**Rules.**
- When two conventions exist, define both explicitly and state which each artefact uses.
- Settle geometry disputes by computing an observable (here, direct-beam transmittance), not by
  redrawing until it looks right.
- Check that a change to a *drawing* does not imply a change to *results*, and say so explicitly when
  it does not.

---

## 6. Distinguish what the model resolves from what it approximates

Be explicit where a scalar stands in for a field:

- A one-way coupling that injects a flux does **not** resolve the glazing inner-surface temperature,
  so mean radiant temperature, and therefore comfort, carries extra uncertainty. Say that.
- A transmittance fraction standing for full slat optics is a simplification. Say what it omits.
- A morphed future weather file is suitable for trend analysis, **not** extreme-event analysis. Say that.

---

## 7. Account for what your intervention consumes

Night ventilation needs a fan. Dynamic shading needs actuators. If you report a saving without the
energy or maintenance cost of achieving it, the saving is overstated and a reviewer will say so.

---

## 8. Numbers that must always agree

Keep a short list of cross-artefact invariants and assert them mechanically. Examples from one project:

- the solar-transmittance parameter takes one fixed value for the code-compliant assembly and 1.0 for
  clear glazing; mixing them invalidates every comparison
- the sub-additivity index must equal `pcm_alone + louvre_alone − combined`
- the decomposition must satisfy `total = optical_sensible + latent`
- the naive sum shown as "not X %" must equal the two individual reductions added

These are the arithmetic a reader will do in their head. If any fails, the paper looks careless even
when the simulation is right. (One project went further and machine-checked them as theorems.)
