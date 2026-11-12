# Venue and section profiles

The useful profile is `(discipline, venue, article type, section, audience, date)`. A publisher name alone is insufficient. MDPI is the publisher; Applied Sciences, Materials, Buildings and Sustainability are distinct journals. CumInCAD is an archive spanning conferences, not a single house style.

## Editing profiles

These are proposed editorial defaults, not corpus-derived frequency estimates.

| Profile | Preserve and emphasize | Avoid |
|---|---|---|
| Nature research article | Broad problem, specific gap, principal finding, bounded implication; accessible summary with technical precision in the body | Turning a tentative implication into a universal breakthrough; applying Nature's rules to every portfolio journal |
| Applied Sciences research article | Application, reproducible procedure, measured comparison, practical limits; IMRAD structure | Deleting useful method detail for conversational flow |
| Results in Engineering | Engineering problem, operating conditions, comparator, numerical result with units, constraint and applicability | Detaching an improvement percentage from its baseline or test regime |
| CAADRIA / eCAADe | Design problem, computational method, fabrication or design study, evaluation and architectural consequence | Recasting a design exploration as a controlled causal experiment |
| Clinical randomized trial | Allocation, analysis population, primary endpoint and time window, effect size and uncertainty, harms | Removing cautious wording, denominators, null results or adverse events |
| Clinical observational study | Population, design, adjustment, association, uncertainty and limitations | Replacing association with causation |
| Clinical case report | Clinical chronology, diagnostic uncertainty, intervention and outcome; applicable consent/reporting requirements | Generalizing from one case to efficacy |
| Materials / Cement and Concrete Research | Mix/composition, specimen preparation, curing, test method, distributions and mechanism evidence | Replacing technical compounds or variable names merely because they recur |
| Buildings / building performance | Geometry, climate, occupancy, boundary conditions, calibration and measured/simulated distinction | Treating simulated savings as observed performance |
| Sustainability / life-cycle assessment | Functional unit, system boundary, allocation, inventory, uncertainty and trade-offs | Removing scope conditions from environmental claims |
| Automation in Construction / Construction Robotics | Hardware/software configuration, task, baseline, tolerances, failure cases and deployment constraints | Treating a laboratory demonstration as proven site-wide performance |
| Systematic review | Search dates, eligibility, selection, risk of bias, synthesis and limitations | Using a review's title as proof it meets reporting or methodological standards |

## Current format checks

