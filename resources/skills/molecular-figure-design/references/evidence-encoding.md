# Encoding evidence grade

The thing an icon library cannot do, and the reason to generate figures as code.

A pathway diagram makes every arrow look equally true. A mechanism demonstrated
by loss- and gain-of-function in vivo gets the same arrow as a correlation from
an expression cohort, and the same arrow as something the authors think is
probably happening. Readers cannot tell them apart, and the field inherits a
picture more confident than its evidence.

Fix it by making epistemic status a visual property.

## The three grades

Use whatever vocabulary the paper uses. A common and defensible set:

| Grade | Line style | Meaning |
|---|---|---|
| Established | solid | loss- and gain-of-function with a phenotypic readout in vivo or in patient-derived models |
| Association | dashed | derived from expression cohorts or correlative data |
| Inference | dotted, optionally with an open arrowhead | mechanistically plausible, not demonstrated causally in the system under discussion |

Put the definitions in the key, not just the labels. "Inference" on its own
means nothing; "not demonstrated causally in vivo" is a claim a reader can check.

## Implementation

Grade belongs in the content module, next to the claim:

```python
BRANCHES = [
    dict(key="carbonyl", isoform="...", grade="established", ...),
    dict(key="retinoid", isoform="...", grade="inference", ...),
]

GRADE_STYLE = {
    "established": dict(ls="solid",  label="Established",
                        note="loss- and gain-of-function, phenotype in vivo"),
    "association": dict(ls="dashed", label="Association",
                        note="derived from expression cohorts"),
    "inference":   dict(ls="dotted", label="Inference",
                        note="not demonstrated causally in vivo"),
}
```

The drawing code then never decides a grade; it looks one up. A reviewer can
read the grades without reading the plotting code, and a change of grade appears
in the diff.

Where a connector is not available to carry the style, put it on the element's
outline instead: a dashed wedge border carries the same information as a dashed
spoke, with one less line on the page.

## Pin the claims that must not drift

List the claims the source explicitly flags as unproven, as data, and treat the
list as a guard:

```python
FLAGGED_INFERENCES = [
    "X blocks differentiation by depleting Y",
    "Z activity remodels the microenvironment",
]
```

Then assert, in the build, that none of them is drawn solid. A figure that
promotes an inference to a fact is a figure that misreports the paper, and it is
exactly the kind of error that survives review because it looks tidy.

## The evidence census

Once grades are in the content module, you can count them, and the count is
often the most honest panel in the figure: a stacked bar of how many of the
mechanisms asserted here are established, associated and inferred.

Count only what the figure itself asserts, so the panel can never disagree with
the lines drawn beside it. Derive it from the same structure the drawing reads:

```python
def grade_counts():
    out = {k: 0 for k in GRADE_STYLE}
    for item in BRANCHES + PHENOTYPES + SCAFFOLD["partners"]:
        out[item["grade"]] += 1
    return out
```

## Do not fill gaps

If the source reports no quantitative value for something, draw no chart of it.
Mark the gap, name what is missing and where it would come from, and move on. A
placeholder that says "no cross-laboratory validation published" is informative;
an invented number is a fabricated result.

`panels.missing_data_note` exists for this: a dashed box stating what is absent
and which source would have to supply it.
