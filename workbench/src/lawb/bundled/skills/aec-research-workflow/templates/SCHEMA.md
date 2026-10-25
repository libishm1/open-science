# Per-paper extraction record schema (one JSON object per line in data/clusters/<cluster>.jsonl)

> Template. Replace the `<...>` placeholders and the *(example)* value lists with your review's own clusters,
> modules and categories. Keep the verification fields (`doi`, `crossref_title`, `verified_crossref`), the
> machine-checkable `equations` block (read by `scripts/check_equations.py`) and the honest `extraction_basis`.
> Check every DOI with `scripts/crossref_check.py` before recording it.

{
 "id": "short key e.g. Smith2018_JournalAbbrev",
 "doi": "10.xxxx/....  (lowercase, no https prefix); MUST resolve on api.crossref.org/works/<doi>",
 "crossref_title": "title exactly as returned by Crossref",
 "authors": "First Author; Second Author; ... (max 6, then 'et al.')",
 "year": 2018,
 "venue": "journal / conference",
 "cluster": "<cluster code, e.g. A..H>",
 "modules": ["<module 1>" | "<module 2>" | "<module 3>" | "validation" | "materials"],
 "material": "<material class 1> | <material class 2> | <material class 3> | other",
 "additives_or_variants": "none | <variant 1> | <variant 2> | ...",
 "method_type": "experimental | numerical | analytical | review | mixed",
 "method_detail": "e.g. 'FEM (<solver>) <element/activation strategy>, <constitutive model>, time-dependent parameters'; '<test> at <rate/condition>'",
 "software": "<tool 1> | <tool 2> | in-house | none | ...",
 "key_findings": "1-3 sentences, quantitative where possible",
 "equations": [
   {"name": "linear growth law (example)",
    "latex": "\tau_s(t)=\tau_{s0}+A t",
    "sympy": "tau_s = tau_s0 + A*t",
    "variables": {"tau_s": "Pa", "tau_s0": "Pa", "A": "Pa/s", "t": "s"},
    "validity": "conditions/range stated by authors"}
 ],
 "parameters": [
   {"symbol": "A", "value": 0.5, "unit": "Pa/s", "range": "0.1-2", "material": "...", "conditions": "...", "where": "Table 2 / abstract / Fig 5 text"}
 ],
 "figures_machine_readable": [
   {"figure": "Fig. 6", "x": "time [min]", "y": "<quantity> [<unit>]", "shape": "linear then exponential", "points": [[0, 0.5], [30, 2.1]], "basis": "values stated in text | read from table | approximate"}
 ],
 "limitations_stated": ["limitations the authors themselves state"],
 "limitations_for_simulation": ["limitations relevant to using this paper's model/data in OUR simulation (inferred), e.g. 'calibrated on one material class only, not transferable without re-fitting', '2D plane strain', 'isothermal', 'single process speed'"],
 "assumptions": ["modelling assumptions used (incompressible, von Mises, small strain, ...)"],
 "access": "open access URL or 'paywalled'",
 "extraction_basis": "full_text | abstract_only | abstract+secondary  (be honest)",
 "verified_crossref": true
}
