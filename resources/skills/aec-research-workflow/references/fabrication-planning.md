# Digital fabrication research: experimental plans and print simulation

For 3D printing with earth, cob, geopolymers or concrete on a lab construction printer, and for the simulation work that supports it.

## Experimental planning

1. **Ground the plan in the actual hardware.** Read the printer's manuals and checklists: pump type (progressive-cavity versus auger), aggregate size limits, hose length, nozzle diameter, flow rates. Correct any assumption the researcher flags immediately.
2. **Map the supply chain.** A desktop market study with validated links, then B2B marketplaces and primary suppliers. Draft a bilingual RFQ where suppliers are local (for example Arabic and English) and state procurement quantities. Buy soil in a single batch so the material stays consistent. Local supplier listings are often not crawlable by US-oriented search; use a local-language query kit.
3. **Design experiments baseline-first.** Start with the simplest mix (earth + water + fibre), then add components one at a time (lime, then biopolymers or other stabilisers). Use a statistical design (for example an L9 orthogonal array plus a baseline), fresh-state tests the lab actually has (slump and flow table, syringe extrusion), and explicit decision gates.
4. **Review the plan independently.** Separate agents check the statistics, consistency with the manuals and lab feasibility. Incorporate expert comments as a new version (v2.x, v3.x), never in place.
5. **Communicate.** A concept one-pager image, a short email to the team, and ELI5 or spoken scripts for presenting to specialists.

## Primary-source discipline (from an expert review)

- Verify every extracted number against the primary source. Mix proportions must sum to 100%; one draft combined figures from two different recipes.
- Every in-text citation must appear in the reference list.
- Do not call a line "unsourced" without checking.
- Separate the study's own inference from a cited paper's finding.
- Use professional terminology, never casual terms (a "fussy pump" is a progressive-cavity pump).
- Reduce reliance on AI-generated content for literature extraction, numbers and technical diagrams; label any generic render as illustrative.
- User-supplied spreadsheets may contain implausible rows; check them against sources before using them as model inputs.

## Simulation before printing

- **Literature corpus.** Records follow a per-paper schema ([`../templates/`](../templates/)): equations as LaTeX, sympy and SI units; parameters with source location; figure points; author-stated and simulation-relevant limitations. Deduplicate by DOI and re-check every DOI against Crossref with a fuzzy title match. Check equation dimensions (PASS / EMPIRICAL / SKIP / FAIL). Flag abstract-only records: read the full text before using their numbers.
- **Registers.** An assumption register (STRONG / PARTIAL / NONE literature support) and a test register linking literature, tests and acceptance criteria. The build fails on any unknown paper id. Never hand-edit generated files.
- **Analytical prescreen** with a simple 1-D reference model before any FE or CFD.
- **G-code and buildability.** Parse the G-code; run FE layer-activation buildability and buckling (for example scikit-fem, large-displacement FE); prepare OpenFOAM VOF cases for extrusion flow on a separate simulation machine (WSL2 where needed).
- **Calibrate against real evidence.** Use photo and video timestamps of real prints rather than nominal G-code timing, and record which bounds depend on that assumption. Show the original printed object or real photos where they exist.
- **Explore the design space** (Pareto fronts across mix, layer height, print speed).
- Check arithmetic formally (Lean 4 or sympy), verify DOIs, and hand off to the simulation machine with a `00_HANDOFF.md` covering setup, rebuild order and first tasks.
