# Writing style: the calibrated academic voice

Academic writing quality depends on three things: argument quality, evidentiary accuracy and venue fit. Voice control alone is not enough.

Primary domain: AEC (architecture, engineering, construction), building performance and robotics research. Outside these domains, apply only the voice and structure rules and drop the domain conventions.

These rules apply to any document written on the researcher's behalf: papers, proposals, READMEs, formal emails and statements.

## Modes

Decide the mode from the request before doing anything else. Do not mix modes unless asked.

| Mode | Trigger words | Behaviour | Output contract |
|---|---|---|---|
| **1. Draft** | write, draft, compose, create a section | Generate polished prose with the voice and structure rules | Final prose only. No inline comments, flags or tracked changes |
| **2. Edit** | edit, fix, revise, tighten, rewrite, proofread | Revise existing text with the correction rules. Preserve the intended argument | Revised text, then a change log: `[CATEGORY] original → revised (rationale)`. Omit obvious grammar fixes |
| **3. Review** | review, check, flag issues, give feedback | Diagnose; do not rewrite | Issue list only: `[CATEGORY] location: problem → suggested fix`. Priority: ARGUMENT > EVIDENCE > STRUCTURE > VOICE > GRAMMAR > CITATION |

If nothing is critical, say so and leave the text alone. The researcher does not want non-essential edits.

## Register: a journal paper, not a report

- "Academic writing style, not a report." The text must read as a journal paper, never as a lab log or progress report.
- Use formal findings language: "The results indicate that…", "The analysis revealed that…". Never chronological or internal wording: "we then ran another test", "the test worked", "the pilot found".
- Keep **connective tissue** between paragraphs and sections, and **no figure dump**: every figure and table is introduced and discussed in the prose.
- Preserve the balance between readability and academic coherence.
- Do not use the phrase "this subsection". One opening sentence without it is fine.

## Voice

1. **Short declarative sentences.** Anchor at 12 to 20 words. Longer sentences are fine when subordinate clauses carry essential technical detail. A tendency, not a ceiling.
2. **Confident delivery with bounded uncertainty.** State claims directly. Replace lazy hedges ("it could be argued that", "this might suggest") with explicit bounds.
   - Avoid: "It could be argued that the method improves efficiency."
   - Prefer: "The method improved efficiency by 23% under the tested conditions; generalisation to production loads remains unverified."
   - Keep legitimate caution: "Results suggest a correlation (r = 0.67, p < 0.05), though the sample size limits generalisability."
3. **"X, specifically Y" narrowing.** Introduce a broad concept, then narrow it at once: "Graph-based representations, specifically adjacency matrices encoding room connectivity, enable…"
4. **Frame contributions inside a larger narrative.** Open with the problem a method solves; close with what it enables next.
5. **Systems-thinking decomposition.** Decompose complex systems, name each subsystem and show the integration points.
6. **Restatement for emphasis**, at most once per major section and only in the Introduction or Discussion. Never in Methods or Results, or in journals with a conservative house style.

## Strongly avoid (rewrite on sight unless the researcher chose the phrasing)

