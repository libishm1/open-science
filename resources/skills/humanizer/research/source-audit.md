# Audit of the original evidence chain

Seed: Humanizer 3.1.0, commit `0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0`. Its stated primary source is Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).

The inspected Wikipedia revision is [1384534594](https://en.wikipedia.org/w/index.php?title=Wikipedia:Signs_of_AI_writing&oldid=1384534594), last edited 8 November 2026. This page offers descriptive editing advice; it is not a peer-reviewed benchmark establishing the sensitivity, specificity or optimal ranking of all 26 Humanizer patterns.

## All reference positions in the inspected seed

Numbers refer to the seed page, not Humanizer's pattern numbers. This inventory covers the 41 numbered reference positions, not every inline external link. Short descriptions below identify records; they are not a substitute for verified bibliographic metadata. “Located” means an original record or abstract was retrieved, not full critical appraisal.

| Ref | Record | Type and status |
|---|---|---|
| 1 | Russell, Karpinska, Iyyer, frequent users detecting AI | ACL 2025 research; [original](https://aclanthology.org/2025.acl-long.267/) located |
| 2 | Dik, Erdem, Dik, GPTZero | [Preprint](https://arxiv.org/abs/2506.23517) located; later journal record needs version reconciliation |
| 3 | Dugan et al., RAID | ACL 2024 research; [original](https://aclanthology.org/2024.acl-long.674/) located |
| 4 | Cheng et al., healthcare text detection | [Journal article](https://doi.org/10.1186/s41077-025-00396-6) located |
| 5 | Fiedler and Döpke, German theses | [Journal article](https://doi.org/10.1016/j.iree.2025.100321) located |
| 6 | Yakura et al., influence on spoken language | [arXiv record](https://arxiv.org/abs/2409.01754) located; version-sensitive |
| 7 | Geng et al., academic speech | [ACL 2025 record](https://aclanthology.org/2025.findings-acl.987/) located |
| 8 | Galpin, Anderson, Juzek, structure | [Preprint](https://arxiv.org/abs/2506.21817) located; proceedings lineage not fully reconciled |
| 9 | Druck, Paredes, Smith, Graphite AI Tells | Industry analysis; seed-linked, not independently appraised |
| 10 | Wendy Belcher, Chronicle essay | Opinion; seed-linked, not empirical validation |
| 11 | Sun et al., LLM idiosyncrasies | [ICML 2025 record](https://proceedings.mlr.press/v267/sun25z.html) located; author is Kolter, not Koller |
| 12 | Juzek and Ward, “Delve” | [COLING 2025 record](https://aclanthology.org/2025.coling-main.426/) located; correct venue metadata |
| 13 | Reinhart et al., human/LLM registers | [PNAS 2025](https://doi.org/10.1073/pnas.2422455122) located |
| 14 | Geng and Trotta, coevolution | [ACL 2025](https://aclanthology.org/2025.findings-acl.657/) PDF and references inspected |
| 15 | Huang et al., Wikipedia in the LLM era | [Preprint](https://arxiv.org/abs/2503.02879) and TMLR 2026 PDF located; one study lineage |
| 16 | Kobak et al., excess vocabulary | [Science Advances 2025](https://doi.org/10.1126/sciadv.adt3813) located |
| 17 | Juzek and Ward, alignment follow-up | [Springer proceedings chapter](https://doi.org/10.1007/978-3-032-19096-3_16) located; first online 2026 |
| 18 | The Economist, spotting AI writing | Journalism; not independently appraised |
| 19 | Sam Kriss, New York Times | Commentary; not independently appraised |
| 20 | Kousha and Thelwall, multi-database shifts | [Scientometrics 2026](https://doi.org/10.1007/s11192-026-05601-5) and earlier preprint/proceedings lineage located |
| 21 | Merrill et al., Washington Post analysis | Journalism/data analysis; not independently appraised |
| 22 | Buchert, ChatGPT review | Blog; not peer reviewed; not independently appraised |
| 23 | Geng and Trotta, transforming academic writing | [2024 preprint](https://arxiv.org/abs/2404.08627) located |
| 24 | Robbins, Substack | Commentary; not independently appraised |
| 25 | Spero, Emi, Pangram | [Vendor preprint](https://arxiv.org/abs/2402.14873) located; self-reported evaluation |
| 26 | GPT-4 system card | Model-provider technical report; seed-linked; not a validation of all editing rules |
| 27 | Rudnicka, Scientific American | Journalism; not independently appraised |
| 28 | Zhou, Cho, Terveen, Wikipedia participation | [Preprint](https://arxiv.org/abs/2509.07819) and institutional publication record located; qualitative research |
| 29 | Stanford HAI bias explainer | Institutional explainer; distinguish from underlying study |
| 30 | Jafarov, Azerbaijani AI | Original source unresolved in this pass; exclude from evidential claims |
| 31 | Wall Street Journal, censorship | Journalism; not independently appraised |
| 32 | Fortune, censorship | Journalism; not independently appraised |
| 33 | Reinhart et al. | Duplicate of ref 13, not another study |
| 34 | Murray and Tersigni, instructors | [JALT 2024](https://doi.org/10.37074/jalt.2024.7.2.12) located |
| 35 | Jill Walker Rettberg, genre glitches | Scholar's blog; useful hypothesis source, not equivalent to a controlled trial |
| 36 | Sussman and Carter, communication | [2025 preprint](https://arxiv.org/abs/2504.19556) located |
| 37 | Strzelecki, knowledge-update residue | [Learned Publishing](https://doi.org/10.1002/leap.1650) located; online 2024 versus issue 2025 |
| 38 | Ju, Blix, Williams, Domain Regeneration | [ACL 2025](https://aclanthology.org/2025.findings-acl.120/) located |
| 39 | Ars Technica, em dashes | Journalism; not independently appraised |
| 40 | Birattari, Italian style | Language/style advice; seed-linked, not independently appraised |
| 41 | Cortelazzo, University of Padua | Language/style advice; seed-linked, not independently appraised |

## Repository evaluation claim

The README's “16/16” claim links to [upstream issue 229](https://github.com/blader/humanizer/issues/229). The inspected community report uses LLM judges, rather than a blinded panel of human readers. It also reports an incomplete broader quality run and controls with imperfect topic matching. Treat it as exploratory contributor evidence. It does not validate every pattern, every genre or academic manuscripts.

## Corrections applied to the skill

- Replaced the categorical statement that all text before 30 November 2022 is not AI-written.
- Reframed pattern strength/order as editing heuristics, not validated authorship evidence.
- Qualified the blanket “people judge near chance” claim: results depend on expertise and study conditions.
- Added an academic override preserving necessary hedges, technical terminology, reporting structure and venue conventions.

Remaining research gap: no rule-by-rule sensitivity, specificity, inter-rater agreement or genre ablation was established by this pass. The experimental design in [evaluation.md](evaluation.md) addresses that gap.