- [Nature's current guide](https://www.nature.com/nature/for-authors/formatting-guide) differs from its [September 2019 annotated summary guide](https://www.nature.com/documents/nature-summary-paragraph.pdf). The latter is useful historical evidence; the former governs current submissions.
- [Applied Sciences instructions](https://www.mdpi.com/journal/applsci/instructions) and [MDPI layout guidance](https://www.mdpi.com/authors/layout) distinguish a single-paragraph abstract from a manuscript with sections. Review and research article structures differ.
- [Materials instructions](https://www.mdpi.com/journal/materials/instructions) should be checked separately. Exact Buildings and Sustainability requirements were not independently retrieved in this pass; use their live instructions before enforcing limits.
- The [Results in Engineering author guide](https://www.sciencedirect.com/journal/results-in-engineering/publish/guide-for-authors) was access-blocked. This profile therefore makes no verified claim about its exact abstract word limit or heading requirements.
- [CAADRIA 2026 full-paper instructions](https://www.caadria2026.org/full-papers) require the event's template and title case. A general rule converting all headings to sentence case would conflict. Do not transfer that event's page limit to another year. [Publication protocol](https://caadria.org/publication-protocol/) also distinguishes review and final versions.
- [EQUATOR](https://www.equator-network.org/reporting-guidelines/) maps study designs to guidelines. Use CONSORT 2025 for current randomized-trial reporting, STROBE for observational work, CARE for case reports and PRISMA 2020 for systematic reviews, as applicable. Historical trials may follow earlier versions.

## Historical pilot

All entries below were published before 30 November 2022. This is a purposive sample, not a representative corpus or proof that no author used machine assistance. Publisher abstracts/records were inspected unless a different access level is given. Dates and version histories need pinning before any training or frequency analysis.

| Year | Venue and paper | Why include / access limit |
|---|---|---|
| 2005 | Nature: [The bipolar mitotic kinesin Eg5 moves on both microtubules that it crosslinks](https://doi.org/10.1038/nature03503) | Referenced in Nature's historical annotated summary; evidence for the summary's rhetorical progression |
| 2022 | Nature: [Aerial additive manufacturing with multiple autonomous robots](https://doi.org/10.1038/s41586-022-04988-4) | Robotics and fabrication; first-person reporting and technical compounds. Published 21 September; current page has a 2024 correction, so retrieve the original version before corpus use |
| 2021 | Communications Materials: [4D Thermomechanical metamaterials for soft microrobotics](https://doi.org/10.1038/s43246-021-00189-0) | Shows why Nature-portfolio articles need separate profiles; abstract extract only |
| 2021 | Applied Sciences: [Development of Communication Protocols between BIM Elements and 3D Concrete Printing](https://doi.org/10.3390/app11167226) | Abstract includes “This study aims to delve into this topic”; direct pre-ChatGPT counterexample to word-based authorship judgments |
| 2021 | Applied Sciences: [Additive Manufacturing in the Construction Industry: The Comparative Competitiveness of 3D Concrete Printing](https://doi.org/10.3390/app11093865) | Scenario-based comparison and practical implications |
| 2021 | Applied Sciences: [Overview of the Development of 3D-Printing Concrete: A Review](https://doi.org/10.3390/app11219822) | Review structure differs from an experimental article |
| 2021 | Applied Sciences: [Towards Phase Change Materials for Thermal Energy Storage: Classification, Improvements and Applications in the Building Sector](https://doi.org/10.3390/app11041490) | Building-energy review; classification and technical terminology |
| 2021 | Applied Sciences: [Review on the Integration of Phase Change Materials in Building Envelopes for Passive Latent Heat Storage](https://doi.org/10.3390/app11199305) | Another review example; avoid treating repeated field terms as defects |
| 2021 | Materials: [3D Concrete Printing: A Systematic Review of Rheology, Mix Designs, Mechanical, Microstructural, and Durability Characteristics](https://doi.org/10.3390/ma14143800) | Full-text sections inspected at [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8304820/); explicit organizational signposting predates ChatGPT |
| 2019 | Materials: [Material Design and Performance Evaluation of Foam Concrete for Digital Fabrication](https://doi.org/10.3390/ma12152433) | Fabrication/materials intersection; bibliographic record only |
| 2021 | Materials: [Potential Phase Change Materials in Building Wall Construction—A Review](https://doi.org/10.3390/ma14185328) | Thermal-performance terminology; abstract extract |
| 2021 | Results in Engineering: [Improving the thermal insulation and mechanical properties of concrete using Nano-SiO2](https://doi.org/10.1016/j.rineng.2021.100303) | Property-specific measurements and conditions; publisher abstract extract |
| 2022 | Results in Engineering: [Mechanical characterization of 3D printed samples under vibration: Effect of printing orientation and comparison with subtractive manufacturing](https://doi.org/10.1016/j.rineng.2022.100372) | Comparator, orientation and dynamic response; publisher abstract extract |
| 2022 | Results in Engineering: [Mechanical response of additively manufactured foam: A machine learning approach](https://doi.org/10.1016/j.rineng.2022.100801) | Institutional PDF inspected; online 26 November, close to cutoff; separate model prediction from physical measurement |
| 2019 | Cement and Concrete Research: [Digital Concrete: A Review](https://www.sciencedirect.com/science/article/pii/S0008884619303680) | Process and materials synthesis; publisher/institutional records |
| 2020 | Cement and Concrete Research: [Extrusion-based additive manufacturing with cement-based materials](https://doi.org/10.1016/j.cemconres.2020.106037) | Production steps and underlying physics; review, not a single experiment |
| 2020 | Cement and Concrete Research: [A process classification framework for defining and describing Digital Fabrication with Concrete](https://doi.org/10.1016/j.cemconres.2020.106068) | Stable field terminology should survive editing |
| 2019 | Automation in Construction: [Large-scale digital concrete construction – CONPrint3D concept for on-site, monolithic 3D-printing](https://www.sciencedirect.com/science/article/pii/S0926580519304601) | Process concept, system context and deployment scope; abstract extract |
| 2019 | Construction Robotics: [Mobile robotic fabrication beyond factory conditions](https://doi.org/10.1007/s41693-019-00020-w) | Mesh Mould wall case study; institutional record/abstract extract |
| 2019 | CAADRIA: [Robot Assisted Assembly of Steel Structures](https://publications.rwth-aachen.de/record/764579) | Institutional record verified; CumInCAD `caadria2019_453`; proceedings PDF blocked |
| 2019 | CAADRIA: [Automation Complexity – Brick by Brick](https://dev.bsl.arch.hku.hk/publications/2019/automation-complexity-brick-by-brick/) | Author-lab abstract; CumInCAD `caadria2019_478`; design/fabrication argument |
| 2021 | CAADRIA: [Automatic assembly of jointed timber structure using distributed robotic clamps](https://doi.org/10.52842/conf.caadria.2021.1.583) | Institutional record; do not infer sentence-level features from metadata |
| 2018 | eCAADe: [Robotic Materialization of Architectural Hybridity](https://research.tudelft.nl/en/publications/robotic-materialization-of-architectural-hybridity-modelling-comp/) | Institutional abstract; multi-material design framework and cases; CumInCAD `ecaade2018_437` |
| 2018 | NEJM: [Tisagenlecleucel in Children and Young Adults with B-Cell Lymphoblastic Leukemia](https://doi.org/10.1056/NEJMoa1709866) | Structured clinical abstract; single-cohort study, not randomized; preserve endpoint, population, uncertainty and harms |
| 2021 | BMJ: [Effect of dexamethasone on complications or all cause mortality after major non-cardiac surgery](https://doi.org/10.1136/bmj.n1162) | Randomized trial comparison; bibliographic/abstract record only |

Additional candidates needing primary-text retrieval before inclusion: Buildings' 2020 comparative life-cycle assessment (10.3390/buildings10120245); Sustainability's 2021 FANUC digital twin (10.3390/su131810336) and brickwork layout (10.3390/su13073905); CAADRIA's 2021 mineral-foam facade panel (10.52842/conf.caadria.2021.1.603). These are leads, not validated style samples.

## Section-sensitive example

Synthetic example, not a result from any cited paper:

> At 28 days, mean compressive strength was 42 MPa in the printed specimens and 45 MPa in the cast controls. The small sample does not establish equivalence.

An engineering results edit must preserve age, unit, comparator and the limitation. A discussion edit may explain the implication only if the source supplies it. A clinical analogue must likewise preserve denominators, time points and uncertainty. Replacing “does not establish equivalence” with “performs equally well” is a scientific error regardless of how natural it sounds.
