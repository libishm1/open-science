# Evidence map

Checked through 9 November 2026. “Abstract” means the original abstract or publisher-indexed extract was available, not that the entire study was independently assessed. Findings below are authors' reported results unless stated otherwise.

## Backward foundations

| Source | Why it matters | Access in this pass |
|---|---|---|
| Biber (1988), [Variation across Speech and Writing](https://doi.org/10.1017/CBO9780511621024) | Register is multidimensional; sentence length alone is a poor style specification. | Publisher record |
| Gopen and Swan (1990), [The Science of Scientific Writing](https://www.cs.tufts.edu/comp/150FP/archive/george-gopen/sci.html), American Scientist 78:550–558 | Reader expectations and information placement offer a better editing basis than cosmetic word substitution. | Full article repost; [author's record](https://georgegopen.com/scientific-writing-articles/) |
| Hyland (2005), [Stance and engagement](https://doi.org/10.1177/1461445605050365) | Analysis across eight disciplines supports preserving discipline-specific hedging and author positioning. | Publisher abstract |
| Plavén-Sigray et al. (2017), [The readability of scientific texts is decreasing over time](https://elifesciences.org/articles/27725) | Difficult scientific prose predates ChatGPT; readability is not an authorship test. | Original article |
| Brown et al. (2020), [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) | Direct counterexample to treating November 2022 as the beginning of AI text generation. | Original abstract |

## Contemporary empirical and methodological work

| Source | Finding relevant to implementation | Limitation / access |
|---|---|---|
| Liang et al. (2023), [GPT detectors are biased against non-native English writers](https://doi.org/10.1016/j.patter.2023.100779) | Include multilingual and second-language author controls when evaluating tools. | Tested detectors and datasets of that period; original article record |
| Mitchell et al. (2023), [DetectGPT](https://proceedings.mlr.press/v202/mitchell23a.html) | Probability-based detection is a separate task from editorial quality. | Model-access assumptions; original abstract |
| Dugan et al. (2024), [RAID](https://aclanthology.org/2024.acl-long.674/) | Detection performance can shift with domain, model, generation settings and transformations. | Benchmark coverage does not establish universal impossibility; original abstract |
| Geng and Trotta (2024), [Is ChatGPT Transforming Academics' Writing Style?](https://arxiv.org/abs/2404.08627) | Early longitudinal evidence of changing academic word use. | Observational preprint/workshop lineage; abstract |
| Juzek and Ward (2025), [Why Does ChatGPT “Delve” So Much?](https://aclanthology.org/2025.coling-main.426/) | Preference alignment is a candidate explanation for marked lexical preferences. | Focused vocabulary; COLING, not Findings of ACL as the Wikipedia entry suggests; original record |
| Reinhart et al. (2025), [Do LLMs write like humans?](https://doi.org/10.1073/pnas.2422455122) | Linguistic differences depend on register and model. Design profiles by genre and section. | Tested models/corpora; original article indexed at [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/) |
| Kobak et al. (2025), [Delving into ChatGPT usage in academic writing through excess vocabulary](https://doi.org/10.1126/sciadv.adt3813) | Excess-word analysis supports population-level estimates of change. | Does not classify an individual author or sentence; original article indexed at [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12219543/) |
| Geng and Trotta (2025), [Human–AI coevolution in academic writing](https://aclanthology.org/2025.findings-acl.657/) | Some markers decline while others rise; a static blacklist becomes stale. | Observational trends have competing explanations; PDF and bibliography inspected |
| Russell, Karpinska and Iyyer (2025), [People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text](https://aclanthology.org/2025.acl-long.267/) | Expertise and task conditions matter; “humans are always near chance” is too broad. | Selected expert group and nonfiction task; original abstract |
| Sun et al. (2025), [The Idiosyncrasies of Large Language Models](https://proceedings.mlr.press/v267/sun25z.html) | Model identity can be reflected in distributional features beyond stock phrases. | Model attribution is not proof of human/AI authorship; original conference abstract |
| Mo and Crosthwaite (2025), [JEAP study of LLM stance and engagement](https://doi.org/10.1016/j.jeap.2025.101499) | Treat stance and engagement as meaningful dimensions rather than filler. | Limited essay samples and models; original publisher abstract |
| Kousha and Thelwall (2026), [Scientometrics study](https://doi.org/10.1007/s11192-026-05601-5) | Multi-database lexical trends suggest broad changes in scientific prose. | Cannot isolate generation, editing and human adoption; original article and references inspected; 2025 preprint is the same study lineage |
| Juzek and Ward (2026), [Alignment follow-up](https://doi.org/10.1007/978-3-032-19096-3_16) | Experimental preference-learning work strengthens the case for studying alignment-induced lexical choices. | Specific models/preferences; publisher abstract; proceedings dated 2025, first online April 2026 |
| McKinley (2026), [study of AI-assisted postgraduate writing](https://doi.org/10.1515/dsll-2025-0016) | Polishing can change hedging and writer presence, not just grammar. | Small cohorts; original abstract, not causal evidence for every discipline |
| Koyama (2026), [Synthetic English and LLM-mediated writing](https://doi.org/10.1017/S0266078426101667) | A research agenda for register variation and changing norms. | Conceptual agenda, not a validated rewriting method; article and references inspected; published 4 November 2026 |
| Pangram (2026), [Pangram 4](https://arxiv.org/abs/2607.27183) | Mixed human/AI spans are an emerging evaluation target. | Vendor-authored preprint; performance claims need external replication; abstract |
| Nam et al. (2026), [ScientistTwo](https://arxiv.org/abs/2609.19644) | Separate manuscript fluency from evidence integrity and scientific review. | Preprint; [assessment](scientist-two.md) |

## Inspected citation edges

An arrow here means the later document's bibliography contains the earlier work. It does not imply agreement or independent replication.

| Later source | Earlier source | Where checked |
|---|---|---|
| Geng and Trotta 2025 | Geng and Trotta 2024 | ACL PDF bibliography |
| Geng and Trotta 2025 | Kobak et al. 2024 preprint | ACL PDF bibliography; same lineage as Science Advances 2025 |
| Kousha and Thelwall 2026 | Kobak et al. 2024 preprint | Publisher reference list |
| Mo and Crosthwaite 2025 | Hyland 2005 | Publisher abstract explicitly names the framework |
| Koyama 2026 | Reinhart et al. 2025 | Publisher reference list |
| Koyama 2026 | Kobak et al. 2025 | Publisher reference list |
| Koyama 2026 | Mo and Crosthwaite 2025 | Publisher reference list |
| Koyama 2026 | McKinley 2026 | Publisher reference list |
| ScientistTwo 2026 | ScientistOne 2026; AI Scientist-v2 2025; ScholarPeer 2026 | arXiv full-text references; source records still need a separate full appraisal |

Juzek and Ward's 2026 work is listed as a research-program follow-up; its backward citation edge was not separately inspected. No global citation counts are reported.

## Current editorial and industry practice

These are current rules and product practices, not evidence about how people wrote in 2019. Recheck at submission because policies change.

| Primary source | Operational implication |
|---|---|
| [Nature formatting](https://www.nature.com/nature/for-authors/formatting-guide) and [AI policy](https://www.nature.com/natmachintell/editorial-policies/ai) | Apply the actual journal/article format and its current risk-based AI guidance. Do not assume one rule covers the whole Nature portfolio. |
| [MDPI ethics](https://www.mdpi.com/ethics) | Basic text editing is treated differently from generation and substantive research uses. Disclose according to the operation actually performed, not the product's “humanizer” label. |
| [Elsevier generative-AI policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals) | Check current disclosure requirements; do not reuse older summaries that restrict all AI use to language editing. Human authors retain responsibility. |
| [ICMJE AI use by authors](https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html) | Clinical workflows need disclosure, source verification and accountable human authorship. |
| [COPE position](https://doi.org/10.24318/cCVRZBms) | An AI tool cannot take author responsibility. |
| [CAADRIA 2026 call](https://www.caadria2026.org/call-for-abstracts) and [full papers](https://www.caadria2026.org/full-papers) | Event-specific templates and disclosure requirements apply. Abstract-submission length and manuscript-abstract length are different fields. |
| [Turnitin AI report guidance](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report) | A detection score can misidentify text and should not alone determine adverse action. |
| [Local-model README](https://github.com/sgaofen/humanizer-local-model) | Its detector and fact-judge evaluations are separate, setting-specific measures. Low detector scores do not certify unchanged meaning. |

## Implementation decisions drawn from this review

- Use historical samples as contextual examples, not a list of required quirks.
- Preserve scientific uncertainty, causality, denominators, units and comparison conditions before optimizing flow.
- Do not force paraphrasing of an already clear methods sentence merely to reduce copied n-grams.
- Keep a claim-to-source record and record every candidate used in evaluation.
- Validate scientific quality with domain readers and artifact checks. Report detector performance only as a secondary, dated, task-specific result.
