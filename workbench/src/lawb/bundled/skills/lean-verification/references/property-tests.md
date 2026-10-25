# Property tests that mirror proofs

Part of the lean-verification skill. Load this file when turning a proven invariant into a test.

## Pattern

One invariant, one test, real code, generated inputs:

1. Name the theorem and quote its statement in the test's comment.
2. Generate inputs that satisfy the theorem's hypotheses. Inputs outside them prove nothing.
3. Call the shipping function, not a copy of it.
4. Assert the invariant with a tolerance chosen from the problem's scale.
5. Keep the seed of every failing case, so it can be replayed.

## C# with CsCheck

```csharp
// Theorem: packed items never overlap (no_overlap).
[Fact]
public void PackedItemsNeverOverlap() =>
    Gen.Select(ItemGen.Array[1, 40], ContainerGen)
       .Sample((items, container) =>
       {
           var placed = Packer.Pack(items, container);      // the real code
           return Geometry.PairwiseDisjoint(placed, tol: 1e-9 * container.Diagonal);
       });
```

## Python with Hypothesis

```python
# Theorem: the objective never increases across iterations (monotone_objective).
from hypothesis import given, strategies as st

@given(st.lists(st.floats(0.1, 10.0), min_size=1, max_size=50))
def test_objective_is_monotone(values):
    trace = optimiser.run(values)                   # the real code
    assert all(b <= a + 1e-12 for a, b in zip(trace, trace[1:]))
```

## Triage

| Failure | Meaning | Action |
|---|---|---|
| Counterexample with valid inputs | The code does not implement the algorithm | Fix the code; add the case as a regression test |
| Counterexample with invalid inputs | The generator ignores a hypothesis | Fix the generator |
| Passes, but the property is weaker than the theorem | Specification gap | Strengthen the property or document the gap |

## Dafny escalation

When one kernel carries the most risk (for example a geometric predicate that every other
component trusts), write it in Dafny with its pre- and postconditions, verify it, and compare its
outputs with the shipping code on the same generated inputs.
