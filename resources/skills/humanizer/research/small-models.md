# Research dossier: small local models for proofreading, translation and drafting (English and Arabic)

> **Verified 12 November 2026.** An independent pass checked the claims this document's recommendations rest on against primary sources; see [verification.md](verification.md). Corrections from that pass are applied below and marked *Verification note*.


Compiled 12 November 2026 for the extension of the "humanizer" Markdown skill. This dossier builds on the earlier review of the AI lexical-shift literature (Kobak et al. 2025; Reinhart et al. 2025; Juzek and Ward 2025; Geng and Trotta 2024/2025; Liang et al. 2023; RAID 2024) and does not repeat it.

## Evidence labels

Every factual claim carries one of these labels. The full source list with identifiers is in the final table.

| Label | Meaning |
|---|---|
| **F** | Full text, or the relevant sections, read directly (PDF text extracted and read, or full README/data file read). |
| **Fx** | Full text processed through an automated extraction step (a fetch tool summarising the full HTML). Numbers are as extracted and were not re-checked line by line against the PDF. |
| **M** | Official model card, documentation page, repository README, or official data file. |
| **A** | Abstract or landing page only. |
| **S** | Secondary summary only (search-engine synthesis, press release, law-firm or vendor blog). Treat as unverified. |
| **V** | Bibliographic metadata verified (Crossref or ACL Anthology); content statements rest on prior knowledge, not on reading the work in this pass. |
| **I** | Inference drawn by the compiler from the cited evidence; not a reported result. |

Three caveats apply throughout:

1. Most model-comparison numbers come from the developers' own reports. Independent human evaluation of 3-4B models on English-Arabic is scarce.
2. Translation evidence is overwhelmingly English-to-Arabic. Arabic-to-English evidence for general 3-4B models is thin.
3. No study found in this pass evaluates 3-4B models on English academic proofreading specifically.

---

## 1. Small models for proofreading and translation

### 1.1 Candidate models (status November 2026)

| Model | Size | Licence | Arabic | Native context | Notes | Label |
|---|---|---|---|---|---|---|
| Qwen3-4B-Instruct-2507 | 4.0B (3.6B non-embedding) | Apache-2.0 | Qwen3 family covers 119 languages and dialects | 262,144 | Non-thinking only. Vendor sampling: T 0.7, top_p 0.8, top_k 20, min_p 0 | M; A (Qwen3 report) |
| Qwen3.5-4B / 9B | 4B language model (safetensors list ~5B incl. vision) | Apache-2.0 | 201 languages and dialects | 262,144 | **Thinking is on by default**; disable with `enable_thinking: False`. WMT24++ (xCOMET-XXL, 55 languages): 4B 66.6, 9B 72.6 | M |
| Gemma 3 4B | ~4B | Gemma Terms of Use | Broad multilingual coverage | 128K | Base of TranslateGemma 4B | A; Fx |
| TranslateGemma 4B / 12B / 27B | 4B / 12B / 27B | Gemma Terms of Use | 55 languages; evaluated on ar_EG and ar_SA | **2K input tokens** | Requires a structured template with source and target language codes; card examples use greedy decoding | A; M |
| Gemma 4 E2B / E4B | E4B: 4.5B effective (8B with embeddings) | Apache-2.0 | "35+ languages out of the box, pre-trained on 140+"; Arabic not named | 128K | MMMLU 76.6 (E4B); no MT benchmark on card | M |
| Tiny Aya Global / Earth | 3.35B | **CC-BY-NC 4.0** | 70 languages incl. Arabic; Earth tuned for West Asia and Africa | 8K | Strongest 3-4B general model on average chrF in its own report | Fx; M |
| Phi-4-mini-instruct | 3.8B | MIT | Arabic in the official 23-language list | 128K | Multilingual MMLU 49.3 (Qwen2.5-3B 55.9); card warns non-English quality is worse | M |
| Llama 3.2 3B Instruct | 3B | Llama 3.2 Community Licence | **Not officially supported**; use in unsupported languages is listed as out of scope | 128K | | M |
| Ministral 3 (3B / 8B / 14B) | 3-14B | Apache-2.0 | Not confirmed | not checked | Weakest English-to-Arabic scores in the Tiny Aya tables | S; Fx |
| SmolLM3-3B | 3B | not checked | Not listed | not checked | Flores average chrF 16.8 in the Tiny Aya evaluation | Fx |
| Hunyuan-MT-7B | 7B | **Not confirmed** (check repository licence) | Arabic among 33 languages | not checked | Authors report first place in 30 of 31 WMT25 categories; see 1.2(e) for the organisers' caveat | A; M |
| Aya Expanse 8B | 8B | **CC-BY-NC 4.0** | Arabic among 23 | 8K | | M |
| Mutarjim | ~1.5B (Kuwain-1.5B base) | Not confirmed | Arabic-English only | not checked | Strong on its authors' Tarjama-25 benchmark | A; Fx |
| Hala | 350M-9B | Not stated on abstract page | Arabic-centric, translation-oriented | not checked | | A |
| Falcon-H1-Arabic 3B / 7B | 3B / 7B (also 34B) | Not confirmed | Arabic incl. dialect data | 128K (3B), 256K (7B) | OALL ~62% (3B), 71.7% (7B), vendor-reported; no translation evaluation | M (official blog) |

### 1.2 Evidence on English-Arabic translation

*Verification note:* the Tiny Aya report also shows Tiny Aya Water tying Tiny Aya Earth on FLORES en-ar (0.53), Tiny Aya Fire above Earth on WMT24++ Arabic (ar_EG 0.31 against 0.30; ar_SA 0.36 against 0.34), and SmolLM3 at 0.44 on FLORES en-ar, above Qwen3-4B (0.42). SmolLM3 is excluded below for its overall average and declared language support, not for its Arabic score.

**(a) Tiny Aya report (Cohere Labs, arXiv:2603.11510) [Fx].** The only head-to-head comparison of current 3-4B general models on Arabic found in this pass.

Average chrF across languages:

| Model | Flores (66 languages) | WMT24++ (55 languages) |
|---|---|---|
| Tiny Aya Global | 43.5 | 46.0 |
| Gemma 3 4B | 38.9 | 41.9 |
| Qwen3.5-4B | 36.1 | 40.1 |
| Qwen3-4B | 30.5 | 32.9 |
| Ministral-3-3B | 32.0 | 31.5 |
| SmolLM3-3B | 16.8 | 18.4 |

TranslateGemma-4B is reported as roughly on par with Tiny Aya Global on average. English-to-Arabic chrF (0-1 scale, appendix tables 21-22):

| Model | Flores en-ar | WMT24++ en-ar_EG | WMT24++ en-ar_SA |
|---|---|---|---|
| TranslateGemma 4B | 0.52 | **0.35** | **0.39** |
| Tiny Aya Earth | **0.53** | 0.30 | 0.34 |
| Tiny Aya Global | 0.52 | 0.31 | 0.35 |
| Gemma 3 4B | 0.50 | 0.30 | 0.34 |
| Qwen3.5-4B | 0.49 | 0.29 | 0.31 |
| Qwen3-4B | 0.42 | 0.27 | 0.30 |
| Ministral-3-3B | 0.38 | 0.21 | 0.24 |

Limitations: developer evaluation; chrF only; English-to-X only (no Arabic-to-English); no human evaluation for Arabic; Llama 3.2 3B and Phi-4-mini not included.

**(b) TranslateGemma (arXiv:2601.09012) [A; M].** Gemma 3 fine-tuned with supervised data then reinforcement learning against an ensemble of reward models (MetricX-QE, AutoMQM) [A]. Model card, WMT24++ over 55 languages: MetricX (lower is better) 5.32 / 3.60 / 3.09 and COMET 81.6 / 83.5 / 84.4 for 4B / 12B / 27B [M]. Human (MQM) evaluation on WMT25 is reported only for 12B and 27B [M]. A secondary summary gives the Gemma 3 4B baseline as MetricX 6.97 [S]. Practical constraints: 2K-token input context and a fixed message format with ISO language codes [M]; the report notes named-entity mistranslation as a residual weakness (Japanese-English) [S].

