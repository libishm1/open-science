# Editorial decisions: why a paper is desk-rejected, why it is sent to review, and where novelty comes from

An editor decides in a few minutes, from the title, the abstract, the first page of the literature review and
the size of the manuscript. The science is rarely read at that stage. This file records one paper's five
editorial decisions, what changed between the four declines and the acceptance, and the method that found the
novelty that carried it: a counted map of which combinations of the field's dimensions have been studied.

## 1. Project C: four declines, then review and acceptance

A simulation paper on phase change material (PCM) envelopes across urban microclimates in a hot-arid country:
1,524 annual EnergyPlus runs, Urban Weather Generator microclimates for three urban densities, matched
inert-layer controls, a reproducibility package. Sole author, a supervisor directing the framing.

| # | Venue type | Decision | What the editor saw first |
|---|---|---|---|
| 1 | Elsevier building-energy journal | declined, transfer offered | Title naming a setup ("Urban morphology effects on ... across ... climate zones"); modest headline savings first |
| 2 | Elsevier building-science journal | declined at the desk | 11,500 words and 22 display items against a 10,000-word and 20-item ceiling |
| 3 | Elsevier open-access built-environment journal | declined, transfer offered | A 326-word abstract against a guide of about 150 |
| 4 | MDPI building journal | declined: "lacks scientific novelty" | The abstract's opening claim, which the paper's own review credited to studies from 2013 and 2023 |
| 5 | MDPI energy journal, PCM section | **sent to three reviewers, accepted after one round** | A framework in the title, a contradicted 2025 claim in the introduction, hypotheses stated, a gap table |

The fourth decline was the informative one because it gave a reason. The abstract opened "PCM envelope design
assumes the material re-solidifies overnight; across 1,524 annual simulations ... it never does", and the
literature review said of a 2023 study that it was "a finding which anticipates the present results". An editor
reading both needs no further evidence. **The paper led with the one claim it attributed to prior work**, while
four claims that no prior work made sat further down.

### What changed between decline 4 and acceptance

| Element | Declined version | Accepted version |
|---|---|---|
| Novelty anchor | "PCM never fully re-solidifies" (established in 2013 and 2023) | A specific 2025 sentence the results contradict ("only PCMs that complete a full daily charge-discharge cycle can deliver meaningful savings"), plus a new dimension (adaptive coupling) at an intersection a counted search showed empty |
| Title | Names the setup | Names the contribution: adaptive envelopes, night-time regeneration, operating limits |
| Contribution type | Parametric study with modest averages | A transferable framework: a two-bound operating window (regeneration floor set by the urban night, activation ceiling set by the cooling setpoint) with three named regimes |
| Structure | Long methods narrative | Six named methodological phases, a phase table, hypotheses stated once in the Introduction and never rewritten after the results |
| Literature review | 1,800 words, gap implied | The 2025 to 2026 state of the art added, the self-defeating sentence deleted, a gap table closing the review |
| Evidence of rigour | Present but not signposted | Verification, corroboration and validation named separately; matched controls; reproducibility package named in the cover letter |
| Venue | Novelty-gated, with word and float caps | Soundness-based review in a section on the paper's topic, no length cap |

The reviewers then asked only for rigour (independence of case-months, threshold choices, attribution, the
generality of the ceiling, the duration of the cool hours, the time scale of cycling) and the editor for shorter
sentences. Nobody questioned the novelty again. See [revision-and-response.md](revision-and-response.md).

## 2. Desk-rejection triggers, and the fix for each

| Trigger | How it shows | Fix before submitting |
|---|---|---|
| Leading claim already in the literature | Abstract's first finding matches a cited study; phrases such as "consistent with" or "anticipates" next to it | Rank the paper's claims against the review (table: claim, anticipated by?), lead with an unanticipated one |
| Title names a setup, not a finding | "Effects of X on Y across Z" | State the contribution or the framework; a finding-title if the supervisor accepts it |
| Modest numbers first | "1.4 to 4.3 % annual saving" in the first sentences | Lead with the mechanism or the inversion; put magnitudes after the claim they support |
| Over the venue's limits | Words, display items, abstract length, references | Measure against the guide for authors before choosing the venue ([submission-compliance.md](submission-compliance.md)) |
| Partly negative result at a novelty-gated venue | "No melting point achieves daily cycling" | Frame the negative as a boundary of a framework, or choose a soundness-based venue |
| Simulation only, no validation | High-impact venues desk-reject it | Separate verification, corroboration and validation and say what each establishes ([claim-rigor-simulation-papers.md](claim-rigor-simulation-papers.md)) |
| Scope mismatch | A building-energy paper sent to an urban-climate journal, or the reverse | Tilt the framing to the venue's half of the contribution, or pick the venue whose recent papers the manuscript cites |
| Gap asserted, not shown | "To the best of our knowledge ..." | A counted search and a combination map (section 4), and a gap table in the review |

## 3. Read the decision, then decide the next move