- **Em dashes, anywhere**, including emails. Use full stops, semicolons, colons or commas. Guard it in builds: `assert body.count(chr(0x2014)) == 0`.
- **Bold sentences in body text.** Keep body text regular.
- "it is worth noting that", "it should be noted that": delete the wrapper, keep the content.
- "in order to" → "to"; "utilise" → "use"; "leverage" as a verb → "use", "exploit" or "apply".
- "novel" without substantiation: say what is new. "State-of-the-art" without a citation or benchmark: name the benchmark.
- "validated" without an experiment: use "verified", "numerically verified", "checked against manufacturer datasheets" or "calibrated" (see [claims below](#claims-and-rigour)).
- "generalisable", "universality holds", "transfers beyond our dataset".

## Context-dependent (flag in Review; rewrite in Edit only if clearly better)

- "methodology" is acceptable for the study of methods or a named framework.
- Rhetorical questions are acceptable in some design-research venues.
- Passive voice outside Methods is acceptable when the agent is irrelevant.

## Venue and supervisor switches (confirm per paper)

| Switch | Default | Notes |
|---|---|---|
| Person | Third person ("This study computed…") | Use "we" only if the venue and supervisor allow it. For a single-author paper, never "we". |
| Spelling | Follow the venue; UK spelling when unspecified | Add a guard; later edits silently regress a spelling pass. |
| Citation style | The venue's style | See [citations](#citations). |
| Word, abstract, float and reference limits | The venue's guide for authors | Measure, never assume. See [venues.md](venues.md). |

## Correction rules (Edit mode; flag in Review mode)

**Grammar and style**
- Comma splices → full stop or semicolon.
- Fragments → complete sentences in body text (fragments are fine in captions and table notes).
- Passive voice in Methods → active, unless the agent is genuinely irrelevant ("Samples were cured at 60 °C for 24 h").
- One capitalisation convention. Define acronyms on first use.

**Evidence and accuracy** (flag; never change technical claims without a source or confirmation)
- Uncontextualised metrics: ask "relative to what?"
- Claims needing a citation or data that have neither. Never invent citations; mark `[citation needed]`.
- "NP-hard" used rhetorically: suggest "computationally expensive" unless a reduction is cited.
- Sustainability claims without a number or citation.
- Limitations framed as apologies: reframe as bounded scope. "This study did not validate X" → "Validation was bounded to Y; extending it to X requires [specific next step]."

**Do not touch**
- Quoted material.
- Technical claims without evidence: flag, never swap the researcher's terminology for a plausible alternative.
- Intentional caution: never strengthen a claim the researcher hedged deliberately.
- Chosen domain terms (if the paper is about ROS1, keep ROS1).
- Venue-specific formatting the researcher stated.
- Mathematical notation and formal definitions: flag suspected errors, do not rewrite.
- A supervisor's own prose: do not make extensive changes to it.

## Precedence

1. The researcher's explicit instruction.
2. The target venue's conventions.
3. Technical accuracy over style. Never trade precision for brevity.
4. Argument clarity over sentence length.
5. Voice preferences, last.

## Claims and rigour

- **Hypotheses** are stated once, near the end of the Introduction, and **never rewritten to match the results**. Report failed or partial predictions openly. Do not structure Results as H1/H2; an optional hypothesis-outcome table belongs in the Discussion.
- **Results** present observed patterns and numbers. **Discussion** gives meaning and prior work. **Methods** are procedural: no result-derived thresholds stated as if assumed in advance, no hypothesis language.
- **Thresholds are empirical** for the tested system, never universal laws.
- **Soften generalisation without deleting it.**
- **Verification is not validation.** Distinguish verification (solved correctly), validation (reproduces measured behaviour of the same quantity) and corroboration (consistent with observations of a related quantity), and say why full validation is not attainable when it is not.
- Lead with the negative result when the data says so. Do not credit a mechanism the controls do not support.
- Always pair R² with the spread of the target, and name the target quantity correctly (peak design load is not energy demand).
- Make the novelty claim very clear, positioned where others stopped. Titles: prefer investigative wording ("Investigating…") over a title that states the result, unless the venue prefers otherwise.
- Separate the study's own inference from a cited paper's finding. Tier claims as established fact, working assumption or speculative.
- Make unit conversions and pricing assumptions explicit wherever a quantity changes units.

## Section conventions (IMRaD defaults for AEC and robotics venues)

**Introduction.** Problem (1 to 2 sentences, no grand openings about "the rapid advancement of technology") → context (present tense) → gap ("No existing work addresses X in the context of Y" beats "limited research exists") → contribution ("This paper presents…", not "This paper aims to…") → paper structure only if non-obvious. Every claim is cited or follows from cited work. If the gap and the contribution do not connect, one of them is wrong. Do not preview results unless the venue expects it.

**Methods.** An overview paragraph from which a reader understands the whole architecture; subsystems with inputs, steps, outputs and parameters; integration (data flow, interfaces, timing); implementation details with versions ("Python 3.11, EnergyPlus 25.2", not "Python"). Past tense for completed actions; present tense for definitions that remain true. Justify every parameter, and say when it was chosen empirically ("α = 0.01 from a grid search over {0.001, 0.01, 0.1}"). Robotic systems: joint configuration, TCP offset, payload, communication protocol, safety limits. Grasshopper: the component chain, plugin names and versions; for custom C# or Python, describe the logic. Reproducibility test: could someone replicate it from the text?

**Results.** One or two sentences recapping the setup; quantitative results with tables and figures first; comparisons on the same metrics as the baselines, with significance; then qualitative observations. Contextualise every metric. Do not interpret. Column headers carry units; give standard deviations or confidence intervals. Figures are referenced before they appear; captions are self-contained.

**Discussion.** Synthesise the key findings (do not copy Results); interpret against prior work ("Unlike [Author, Year], who reported X under Y, these results show Z, likely because…"); implications for the field and for practice; limitations as bounded scope, each with a concrete extension, and not overlong; concrete future work, never "further research is needed". Address every research question. No new data.

**Literature review.** Synthesise by theme, never chronologically or paper by paper. Three to six thematic sections, each ending with a synthesis statement and the remaining gap, then a gap map. Present tense for established findings; past tense for specific experimental results. Every citation earns its place.

**PRISMA layer.** Exact search strings, databases, date ranges and hits per database; a flow diagram with exact counts; binary-testable criteria; screener roles and inter-rater reliability; a standard extraction form; a quality tool where relevant. For graph ML in AEC, the "Bridge to GNN" rule: include papers that bridge toward GNN/GML by establishing graph data representations or providing core graph ML methodology adopted by AEC researchers; exclude pure space syntax, pure ontology and pure algorithmic graph theory without an ML connection, even under relaxed criteria.

**Abstract.** Context → gap → method → results → implication, 150 to 250 words (or the venue limit). No citations, no undefined acronyms (BIM, GNN and AEC are fine), every sentence carrying unique information.

## Citations

Follow the target venue's style: numbered by first appearance for Elsevier numbered styles, ISO-4 journal abbreviations for MDPI, author-date where the venue uses it. With no venue stated, use author-date and ask.

- Author-date forms: two authors "(Smith and Jones, 2023)", three or more "(Smith et al., 2023)", several citations separated by semicolons in chronological order. (Strict Chicago omits the comma: "(Smith 2023)". Confirm which form the venue wants.)
- Same author and year: 2023a, 2023b, assigned alphabetically by title, checked against the full reference list.
- Institutional authors: "(National Institute of Standards and Technology [NIST], 2022)", then "(NIST, 2022)".
- Article titles in sentence case; journal titles in title case. DOIs as full URLs (`https://doi.org/…`) with no trailing full stop.
- **Build reference lists from verified Crossref records, not by hand.** Verify every DOI with Crossref and at least one other API (see [literature-review.md](literature-review.md)).
- Every in-text citation appears in the reference list and vice versa. Strip AI artefacts from reference lists. Uncited references are a liability; a reference ceiling set by the supervisor wins.
- Duplicates: remove exact duplicates; keep the journal version over the conference version unless the conference version has unique content; keep the published version over the preprint.
- Common errors: "et al." with fewer than three authors, missing years, text and list mismatches, inconsistent names or abbreviations, missing issue numbers, a DOI resolving to the wrong paper, proceedings missing location or publisher.

## Responding to reviewers and co-authors

- Non-defensive tone. "Section 4.5 already showed that…" becomes "We appreciate this point. Section 4.5 has been clarified to show that…".
- Neutralise absolute claims ("strengthened, not weakened", "cannot reorder").
- Close by stressing scientific robustness and transparency, not machine verification.
- Supervisor comments carry about 70% weight: use judgement and research for each one, push back with data where readability or academic integrity requires it, and record the decision. See [manuscript-engineering.md](manuscript-engineering.md).

## Domain context (verify before citing)

- Robotic hardware: UR10e with an OnRobot RG6 gripper. Verify payload, reach and protocol specifications against the Universal Robots and OnRobot datasheets before citing them.
- Software: ROS2 (rclpy, ros2 launch, ros2_control) unless the paper is about ROS1.
- Building performance: EnergyPlus, OpenStudio, Ladybug Tools (Honeybee, Dragonfly), Radiance, Urban Weather Generator; Saudi Building Code (SBC 601/602) and ASHRAE 90.1/62.1/140 for code-compliant baselines.
- Computational design: Rhino and Grasshopper, TopologicPy, COMPAS.