**(c) Qwen3.5 model card [M].** WMT24++ (xCOMET-XXL averaged over 55 languages): 4B 66.6, 9B 72.6. Within the family the 9B is a material step up. These numbers are not directly comparable with TranslateGemma's MetricX/COMET figures.

**(d) Mutarjim and Tarjama-25 (arXiv:2505.17894) [A; Fx].** Tarjama-25 has 5,000 expert-reviewed sentence pairs. Selected results (COMET):

| Model | Size | AR-to-EN | EN-to-AR |
|---|---|---|---|
| Mutarjim | 1.5B | 82.63 | 83.41 |
| GPT-4o mini | n/a | 83.67 | 83.36 |
| Cohere (listed as 8B) | 8B | 81.20 | 82.50 |
| Cohere (listed as 32B) | 32B | 82.44 | 82.09 |
| NLLB | 3.3B | 67.06 | 81.27 |
| ALLaM | 7B | 72.90 | 75.41 |
| AceGPT | 8B | 80.71 | 78.39 |
| SILMA | 9B | 64.36 | 58.01 |
| Gemma 2 | 27B | 80.81 | 42.20 (chrF++ 3.52) |

Observations: a 1.5B specialised model matches GPT-4o mini on English-to-Arabic on this benchmark; Arabic-centric chat models (ALLaM, SILMA, AceGPT) are weaker translators than multilingual models of similar size; Gemma 2 27B collapsed on English-to-Arabic, which indicates an output-language or format failure rather than weak translation, so a pipeline must check the output language. The paper's text claims state-of-the-art Arabic-to-English on all metrics while its table shows GPT-4o mini higher; this inconsistency was noted by the extraction step [Fx]. The authors also report that tuning only on long inputs increased hallucinated continuations on short inputs [Fx].

**(e) WMT25 General MT findings (Kocmi et al. 2025, DOI 10.18653/v1/2025.wmt-1.22) [F, sections].**
- English-to-Egyptian Arabic was one of the two hardest pairs; systems tended to output Modern Standard Arabic instead of Egyptian, "an error that would likely be overlooked by quality estimation metrics".
- No model below 7B was in the official LLM benchmark. CommandR 7B reached a best rank of 11-14 on English-Egyptian Arabic.
- Many 7-8B models failed to translate a whole document while keeping paragraph breaks. Share of data translated at document level: GPT-4.1 97.1%, Gemini-2.5-Pro 95.1%, Qwen2.5-7B 70.4%, Aya Expanse 8B 43.2%, Mistral-7B 35.7%, Llama-3.1-8B 35.1%, CommandR 7B 27.1%. The organisers used temperature 0 and fell back to paragraph-by-paragraph translation when a document failed.
- Automatic rankings did not always match human judgements; the Hunyuan-based system that topped automatic metrics did not consistently win in human evaluation.

**(f) Context.** WMT24 findings: "The LLM era is here but MT is not solved yet" [A]. WMT24++: on automatic metrics LLMs are the best systems in all 55 languages, with human confirmation left for future work [A].

### 1.3 Evidence on English (and Arabic) proofreading

- Davis et al. (ACL Findings 2024): seven open and three commercial LLMs on four English GEC benchmarks. LLMs do not always beat supervised GEC systems; several open models beat commercial ones on minimal-edit benchmarks; zero-shot prompting is sometimes as competitive as few-shot [A].
- Fang et al. (2023): ChatGPT corrects fluently but over-corrects and does not follow the minimal-edit principle; it struggles with cross-sentence agreement, coreference and tense [A].
- Kwon et al. (2023), Arabic GEC: instruction-tuned LLMs, including GPT-4 at 65.49 F1 with expert prompting, are outperformed by fully fine-tuned and much smaller models (73.29 F1 on QALB-2014) [A].
- Vendor writing and instruction-following scores: Qwen3-4B-Instruct-2507 improved WritingBench from 68.5 to 83.4 and MultiIF from 61.3 to 69.0 over the original Qwen3-4B non-thinking mode [M]; Qwen3.5-4B MAXIFE 78.0, 9B 83.4 [M]. These measure fluency and instruction following, not editing fidelity.
- [I] For proofreading, fidelity (minimal edits, no meaning drift, citations and numbers untouched) matters more than fluency, and none of the available benchmarks measures it for 3-4B models. It has to be measured on the user's own text.

### 1.4 Effect of 4-bit quantisation

- **Marchisio et al., "How Does Quantization Affect Multilingual LLMs?" (Findings of EMNLP 2024, arXiv:2407.03211) [F].** Arabic is among the ten primary languages of the automatic evaluation (human evaluation covered other languages). Findings: (1) automatic metrics severely underestimate damage; a 1.7% average automatic drop in Japanese corresponded to a 16.0% drop in human ratings; (2) non-Latin-script languages are hurt most; (3) at 4-bit, smaller models are more sensitive (Command 103B vs 35B with group-wise W4: -0.9% vs -2.8% on average; -2.9% vs -13.1% on MGSM); (4) group-wise scaling (W4-g) recovers much of the loss of naive per-column W4; (5) the correlation between degradation and a language's share of web data strengthens at 4-bit (R² 0.24 at W8 to 0.63 at W4).
- **Marie and Fujita, "The Uneven Impact of Post-Training Quantization in Machine Translation" (arXiv:2508.20893) [Fx].** 55 languages, five models from Qwen3-1.7B to Llama-3.3-70B, WMT24++, COMET. 4-bit generally preserves quality for high-resource languages and larger models; low-resource languages degrade more. For Qwen3-1.7B at GGUF Q4_K_M the COMET change was small for high-resource targets (Japanese 80.4 to 79.7; French 74.2 to 74.3) and larger for lower-resource ones (Bengali 50.1 to 48.5; Zulu 27.3 to 26.0). GGUF was the most consistent of the four post-training methods compared. Arabic is not in the main tables.
- **Kurtic et al., "Give Me BF16 or Give Me Death?" (ACL 2025, arXiv:2411.02355) [A].** Over 500,000 evaluations on Llama 3.1: FP8 effectively lossless; INT8 1-3% degradation; INT4 weight-only "more competitive than expected".
- **Tiny Aya report [Fx].** Q4_K_M: ~2.14 GB memory and ~1.4-point degradation on mDolly; Q4_0 ~2.1 points; Q8_0 negligible. Degradation was smaller for languages with more web presence.
- **WMT25 Model Compression task** required compressing Aya Expanse 8B on, among others, English-to-Arabic, with 8-bit and 4-bit baselines [S]. The findings paper was not read.
- [I] Q4_K_M is an acceptable floor for English editing at 4B. For Arabic output, the evidence (non-Latin scripts hurt more, small models more sensitive, automatic metrics understating human-perceived loss) favours Q6_K or Q8_0 where memory allows. No study measured Q4_K_M against Q8_0 for a 4B model on English-Arabic; the tool's own test set should close this gap.

### 1.5 Runtimes with an OpenAI-compatible API

| Runtime | Endpoints | Context control | Structured output | Notes | Label |
|---|---|---|---|---|---|
| llama.cpp `llama-server` | `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings`, Responses and others | `-c/--ctx-size`; default 0 = model's trained context. `-np/--parallel` slots (default auto) share the KV pool; `--kv-unified-per-slot N` caps each slot | `response_format` with `json_object` or `json_schema`; GBNF grammars | Jinja chat templates on by default. Server defaults T 0.8, top_k 40, top_p 0.95, min_p 0.05, so send sampling parameters explicitly. No watermarking option in the README (the only "watermark" hit is a metrics counter) | F (README) |
| Ollama | `http://localhost:11434/v1/` chat, completions, embeddings, responses | **Default 4K context when VRAM < 24 GiB** (32K at 24-48 GiB; 256K at 48 GiB+). The OpenAI API cannot set context size; use a Modelfile `PARAMETER num_ctx` or `OLLAMA_CONTEXT_LENGTH` | `response_format` JSON mode | `logit_bias`, `n`, logprobs unsupported | M |
| LM Studio | `http://localhost:1234/v1` chat, completions, embeddings, responses | Per-model load-time setting | Separate "Structured Output" page (not read) | Good for non-technical users | M |
| vLLM | `vllm serve`; chat, completions, embeddings, responses | not checked | not checked | GPU-first. CPU backend: x86 wheels from 0.17.0 (AVX512 recommended), ARM from 0.11.2; Apple silicon experimental, source build only; CPU page does not mention GGUF | M |

