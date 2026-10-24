---
card_id: <short-slug>
source: <citation key, verified DOI>
discipline: [geophysics | geostatistics | rock_mechanics | fabrication_economics | decision_theory | geometry_processing | other]
method_class: <name>
evidence_tag: [measured | lit-default | anchor]
validated_against: [measurement | reference implementation | none]
scale: <stated scale of the source>
---

# <Method name>

## Derived equations
Derive each equation from the definitions in the source. State the
assumptions each step uses. Do not paste an equation from PDF text unchecked.

## Assumptions and domain of validity

## Complexity and parallel model
- Time:
- Memory:
- Parallel model:

## Code seam (if an implementation exists)
- Interface:
- Inputs and units:
- Known numeric pitfalls:

## Pitfall checklist (run against the paper, then against any implementation)
- [ ] Units consistent across inputs.
- [ ] Tolerance chosen relative to object size, not as a fixed constant.
- [ ] Degenerate inputs handled (zero area, coincident points, empty sets).
- [ ] Ordering or sorting assumptions stated and enforced.
- [ ] Randomness seeded and recorded.
- [ ] Floating-point cancellation checked in differences of large values.

Each unchecked item is resolved, or waived with a written reason.

## Open questions