- **A decline with a transfer offer** means "out of scope or below our bar", rarely "unsound". Transfers keep
  the file but carry the framing problem with them; fix the framing first.
- **A decline that names novelty** is the most useful decision available: rank the claims (section 2) before
  anything else.
- **Two declines on editorial grounds** are a positioning signal, not a science signal. Do not add analyses;
  change the first page.
- **Sent to review** means the framing worked. Reviewer requests are then about rigour, and the revision
  should narrow claims rather than defend them.
- After each decline, write a one-page diagnosis (what the editor saw first, which trigger, what changes) and
  get the supervisor's decision on title and abstract before resubmitting. Keep the old versions.

## 4. Novelty by combination: the field map

Most defensible novelty in applied simulation research is an **intersection**: two or three established lines
of work that nobody has joined. Asserting it invites "lacks novelty"; counting it does not.

1. **Describe the field as dimensions with levels.** Technology (PCM, adaptive envelope, night ventilation, ...),
   context (urban heat island, morphology, canyon, coupled urban weather), climate, focus (regeneration,
   cycling, peak, comfort, durability), method. Template: [`templates/gap_dimensions.example.json`](../../templates/gap_dimensions.example.json).
2. **Harvest the field broadly**, not only the target journals (`scripts/harvest_openalex.py`).
3. **Code and count** with `scripts/gap_matrix.py`: densest pairs (established lines), pairs far below
   expectation, and **closure gaps**, k-way combinations with no papers although every (k-1)-way neighbour is
   well studied.
4. **Read the nearest papers** of each candidate gap (the report lists the most cited papers of every
   neighbouring pair). Project C's closest candidate was a block-scale static dual-PCM study with radiative
   cooling; reading it in full confirmed the gap and became a precise contrast sentence in the review.
5. **Choose the gap the data can fill, and say why it matters**: a gap is only novelty when an established
   claim breaks or a practical decision changes inside it.
6. **Put the count in the paper**: "Of 2,086 papers in nine journals, 147 combine PCM with adaptive control and
   six combine PCM with urban context; none combines all three." Editors and reviewers can check a number.

**Retrospective check.** Run afterwards on 4,146 envelope papers (2010 to 2026, six queries, the example
dimensions file), the map returned Project C's gap without being told about it: PCM x adaptive control x urban
morphology held 0 papers and PCM x coupled urban weather 0, while PCM x adaptive control held 53 papers (42 of
them since 2023) and PCM x urban heat island 25. The two papers in the neighbouring cells were a green-facade
wall study and an insulation review. Had the map been run before the first submission, the paper would have led
with the right claim.

Keyword coding undercounts papers that use other words, and abstracts missing from the index (common for some
publishers; 35% in that corpus) are coded on the title only. Report both, and treat every gap as a candidate
until read. A dimension must hold the axis being crossed: with "PCM" and "adaptive envelope" as two levels of
one technology dimension the decisive triple could not even be formed; control mode is its own dimension.

## 5. Mapping the lessons to the other research lines

The same triggers and the same combination method apply to every line of this lab's work. Typical dimensions
and the claim that usually sinks a first submission:

| Research line | Dimensions for the field map | Typical desk-rejection trap | Novelty anchor that works |
|---|---|---|---|
| PCM and adaptive envelopes, glazing, shading | technology x element x climate x context x focus x method | Leading with under-utilisation or "PCM saves energy" | A design rule the results invert; an operating window with named regimes |
| Urban microclimate and building energy (UWG, ENVI-met, UBEM) | coupling level x morphology descriptor x climate x building type x validation | "Urban form changes energy use" | Which descriptor governs which outcome, with the coupling verified per case |
| Future weather and climate adaptation | morphing method x scenario x building type x metric | Single scenario, single file | Robustness across ensemble members; where a design ranking flips |
| Daylight, glare and dynamic facades | facade technology x metric (sDA, UDI, DGP) x control x climate | Annual metrics only, no glare-energy trade-off | Coupled hourly states (phase state, louvre position) and the trade-off frontier |
| Earth, cob and concrete 3D printing | material x printing process x structural or thermal property x scale x climate | "We printed a wall" | A measured property relation or a design limit that transfers to other mixes |
| UR robotic fabrication, ROS 2, Grasshopper bridges | task x sensing x control architecture x material x accuracy metric | A demonstration without a benchmark | A repeatable accuracy or throughput result against a stated baseline |
| TopologicPy, building graphs, GNN surrogates | graph representation x task x dataset x generalisation test | Accuracy on one dataset | Out-of-distribution tests across typologies; what the graph encodes that a vector cannot |
| Systematic and PRISMA reviews | topic x method family x evidence type x period | A narrative summary | A counted evidence map, an extraction schema and a verdict per question ([`research-synthesis`] and [literature-review.md](../literature-review.md)) |

For each line, write the dimensions file once, keep it with the project, and re-run the map before every
submission: a gap that was empty last year may hold a paper now.