Effective context on a laptop is smaller than the native window, for three reasons:

- model-specific limits are tight for the translation specialists (TranslateGemma 2K input; Tiny Aya and Aya Expanse 8K) [M];
- reasoning performance degrades at input lengths far below the technical maximum (Levy et al., ACL 2024) [A], and information in the middle of long inputs is used worst (Liu et al., TACL) [A];
- tokenisers can need many times more tokens for the same text in some languages (up to 15x; Petrov et al., NeurIPS 2023) [A]. The abstract gives no Arabic figure, so Arabic token counts should be measured with each model's tokenizer.

### 1.6 Recommendations for the tool (section 1)

1. **Default model routing** (choose on the user's test set before fixing):

| Task | Laptop default (8-16 GB RAM) | Step up (16-32 GB) | Frontier option |
|---|---|---|---|
| English proofreading | Qwen3-4B-Instruct-2507 (Apache-2.0, non-thinking) | Qwen3.5-9B, thinking off | Final pass on flagged paragraphs only |
| English-to-Arabic translation | TranslateGemma 4B (one paragraph per call, under 2K tokens) | TranslateGemma 12B | Escalate paragraphs that fail checks |
| Arabic-to-English translation | TranslateGemma 4B or Gemma 3 4B; test Mutarjim 1.5B if its licence permits | TranslateGemma 12B or Qwen3.5-9B | As above |
| Arabic proofreading | Detection-only mode (flag, do not rewrite) with Gemma 3/4 4B or Tiny Aya | Same, 8-12B | Rewrites only on author request |
| Drafting from notes (English) | Qwen3.5-4B (thinking off) or Qwen3-4B-Instruct-2507 | Qwen3.5-9B | Optional outline or final pass |
| Drafting from notes (Arabic) | Gemma 3/4 4B-class; test Falcon-H1-Arabic 3B | Falcon-H1-Arabic 7B, TranslateGemma 12B for translated drafts | As above |

2. **Exclude for Arabic:** Llama 3.2 3B (not supported), SmolLM3-3B, and Ministral-3-3B (weakest English-to-Arabic in the only comparison found).
3. **Licences:** store a licence field per model. Flag non-commercial weights (Tiny Aya, Aya Expanse) and unconfirmed licences (Hunyuan-MT, Mutarjim, Falcon-H1-Arabic, Hala). Tiny Aya Earth is a strong option for personal academic use if non-commercial terms are acceptable.
4. **Quantisation:** Q4_K_M as the floor; Q6_K or Q8_0 for any model that writes Arabic. Evaluate the exact quantised file that ships.
5. **Runtime:** use `llama-server` as the reference backend. Always send `temperature`, `top_p`, `top_k`, `min_p`, `repeat_penalty` and `seed`; set `-c` explicitly; run with `-np 1` on a laptop. For Ollama, ship a Modelfile with `num_ctx` of at least 8192 and compare `usage.prompt_tokens` with the expected count to detect silent truncation.
6. **Thinking mode:** disable it for Qwen3.5 by default (see 2.2).

---

## 2. Prompting and pipeline techniques for small models

### 2.1 Instruction length and format

- Instruction-following accuracy falls as the number of simultaneous instructions grows; the best frontier models reach only about 68% at 500 instructions, and models show a bias towards earlier instructions (IFScale, arXiv:2507.11538) [A].
- Open models are highly sensitive to formatting changes in few-shot prompts, up to 76 accuracy points for LLaMA-2-13B, and the sensitivity persists with larger models, more examples and instruction tuning (Sclar et al., ICLR 2024) [A].
- Longer inputs degrade reasoning well below the context limit (Levy et al.) [A]; mid-context information is used least (Liu et al.) [A].
- [I] For 3-4B models, a long rule list in the system prompt is likely to be followed partially and unpredictably. Keep the prompt short and task-specific, put the most important constraint first, and move style rules (banned words, punctuation, digits) into deterministic post-checks.

### 2.2 Decoding and reasoning

- For ChatGPT translation, lower temperature usually performed better, and chain-of-thought prompting leads to "word-by-word translation behavior, thus bringing significant translation degradation" (Peng et al., Findings of EMNLP 2023, arXiv:2303.13780) [A].
- WMT25 organisers used temperature 0 for all LLMs [F].
- Test-time reasoning gives limited and inconsistent gains for direct translation, and forcing reasoning beyond the model's natural stopping point lowers quality; extra reasoning helps most in post-editing (Li, Ji and Tiedemann, arXiv:2510.06471) [A].
- Enabling explicit reasoning "consistently degrades translation quality across languages and models", because MT reasoning traces are linear and do not revise (Rajaee et al., arXiv:2602.14763) [A].
- Vendor defaults differ: Qwen T 0.7, top_p 0.8 [M]; Hunyuan-MT T 0.7, top_p 0.6, top_k 20, repetition penalty 1.05 [M]; TranslateGemma card examples use greedy decoding [M]; Tiny Aya card example T 0.1 [M].
- [I] For proofreading and translation, turn thinking off, use T between 0 and 0.3 with top_p around 0.8-0.95, keep repetition penalty at or below 1.05 to avoid loops, and fix the seed. Drafting from notes can use the vendor default (about 0.7).

### 2.3 Few-shot examples

- Example quality is the most important factor in few-shot MT prompting (Vilar et al., ACL 2023) [A].
- For GEC, zero-shot is sometimes as good as few-shot (Davis et al.) [A].
- Few-shot examples help LLMs produce dialectal Arabic, which they otherwise avoid (AL-QASIDA, arXiv:2412.04193) [A].
- Fuzzy matches from a translation memory plus terminology in the prompt improve LLM translation, with English-Arabic among the pairs studied (Moslem et al., EAMT 2023) [A].
- [I] Use zero-shot for proofreading. For translation, add one to three short, high-quality, in-domain example pairs from the user's own approved translations, retrieved by similarity, with identical formatting every time.

### 2.4 Glossaries and terminology

- Phrase-level dictionary hints in the prompt improve low-resource and out-of-domain MT (DiPMT, Ghazvininejad et al.) [A].
- WMT25 Terminology task: providing proper terminology "consistently boosts both overall translation quality and term accuracy"; random terminology gives smaller gains; sentence-level benchmarks are near saturation while document-level finance translation still falls short (Semenov et al., DOI 10.18653/v1/2025.wmt-1.30) [A].
- [I] Inject only glossary entries whose source term occurs in the current paragraph (at most about 10-20), as plain "source term -> required target term" lines, and verify presence of each target term after generation.

### 2.5 Chunking

- Paragraph-level translation beat sentence-level for literary text (fewer mistranslations, grammar and style errors), but critical errors, including omissions, persisted (Karpinska and Iyyer, arXiv:2304.03245) [A].
- 7-8B models often failed document-level translation with paragraph breaks preserved; paragraph-level fallback was used (WMT25) [F].
- TranslateGemma accepts 2K input tokens [M].
- [I] Translate one paragraph per call, with the previous source paragraph and its accepted translation supplied as read-only context. Treat headings, list items, table cells and captions as separate units. Never send equations, code or reference lists to the model.

### 2.6 Protecting numbers, citations, units and terms

- Numerical mistranslation is a general problem in NMT, including commercial systems (Wang et al., Findings of ACL 2021) [A].
- LLMs place markup tags well but risk losing, hallucinating or corrupting them (Dabre et al., MT Summit 2023) [A]. Placeholder substitution and detag-and-project are the two standard approaches (Hanneman and Dinu, WMT 2020) [V; S].
- In Arabic, the counted noun's form depends on the numeral (number, gender, case agreement), and MT systems have been tested on exactly this (study of Google Translate, Systran, Bing) [S].
- [I] Mask-then-restore is sound for citations, DOIs, URLs, LaTeX, code and locked terms. For numbers that govern grammar in Arabic, do not hide the value: keep the digits visible inside a copy-me marker (for example `⟦12⟧`), or leave them unmasked and verify afterwards. Every placeholder must appear exactly once in the output; on mismatch retry once, then flag.

### 2.7 Self-refinement, critic loops and multi-agent pipelines

- Prompted intrinsic self-correction has not been shown to work except in tasks well suited to it; it works with reliable external feedback or after fine-tuning (Kamoi et al., TACL 2024) [A]. Without external feedback, LLMs struggle to self-correct reasoning and sometimes get worse (Huang et al., ICLR 2024) [A].
- Self-Refine gave about 20% absolute average gains with GPT-3.5/ChatGPT/GPT-4, but Vicuna-13B could not produce feedback in the required format and, even with oracle feedback, often repeated its output or hallucinated a conversation. A "mixed-refine" set-up, with the small model drafting and ChatGPT giving feedback and refining, raised Vicuna's math score from 24.18% to 40.5%. Most failures came from wrong feedback, not from bad refinement (Madaan et al., arXiv:2303.17651) [F].
- Translate, estimate, refine (TEaR) improves LLM translation, and the choice of estimation strategy matters (Feng et al., arXiv:2402.16379) [A].
- Prompting LLaMA-2 to post-edit with MQM error feedback improves TER, BLEU and COMET, but the benefit of fine-grained feedback is unclear without fine-tuning (Ki and Carpuat, Findings of NAACL 2024) [A].
- Iterative refinement lowers string-metric scores but humans rate the output more fluent and natural; anchoring to the source and starting from a reasonable draft both matter (Chen et al., arXiv:2306.03856) [A].
- Multi-stage translation (research, draft, refine, proofread) with Gemini 1.5 Pro gives large gains over zero-shot (Briakou et al., arXiv:2409.06790) [A]. TransAgents (six GPT-4-based roles) scores lower on d-BLEU but is preferred by human and LLM judges for long literary texts (Wu et al., TACL) [A].
- Hunyuan-MT-Chimera-7B fuses several candidate translations from the 7B model [A]. WMT25 participants commonly used QE reranking, MBR decoding and automatic post-editing [F].
- Failure modes for small models: format failures in feedback, drift away from the source, over-editing, and gains on fluency that string metrics penalise.
- [I] For 3-4B models: one draft, external checks, at most one targeted repair driven by the check's specific error message, and escalation of still-failing paragraphs to a larger or frontier model. Use the frontier model as critic and refiner, not the small model.

### 2.8 Recommendations for the tool (section 2)

**Prompt rules (all tasks)**
1. One task per prompt, no more than about 8 short rules, most important first. Example for proofreading: "Correct grammar, spelling and punctuation errors only. Keep the author's wording, terminology, citations and numbers. Do not add or remove content. Return only the corrected paragraph."
2. Example for translation (general model): "Translate the paragraph from English to Modern Standard Arabic. Keep every ⟦…⟧ marker exactly once. Use these term translations: … Return only the translation." For TranslateGemma, use its own message format with language codes instead.
3. Thinking off; T 0-0.3 for proofreading and translation; fixed seed; explicit `max_tokens` of roughly 1.5-2 times the source token count.
4. No chain-of-thought for translation.
5. Few-shot only from the user's own approved examples, with identical formatting.
6. State the Arabic variety explicitly (MSA by default); request dialect only with examples.

**Translation pipeline**
1. Segment into paragraphs; separate headings, lists, captions, tables; skip equations, code and reference lists.
2. Protect citations, DOIs, URLs, LaTeX, locked terms with placeholders; keep numerals visible in copy-me markers.
3. Select glossary entries present in the paragraph.
4. Translate with the previous paragraph pair as read-only context.
5. Restore placeholders and verify one-to-one.
6. Run the checks in section 5 (language and script, numbers, terms, length ratio, alignment, optional QE).
7. For flagged paragraphs, one repair call that quotes the exact problem ("number 2.5 missing", "term X must be Y"); otherwise escalate.
8. Arabic finishing pass (section 3.7) done by code, not by the model.
9. Present a review list of every flagged paragraph to the author.

**Proofreading pipeline**
1. Segment and protect as above.
2. Minimal-edit prompt.
3. Compute word-level edit rate per paragraph; flag or reject edits above a threshold calibrated on the user's own accepted edits.
4. Reject any change to numbers, citations or protected terms.
5. Flag words introduced by the edit that appear on the prior pass's AI-typical vocabulary list and were absent from the source.
6. Deliver as tracked changes for the author to accept.

**Drafting from notes**
1. Number each note.
2. Draft section by section from only the relevant notes.
3. Require a note ID for each factual sentence (kept in a hidden sidecar).
4. Check that every number and citation in the draft occurs in the notes.
5. Run the editing checks in section 3.7.
6. Mark the draft as machine-drafted for the author's revision.

---

## 3. Linguistics and stylometry of human and machine text, for editing quality

### 3.1 Measurable differences between human and LLM prose

- In news text, human writing shows more scattered sentence-length distributions, more varied vocabulary, shorter constituents and more optimised dependency distances; LLM output uses more pronouns, numbers, symbols and auxiliaries and shows less negative emotion (Muñoz-Ortiz et al., Artificial Intelligence Review 2024) [A].
- Co-writing with an instruction-tuned model (InstructGPT), but not the base model, reduced lexical and content diversity across authors (Padmakumar and He, ICLR 2024) [A].
- Diversity measures (compression ratio, long n-gram self-repetition, Self-BLEU, BERTScore-based) correlate weakly with each other, so several should be reported together (Shaib et al., AACL 2025) [A].
- Generated text carries statistical artefacts visible in token-rank statistics (GLTR, ACL 2019 demo) [A].
- "Burstiness" as used by commercial detectors is not a peer-reviewed construct. The documented, measurable counterpart is the variance of sentence length (above) [I].
- The earlier pass (Reinhart et al. 2025 on Biber features; Kobak et al. 2025 on vocabulary) covers lexical and grammatical shifts and is not repeated.

### 3.2 Function words and the author's voice

- Function-word frequencies are a classic authorship signal (Mosteller and Wallace 1963; Burrows's Delta 2002) [V].
- [I] An editor that replaces an author's function-word habits with a model's homogenises voice even when grammar improves. Editing quality should be judged partly by how little the function-word profile and sentence-length distribution move away from the author's own baseline.

### 3.3 Lexical diversity

- Type-token ratio depends on text length; MTLD and moving-average TTR (MATTR) were proposed as length-robust alternatives (McCarthy and Jarvis 2010; Covington and McFall 2010) [V].
- [I] Use MTLD or MATTR for before/after comparison of the same passage, never across passages of different length or language.

### 3.4 Register

- Biber's multidimensional analysis (1988) is the standard framework for register variation; academic prose sits at the informational, nominal end [V].
- [I] Proofreading should keep register constant. A small model asked to "improve" academic text tends towards generic expository style, so the prompt should say "correct" not "improve".

### 3.5 Translationese and machine translationese

- Baker (1993) set the agenda for corpus-based study of features typical of translated text [V]. Baroni and Bernardini (2006) showed machine learning can separate translated from original text [V].
- Volansky, Ordan and Wintner (2015) tested proposed translation universals with classifiers: some feature sets were good indicators, others near chance, so some assumed "universals" need reconsideration [A].
- Post-edited MT is simpler, more normalised and shows more source-language interference than human translation from scratch ("post-editese", Toral 2019) [A].
- MT output loses lexical and morphological richness relative to its training data across paradigms ("machine translationese", Vanmassenhove et al., EACL 2021) [A; V].
- LLM translations are often overly literal; the authors trace this to supervised fine-tuning data and reduce it by polishing references and filtering unnatural training pairs (Li et al., "Lost in Literalism", arXiv:2503.04369) [A].
- Iterative LLM refinement made translations more fluent and natural in human judgement (Chen et al.) [A].
- [I] What makes MT read as translated: source word order kept where the target prefers another; over-explicit connectives; normalised, high-frequency vocabulary; English punctuation conventions carried over; calqued collocations. These are the targets of a naturalness pass, which must stay anchored to the source.

### 3.6 Arabic-specific issues in machine output

- **Variety.** WMT25 systems asked for Egyptian Arabic tended to produce MSA, an error QE metrics would likely miss [F]. LLMs understand dialect better than they produce it, mainly because they avoid producing it (AL-QASIDA) [A].
- **Error taxonomy.** LQM (ACL 2026) proposes a six-level taxonomy for Arabic MT errors (sociolinguistics, pragmatics, semantics, morphosyntax, orthography, graphetics) and argues that MQM misses variety, coverage and pragmatic mismatches in diglossic Arabic [A].
- **Punctuation.** In Arabic, the comma, quotation marks and parentheses carry multiple and overlapping functions; the semicolon and apostrophe are rare in original Arabic texts; English marks are sometimes replaced by lexical connectors in translation (Alqinai, punctuation in English-Arabic translation) [S].
- **Numerals and separators.** Unicode CLDR 49 data: the generic `ar` locale defaults to Western digits; `ar-SA`, `ar-EG` and `ar-JO` default to Arabic-Indic digits (٠-٩) with the Arabic decimal separator U+066B; `ar-AE` uses Western digits; `ar-MA` and `ar-DZ` use Western digits with a comma decimal separator [M, data file read].
- **Bidirectional text.** UAX #9 (Unicode 18.0, revision 52) encourages directional isolates (LRI, RLI, FSI, PDI) for embedding opposite-direction runs, such as Latin terms in Arabic [M].
- **Calques.** English-derived phraseological calques in Modern Standard Arabic, especially in news language, are documented (for example Bader 1994; a 2022 study in Occasional Papers) [S]. No verified study found that measures calques in LLM output specifically.
- **Word order.** MSA permits verb-initial and subject-initial clauses while English is subject-initial; literal translation is expected to over-use subject-initial order [I; no verified empirical source on LLM output found].
- **Culture.** Multilingual and Arabic LLMs favour Western-associated entities when operating in Arabic (Naous et al., CAMeL) [A].
- **Proofreading.** Instruction-tuned LLMs lag fine-tuned GEC systems on Arabic (Kwon et al.) [A].

### 3.7 Recommendations for the tool (section 3)

1. **Editing-quality diagnostics** (shown to the author; not used to "pass" detectors):
   - change in sentence-length mean and standard deviation;
   - change in function-word profile against the author's own earlier texts (cosine of relative frequencies of the 100 most frequent function words);
   - MTLD/MATTR before and after;
   - list of newly introduced words from the AI-typical vocabulary list.
   Thresholds are set empirically from the author's accepted edits, not fixed in advance.
2. **Translation naturalness pass** (optional, anchored to source, one pass): ask for target-language word order and connectives, forbid adding or removing content, then re-run all fidelity checks.
3. **Arabic finishing rules, applied in code:**
   - Arabic comma ، semicolon ؛ and question mark ؟ in Arabic sentences; no Latin comma inside Arabic text;
   - one digit system per document, chosen by a locale setting (CLDR defaults above) with the decimal separator to match, and values verified unchanged after conversion;
   - optional directional isolates around Latin-script runs and mixed number/unit strings;
   - no tatweel; no diacritics unless requested;
   - consistent quotation-mark style per house style.
4. **Variety control:** default to MSA; for dialect, require few-shot examples and check the output with an Arabic dialect identifier if one is added later.
5. **Calque list:** let the user maintain a list of disfavoured calques and preferred alternatives. Do not ship an invented list; seed it only from a verified style guide.

---

## 4. Watermarking and detection (background for honest documentation)

This section summarises the state of knowledge only. It contains no methods for removing watermarks or defeating detectors.

### 4.1 Watermarking schemes

- **Green-list watermark** (Kirchenbauer et al., ICML 2023): before each token, a pseudo-random "green" subset of the vocabulary is chosen and softly favoured during sampling. Detection is a statistical test with interpretable p-values that needs neither the model nor its API [A]. A follow-up found watermarks remain detectable after human or machine paraphrasing given enough text; after strong human paraphrase about 800 tokens were needed at a 1e-5 false-positive rate (Kirchenbauer et al., ICLR 2024) [A].
- **Aaronson's scheme** (blog lecture, 28 November 2022): tokens are selected pseudo-randomly with a keyed cryptographic function so the output looks like normal sampling to anyone without the key. A key holder sums a score over n-grams; a few hundred tokens give a reasonable signal. The post states it is robust to small edits but can be defeated with enough effort, for example by paraphrasing with another model [Fx, partial].
- **Distortion-free watermark** (Kuditipudi et al., TMLR): maps a keyed random sequence to samples without changing the text distribution up to a generation budget. Detected at p ≤ 0.01 from 35 tokens even after 40-50% of tokens were randomly edited; less robust to some paraphrasing; only about 25% of lower-entropy Alpaca-7B responses were detectable [A].
- **Undetectable watermarks** (Christ, Gunn and Zamir): cryptographically undetectable without the secret key, assuming one-way functions exist [A].
- **SynthID-Text** (Dathathri et al., Nature 634:818-823, 2024): modifies only the sampling procedure, combines with speculative sampling, and showed no quality loss in a live experiment on nearly 20 million Gemini responses [A]. Google's documentation: implemented as a logits processor after top-k and top-p; included in Hugging Face Transformers from v4.46.0; activated only when a watermarking configuration is passed to `generate()`; less effective on factual responses; detector confidence can drop substantially after thorough rewriting or translation [M].
- **Theoretical limits.** Strong watermarking is argued to be impossible under stated assumptions about attacker oracles (Zhang et al., ICML 2024) [A]. The AUROC of the best possible detector is bounded by the total-variation distance between human and machine text distributions (Sadasivan et al., TMLR) [A].

### 4.2 Does locally run open-weight output carry a watermark?

- The schemes above act at decoding time through a logits processor or keyed sampler [A; M]. In Hugging Face Transformers both the Kirchenbauer-style `WatermarkingConfig` and `SynthIDTextWatermarkingConfig` are applied by passing a configuration to `generate()` [M]. The llama.cpp server README documents no watermarking option [F].
- Existing inference-time schemes are described as "inapplicable to the open-source setting" because the user controls decoding (Christ, Gunn, Malkin and Raykova, arXiv:2410.18861) [A].
- Watermarks can in principle be distilled into model weights, but this ability can be lost after fine-tuning on normal text (Gu et al., ICLR 2024) [A]; weight-based schemes for open models have been proposed [A].
- No documentation found for Qwen, Gemma, Llama, Phi, Tiny Aya or TranslateGemma states that their released weights carry a learned watermark. Absence of documentation is not proof of absence.
- **Conclusion:** text produced by an open-weight model run locally through llama.cpp, Ollama or LM Studio carries no decoding-time watermark unless the operator adds one [I, from the above]. Output from frontier APIs may carry provider watermarks (for example SynthID in Gemini); the tool can neither see nor certify these. Unwatermarked text is still statistically machine-like, which is what zero-shot detectors measure.

### 4.3 What detectors measure

- **Perplexity and rank statistics:** how predictable the text is under a reference model (GLTR) [A].
- **Fast-DetectGPT:** conditional probability curvature; about 340 times faster than DetectGPT with about 75% relative improvement (ICLR 2024) [A].
- **Binoculars:** contrasts two closely related language models; detects over 90% of ChatGPT samples at a 0.01% false-positive rate, zero-shot [A].
- **Trained classifiers:** generalise poorly to unseen domains and generators (M4 benchmark) [A].
- **Retrieval:** a provider-side database of past generations detected 80-97% of paraphrased outputs at a 1% false-positive rate (Krishna et al.) [A].

### 4.4 Reliability on paraphrased, non-native, edited, translated and Arabic text

- Paraphrasing with DIPPER (11B) cut DetectGPT accuracy from 70.3% to 4.6% at a 1% false-positive rate and also evaded watermarking, GPTZero and OpenAI's classifier (Krishna et al., NeurIPS 2023) [A]. Recursive paraphrasing lowers detection across detector types; watermarks can be spoofed so that human text is flagged (Sadasivan et al.) [A].
- Non-native writing: covered by Liang et al. (2023) in the earlier pass. New evidence: across 13 detectors, false-positive rates on human-written academic texts ranged from 0% to 100%, and professional English editing shifted detector scores in inconsistent directions (Park et al., EMNLP 2026, arXiv:2608.26710) [A].
- Translation: Google states SynthID confidence can drop substantially after translation [M]. No primary study found that measures detector false-positive rates on human-written text that was machine-translated.
- Arabic: detectors are confounded by diacritics; GPTZero reached 62.7% on the AIRABIC benchmark against 98.4% for fine-tuned Arabic encoders, and removing diacritics before evaluation helped (Alshammari and Elleithy, Information 2024) [V; S].
- OpenAI withdrew its own classifier on 20 July 2023 for low accuracy; at launch it identified 26% of AI-written text with 9% false positives and was unreliable below 1,000 characters [S].

### 4.5 Regulation relevant to documentation

- EU AI Act (Regulation (EU) 2024/1689, adopted 13 June 2024) [M]. Article 50(2): providers of systems generating synthetic text must mark outputs in a machine-readable, detectable form, except where the system performs an assistive function for standard editing or does not substantially alter the input or its semantics. Article 50(4): deployers publishing AI-generated text to inform the public on matters of public interest must disclose it, unless the text underwent human review or editorial control and someone holds editorial responsibility. Applies from 2 August 2026 [M, text as reproduced on artificialintelligenceact.eu (secondary; the primary text is Regulation (EU) 2024/1689 on EUR-Lex)].
- A 2026 "Digital Omnibus on AI" reportedly gives providers of systems already on the market until 2 December 2026 for Article 50(2), as Regulation (EU) 2026/1744 [S]. Verify against the Official Journal before citing.

### 4.6 Recommendations for the tool (section 4): statements for the documentation

1. "This tool does not add or remove watermarks. Text generated by open-weight models running locally carries no decoding-time watermark unless you configure one. Text from cloud models may carry the provider's watermark; the tool cannot detect or certify this."
2. "The tool is designed to improve accuracy and readability. It is not designed to, and makes no claim to, change the outcome of AI-text detectors. Published research shows these detectors give inconsistent results, and they are least reliable on non-native, professionally edited, translated and Arabic text."
3. "Detector scores are not used as a quality metric anywhere in this tool."
4. "Follow your journal's or institution's AI-use disclosure policy. Proofreading that does not substantially alter meaning is treated differently from generation under the EU AI Act; drafting from notes is generation."
5. Do not ship a detector-testing feature. Optionally, offer a "provenance note" listing models, versions and settings used per document, for the author's disclosure statement.

---

## 5. Reference-free quality checks that run on a CPU laptop

### 5.1 Learned quality-estimation (QE) metrics

| Metric | Size | Licence | Reference-free | Arabic | Evidence | Label |
|---|---|---|---|---|---|---|
| CometKiwi-22 (`Unbabel/wmt22-cometkiwi-da`) | InfoXLM-large encoder (~0.5B, inferred from architecture) | **CC BY-NC-SA 4.0**, gated | Yes (source + MT, score 0-1) | Arabic in the 94 covered languages | WMT24 metrics: average correlation 0.640 | M; F |
| CometKiwi-23 XL / XXL | 3.5B / 10.7B | CC BY-NC-SA | Yes | as above | CometKiwi-XXL 0.703 (WMT24 appendix) | F; A |
| xCOMET-XL | ~3.5B | CC BY-NC-SA 4.0, gated | QE variant (XCOMET-QE) evaluated at WMT24 | 94 languages | XCOMET-QE 0.695 | M; F |
| xCOMET-lite | 278M (mDeBERTa-v3-base) | **Not stated on card** | Not documented on card (examples pass a reference) | not listed | Retains 92.1% of xCOMET-XXL quality; beats COMET-22 and BLEURT-20 on WMT22 (EMNLP 2024) | A; M |
| MetricX-24 Hybrid (Large / XL / XXL) | mT5-based; Large ~1.2B (inferred) | **Apache-2.0** | Yes (`--qe`, empty reference) | mT5 pretraining covers Arabic; fine-tuning pairs listed do not include Arabic | MetricX-24-Hybrid-QE 0.714, second significance cluster at WMT24; scores 0-25, lower is better; max input 1,536 tokens | M; F |

WMT24 Metrics task (Freitag et al., DOI 10.18653/v1/2024.wmt-1.2) [F]: average correlation with MQM over six tasks.

- Reference-free metrics: MetricX-24-Hybrid-QE 0.714; GEMBA-ESA (prompted LLM) 0.711; XCOMET-QE 0.695; CometKiwi 0.640.
- Reference-based baselines: COMET-22 0.688; BERTScore 0.617; chrF 0.608; BLEU 0.589.
- "Fine-tuned neural metrics continue to perform well, even when used to evaluate LLM-based translation systems."
- Limitation: the language pairs were English-German, English-Spanish and Japanese-Chinese. **No Arabic.** WMT25 adds that QE metrics would likely miss MSA-for-dialect errors [F].

Kocmi et al. (WMT 2021), over 2.3M human judgements [F]:

- recommend COMET as the primary metric and chrF as the secondary metric and for unsupported languages;
- advise against BLEU;
- note "surprisingly" high accuracy for a reference-free COMET variant.

### 5.2 Round-trip (back-translation) checks

- Round-trip BLEU was a poor QE signal historically. Scoring round-trip output with semantic embeddings achieved the highest correlation with human judgements among WMT19 QE-metric submissions and was robust to the choice of backward system (Moon et al., EAMT 2020) [A].
- Round-trip scores can reflect forward quality once the copying artefact of older systems is removed (Zhuo et al., Findings of ACL 2023) [A].
- BERTScore correlates with human judgement better than earlier string metrics (ICLR 2020) [A]; chrF is a character n-gram F-score (Popović, WMT 2015) [V].
- [I] With LLMs, back-translation can silently repair forward errors. Use a different model for the backward direction from the forward one, and treat the round-trip score as a weak, ranking-only signal.

### 5.3 Alignment and omission checks

- LaBSE: cross-lingual sentence embeddings for 109 languages, 83.7% bitext retrieval accuracy on 112 Tatoeba languages (ACL 2022) [A]; Hugging Face port is Apache-2.0, about 0.5B parameters, 256-token maximum [M].
- Contrastive conditioning detects over- and under-translation without references, rivalling a supervised QE approach (Vamvas and Sennrich, ACL 2022) [A]. It needs an NMT model to score likelihoods.

### 5.4 Deterministic consistency checks

Evidence:
- numbers are a known NMT failure point (Wang et al. 2021) [A];
- named-entity errors remain in TranslateGemma [S];
- WMT25 measured the share of words in the wrong script as a quality check [F];
- small models drop paragraph breaks (WMT25) [F].

[I] Checks to run on every segment:
- multiset of numbers after digit normalisation (Arabic-Indic to Western; separators per CLDR);
- units and percentages;
- citation keys, DOIs and URLs;
- placeholders;
- glossary target terms;
- paragraph and list-item counts;
- target/source length ratio;
- output-language and script ratio;
- no untranslated source sentences.

### 5.5 CPU feasibility

- No source found reports CPU throughput for these metrics. The Hugging Face examples assume a GPU (`gpus=1`) [M].
- [I] Encoders around 0.3-0.6B (CometKiwi-22, xCOMET-lite, LaBSE) should be usable on a laptop CPU for paragraph-level scoring of a paper-length document. Models of 3.5B and above (xCOMET-XL, CometKiwi-XL, MetricX-24 XL/XXL) are impractical on CPU. This is an estimate; benchmark before committing.

### 5.6 Recommendations for the tool (section 5)

**Check pipeline**
1. Run deterministic checks (5.4) on every segment. They are cheap, precise and catch the most damaging errors.
2. Compute LaBSE cosine between source and translation per paragraph, plus the length ratio, to flag omissions or misalignment.
3. Optional learned QE per paragraph:
   - for an open-source or commercial release, MetricX-24-Hybrid-Large in QE mode (Apache-2.0; check CPU speed first);
   - for personal academic use, CometKiwi-22 (non-commercial, gated);
   - use QE scores only to rank paragraphs for review, never as pass/fail.
4. Optional round-trip with a different model, scored with chrF and BERTScore (or LaBSE). Use it as a tie-breaker only.
5. Set all thresholds empirically on the user's own reviewed translations (for example, flag the lowest-scoring 10-20% of paragraphs until calibrated). Re-calibrate per language direction and per model.
6. Document that no learned metric has been validated on Arabic in the WMT24 meta-evaluation, and that QE metrics can miss wrong-variety output.

**Licences.** Record metric licences alongside model licences. Do not bundle CC BY-NC-SA metric weights in a commercial distribution.

---

## Source table

| # | Source | Identifier | Access |
|---|---|---|---|
| 1 | Qwen3 Technical Report (Yang et al., 2025) | arXiv:2505.09388 | A |
| 2 | Qwen3-4B-Instruct-2507 model card | https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 | M |
| 3 | Qwen3.5-4B model card | https://huggingface.co/Qwen/Qwen3.5-4B | M |
| 4 | Qwen3.5 small series release reports | e.g. https://officechai.com/ai/alibaba-qwen-3-5-0-8b-2b-4b-9b-benchmarks | S |
| 5 | Gemma 3 Technical Report (Gemma Team, 2025) | arXiv:2503.19786 | A |
| 6 | TranslateGemma Technical Report (Finkelstein et al., 2026) | arXiv:2601.09012 | A (+S for baseline numbers) |
| 7 | TranslateGemma 4B model card | https://huggingface.co/google/translategemma-4b-it | M |
| 8 | Gemma Terms of Use | https://ai.google.dev/gemma/terms | M |
| 9 | Gemma 4 model card | https://ai.google.dev/gemma/docs/core/model_card_4 | M |
| 10 | Tiny Aya: Bridging Scale and Multilingual Depth (Cohere Labs, 2026) | arXiv:2603.11510 | Fx |
| 11 | Tiny Aya Global model card | https://huggingface.co/CohereLabs/tiny-aya-global | M |
| 12 | Phi-4-mini-instruct model card | https://huggingface.co/microsoft/Phi-4-mini-instruct | M |
| 13 | Llama 3.2 3B Instruct model card | https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct | M |
| 14 | Ministral 3 technical report / Mistral 3 announcement | arXiv:2601.08584; https://mistral.ai/news/mistral-3 | S |
| 15 | Hunyuan-MT Technical Report (Zheng et al., 2025) | arXiv:2509.05209 | A |
| 16 | Hunyuan-MT-7B model card | https://huggingface.co/tencent/Hunyuan-MT-7B | M |
| 17 | Aya Expanse 8B model card | https://huggingface.co/CohereLabs/aya-expanse-8b | M |
| 18 | Mutarjim (Hennara et al., 2025) | arXiv:2505.17894 | A; Fx (v2 HTML) |
| 19 | Hala Technical Report (Hammoud et al., 2025) | arXiv:2509.14008 | A |
| 20 | Falcon-H1-Arabic announcement (TII) | https://huggingface.co/blog/tiiuae/falcon-h1-arabic | M (official blog) |
| 21 | Falcon-H1-Arabic licence (aggregator and TII pages) | https://falconllm.tii.ae/falcon-h1-arabic.html | S |
| 22 | Findings of WMT25 General MT (Kocmi et al., 2025) | DOI 10.18653/v1/2025.wmt-1.22 | F (sections) |
| 23 | Findings of WMT24 General MT (Kocmi et al., 2024) | DOI 10.18653/v1/2024.wmt-1.1 | A |
| 24 | WMT24++ (Deutsch et al., 2025) | arXiv:2502.12404 | A |
| 25 | WMT25 Model Compression task | https://www2.statmt.org/wmt25/model-compression.html | S |
| 26 | How Does Quantization Affect Multilingual LLMs? (Marchisio et al., 2024) | arXiv:2407.03211 | F |
| 27 | The Uneven Impact of PTQ in MT (Marie and Fujita, 2025) | arXiv:2508.20893 | Fx |
| 28 | Give Me BF16 or Give Me Death? (Kurtic et al., ACL 2025) | arXiv:2411.02355 | A |
| 29 | llama.cpp server README | https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md | F |
| 30 | Ollama OpenAI compatibility | https://docs.ollama.com/openai | M |
| 31 | Ollama context length | https://docs.ollama.com/context-length | M |
| 32 | LM Studio OpenAI compatibility | https://lmstudio.ai/docs/developer/openai-compat | M |
| 33 | LM Studio per-model defaults | https://lmstudio.ai/docs/app/advanced/per-model | M |
| 34 | vLLM online serving | https://docs.vllm.ai/en/latest/serving/online_serving/ | M |
| 35 | vLLM CPU installation | https://docs.vllm.ai/en/latest/getting_started/installation/cpu.html | M |
| 36 | Davis et al., Prompting LMs for GEC (Findings of ACL 2024) | arXiv:2401.07702 | A |
| 37 | Fang et al., Is ChatGPT a Highly Fluent GEC System? | arXiv:2304.01746 | A |
| 38 | Kwon et al., Beyond English: LLMs for Arabic GEC | arXiv:2312.08400 | A |
| 39 | Language Model Tokenizers Introduce Unfairness (Petrov et al., NeurIPS 2023) | arXiv:2305.15425 | A |
| 40 | Same Task, More Tokens (Levy et al., ACL 2024) | arXiv:2402.14848 | A |
| 41 | Lost in the Middle (Liu et al., TACL) | arXiv:2307.03172 | A |
| 42 | How Many Instructions Can LLMs Follow at Once? (IFScale) | arXiv:2507.11538 | A |
| 43 | Quantifying Sensitivity to Prompt Formatting (Sclar et al., ICLR 2024) | arXiv:2310.11324 | A |
| 44 | Towards Making the Most of ChatGPT for MT (Peng et al., Findings of EMNLP 2023) | arXiv:2303.13780 | A |
| 45 | Test-Time Scaling of Reasoning Models for MT (Li, Ji, Tiedemann) | arXiv:2510.06471 | A |
| 46 | Unlocking Reasoning Capability on MT (Rajaee et al., 2026) | arXiv:2602.14763 | A |
| 47 | Prompting PaLM for Translation (Vilar et al., ACL 2023) | arXiv:2211.09102 | A |
| 48 | Adaptive MT with LLMs (Moslem et al., EAMT 2023) | arXiv:2301.13294 | A |
| 49 | Dictionary-based Phrase-level Prompting (Ghazvininejad et al.) | arXiv:2302.07856 | A |
| 50 | Findings of WMT25 Terminology Task (Semenov et al.) | DOI 10.18653/v1/2025.wmt-1.30 | A (+S for participant figures) |
| 51 | LLMs leverage document-level context for literary translation (Karpinska and Iyyer) | arXiv:2304.03245 | A |
| 52 | Behavioural Testing of NMT for Numerical Translation (Wang et al., 2021) | arXiv:2107.08357 | A |
| 53 | LLMs for Translation with Markup (Dabre et al., MT Summit 2023) | https://aclanthology.org/2023.mtsummit-research.13 | A |
| 54 | How Should Markup Tags Be Translated? (Hanneman and Dinu, WMT 2020) | DOI 10.18653/v1/2020.wmt-1.138 | V; S |
| 55 | Arabic numeral-noun agreement in MT (Google, Systran, Bing study) | search result only; not identified | S |
| 56 | When Can LLMs Actually Correct Their Own Mistakes? (Kamoi et al., TACL 2024) | arXiv:2406.01297 | A |
| 57 | LLMs Cannot Self-Correct Reasoning Yet (Huang et al., ICLR 2024) | arXiv:2310.01798 | A |
| 58 | Self-Refine (Madaan et al., 2023) | arXiv:2303.17651 | F (sections, incl. Appendix G) |
| 59 | TEaR (Feng et al., 2024) | arXiv:2402.16379 | A |
| 60 | Post-editing with error annotations (Ki and Carpuat, Findings of NAACL 2024) | arXiv:2404.07851 | A |
| 61 | Iterative Translation Refinement with LLMs (Chen et al.) | arXiv:2306.03856 | A |
| 62 | Translating Step-by-Step (Briakou et al., 2024) | arXiv:2409.06790 | A |
| 63 | TransAgents (Wu et al., TACL) | arXiv:2405.11804 | A |
| 64 | GEMBA-MQM (Kocmi and Federmann, WMT 2023) | arXiv:2310.13988 | A |
| 65 | Contrasting Linguistic Patterns in Human and LLM News Text (Muñoz-Ortiz et al., AI Review 2024) | arXiv:2308.09067 | A |
| 66 | Does Writing with LMs Reduce Content Diversity? (Padmakumar and He, ICLR 2024) | arXiv:2309.05196 | A |
| 67 | Standardizing the Measurement of Text Diversity (Shaib et al., AACL 2025) | arXiv:2403.00553 | A |
| 68 | GLTR (Gehrmann et al., ACL 2019 demo) | arXiv:1906.04043 | A |
| 69 | Inference in an Authorship Problem (Mosteller and Wallace, JASA 1963) | DOI 10.1080/01621459.1963.10500849 | V |
| 70 | Delta (Burrows, LLC 2002) | DOI 10.1093/llc/17.3.267 | V |
| 71 | MTLD, vocd-D and HD-D (McCarthy and Jarvis, BRM 2010) | DOI 10.3758/BRM.42.2.381 | V |
| 72 | MATTR (Covington and McFall, J. Quant. Linguistics 2010) | DOI 10.1080/09296171003643098 | V |
| 73 | Variation across Speech and Writing (Biber, 1988) | DOI 10.1017/CBO9780511621024 | V |
| 74 | Corpus Linguistics and Translation Studies (Baker, 1993) | DOI 10.1075/z.64.15bak | V |
| 75 | A New Approach to the Study of Translationese (Baroni and Bernardini, LLC) | DOI 10.1093/llc/fqi039 | V |
| 76 | On the Features of Translationese (Volansky, Ordan, Wintner, DSH 2015) | DOI 10.1093/llc/fqt031 | A |
| 77 | Post-editese (Toral, MT Summit 2019) | arXiv:1907.00900 | A |
| 78 | Machine Translationese (Vanmassenhove et al., EACL 2021) | arXiv:2102.00287; DOI 10.18653/v1/2021.eacl-main.188 | A; V |
| 79 | Lost in Literalism (Li et al., 2025) | arXiv:2503.04369 | A |
| 80 | LQM: Linguistically Motivated MQM (Magdy et al., ACL 2026) | arXiv:2604.18490 | A |
| 81 | AL-QASIDA (Robinson et al., 2024) | arXiv:2412.04193 | A |
| 82 | Mediating Punctuation in English-Arabic Translation (Alqinai) | https://journal.equinoxpub.com/JALPP/article/view/13241 | S |
| 83 | English calques in MSA (Bader 1994; Occasional Papers 2022) | search results only | S |
| 84 | Unicode CLDR 49 number data (cldr-json) | https://github.com/unicode-org/cldr-json | M (data read) |
| 85 | UAX #9 Unicode Bidirectional Algorithm (rev. 52) | https://www.unicode.org/reports/tr9/ | M |
| 86 | Having Beer after Prayer? (Naous et al.) | arXiv:2305.14456 | A |
| 87 | A Watermark for LLMs (Kirchenbauer et al., ICML 2023) | arXiv:2301.10226 | A |
| 88 | On the Reliability of Watermarks (Kirchenbauer et al., ICLR 2024) | arXiv:2306.04634 | A |
| 89 | My AI Safety Lecture (Aaronson, 2022) | https://scottaaronson.blog/?p=6823 | Fx (first part) |
| 90 | Robust Distortion-free Watermarks (Kuditipudi et al., TMLR) | arXiv:2307.15593 | A |
| 91 | Undetectable Watermarks (Christ, Gunn, Zamir) | arXiv:2306.09194 | A |
| 92 | Scalable watermarking (SynthID-Text) (Dathathri et al., Nature 2024) | DOI 10.1038/s41586-024-08025-4; PMID 39443777 | A (Europe PMC record) |
| 93 | SynthID Text documentation (Google) | https://ai.google.dev/responsible/docs/safeguards/synthid | M |
| 94 | Transformers generation utilities (WatermarkingConfig, SynthID) | https://huggingface.co/docs/transformers/main/en/internal/generation_utils | M |
| 95 | Provably Robust Watermarks for Open-Source LMs (Christ et al., 2024) | arXiv:2410.18861 | A |
| 96 | On the Learnability of Watermarks (Gu et al., ICLR 2024) | arXiv:2312.04469 | A |
| 97 | Watermarks in the Sand (Zhang et al., ICML 2024) | arXiv:2311.04378 | A |
| 98 | Paraphrasing evades detectors (Krishna et al., NeurIPS 2023) | arXiv:2303.13408 | A |
| 99 | Can AI-Generated Text be Reliably Detected? (Sadasivan et al., TMLR) | arXiv:2303.11156 | A |
| 100 | Fast-DetectGPT (Bao et al., ICLR 2024) | arXiv:2310.05130 | A |
| 101 | Binoculars (Hans et al.) | arXiv:2401.12070 | A |
| 102 | M4 benchmark (Wang et al.) | arXiv:2305.14902 | A |
| 103 | Style as a Confound (Park et al., EMNLP 2026) | arXiv:2608.26710 | A |
| 104 | Arabic AI-text detection and diacritics (Alshammari and Elleithy, Information 2024) | DOI 10.3390/info15070419 | V; S |
| 105 | OpenAI AI classifier withdrawal note | https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/ (403 when fetched) | S |
| 106 | EU AI Act, Regulation (EU) 2024/1689 | http://data.europa.eu/eli/reg/2024/1689/oj; Art. 50 via https://artificialintelligenceact.eu/article/50/ | M |
| 107 | Digital Omnibus on AI (reported Regulation (EU) 2026/1744) | law-firm summaries, e.g. https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/ | S |
| 108 | CometKiwi-22 model card | https://huggingface.co/Unbabel/wmt22-cometkiwi-da | M |
| 109 | CometKiwi (Rei et al., WMT 2022) | arXiv:2209.06243 | A |
| 110 | xCOMET (Guerreiro et al., TACL) | arXiv:2310.10482 | A |
| 111 | XCOMET-XL model card | https://huggingface.co/Unbabel/XCOMET-XL | M |
| 112 | xCOMET-lite (Larionov et al., EMNLP 2024) | arXiv:2406.14553 | A |
| 113 | xCOMET-lite model card | https://huggingface.co/myyycroft/XCOMET-lite | M |
| 114 | MetricX repository (incl. MetricX-24 citation, WMT 2024 pp. 492-504) | https://github.com/google-research/metricx | M |
| 115 | MetricX-24 Hybrid Large model card | https://huggingface.co/google/metricx-24-hybrid-large-v2p6 | M |
| 116 | Are LLMs Breaking MT Metrics? WMT24 Metrics (Freitag et al.) | DOI 10.18653/v1/2024.wmt-1.2 | F |
| 117 | To Ship or Not to Ship (Kocmi et al., WMT 2021) | arXiv:2107.10821 | F (sections) |
| 118 | Revisiting Round-Trip Translation for QE (Moon et al., EAMT 2020) | arXiv:2004.13937 | A |
| 119 | Rethinking Round-Trip Translation (Zhuo et al., Findings of ACL 2023) | arXiv:2209.07351 | A |
| 120 | BERTScore (Zhang et al., ICLR 2020) | arXiv:1904.09675 | A |
| 121 | chrF (Popović, WMT 2015) | DOI 10.18653/v1/W15-3049 | V |
| 122 | LaBSE (Feng et al., ACL 2022) | arXiv:2007.01852 | A |
| 123 | LaBSE sentence-transformers card | https://huggingface.co/sentence-transformers/LaBSE | M |
| 124 | Detecting Over- and Undertranslations (Vamvas and Sennrich, ACL 2022) | arXiv:2203.01927 | A |

### Not verified or deliberately omitted

- Gemma 4 model card cites arXiv:2607.02770; this was not checked.
- Gemma 4 E4B quantised memory figures (BF16 17.9 GB, Q4_0 4.5 GB) come only from a search summary [S] and are omitted from the tables.
- Licences for Hunyuan-MT-7B, Mutarjim, Hala and Falcon-H1-Arabic were not confirmed from primary sources.
- No primary source was found for: CPU throughput of QE metrics; detector false-positive rates on machine-translated human text; quantisation effects on English-Arabic for a 4B model; LLM-specific Arabic calque or word-order rates; GEC evaluation of 3-4B models on academic English.
