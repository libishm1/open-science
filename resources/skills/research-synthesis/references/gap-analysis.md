# Gap analysis procedure

Purpose: turn a synthesis into a ranked list of gaps that a reviewer can
check. A gap is a claim the evidence does not yet support. This file does not
contain gaps for any field. It is the method for finding and ranking them.

## Inputs

- T0 corpus statistics (counts by stage, discipline, year, evidence tag).
- T1 extraction cards (method, assumptions, validation status, scale).
- T2 evidence map and compatibility matrix.

## Step 1: build the gap matrix

Rows: pipeline stages or model components. Columns: disciplines or domains.
Each cell holds the number of included sources that support the stage in that
domain, and the strongest evidence tag (`measured`, `lit-default`, `anchor`).

An empty cell with a non-empty row or column is a candidate gap.

## Step 2: classify each candidate

| Type | Definition | Evidence to record |
|---|---|---|
| Unstudied combination | No source applies method A and domain B together | Search scope and count showing zero hits |
| Unmeasured parameter | The model needs a value that only appears as a default | Cards tagged `lit-default` for that parameter |
| Unvalidated method | No comparison to measurement or a reference | Cards with no validation section |
| Transfer gap | Result from one material, site or domain, not tested in the target | Source domains versus target domain |
| Scale gap | Result at one scale, none at the scale of use | Scale stated in each card |

A candidate can have more than one type. Record all of them.

## Step 3: rank

Score each gap on two scales, 1 to 3:

- **Impact.** How much the gap changes the question's answer, if closed.
- **Closability.** How much a single study would close it. High closability
  means one defined experiment or dataset would settle it.

Rank by impact first, then closability. Drop gaps with impact 1 unless
closability is 3 and the gap blocks another gap.

## Step 4: verify before reporting

For each ranked gap:

1. Re-run the search for the gap's scope. Record the query and date.
2. If the search finds a source, the gap is not a gap. Move it to T2 as an
   addressed item and cite the source.
3. Record the search class (P5). A rapid map cannot prove absence. Write
   "no source found in [scope] as of [date]", not "no work exists".

## Step 5: write the gap entry

```
Gap: <one sentence>
Type: <type from step 2>
Evidence of absence: <search scope, query, date, count>
Cards that show it: <card ids>
Impact / Closability: <1-3> / <1-3>
Closing study: <one defined experiment, dataset or comparison>
Status: open | addressed by <source> | dropped (reason)
```

## Common errors

- **Absence from the wrong search.** A gap claimed from one database. Search
  at least two engines for the scope.
- **Gap that is a limitation.** "The sample was small" is a limitation of one
  paper, not a gap in the field. Only report it as a gap if no source covers
  the case.
- **Novelty by omission.** Stating a method is new without a search. Attach
  the scope or drop the word.
