# Research dossier addendum: Tamil

> **Verified 12 November 2026.** An independent pass checked the claims this document's recommendations rest on against primary sources; see [verification.md](verification.md). Corrections from that pass are applied below and marked *Verification note*.


Compiled 12 November 2026 as a companion to `research_dossier.md` (English and Arabic). This file does not repeat that dossier. Where a general point is already established there (runtimes, generic quantisation findings, prompt-format rules, generic QE metrics), this section refers to it by section number and adds only the Tamil-specific evidence.

---

## 6. Tamil

### 6.0 Evidence labels and scope

The labels are those of the main dossier (**F**, **Fx**, **M**, **A**, **S**, **V**, **I**). One label is added for this section:

| Label | Meaning |
|---|---|
| **R** | Measured by the compiler in this pass with a script and public data named in the text. Small samples; reproducible but not peer-reviewed. |

Tamil-specific source numbers (T1, T2, ...) refer to the source table at the end of this file. Sources already listed in the main dossier are cited as "dossier #n".

Four caveats apply throughout:

1. Almost all English-Tamil translation numbers come from developers' own reports or from shared-task organisers. No independent human evaluation of 3-4B general LLMs on English-Tamil was found.
2. Evidence is strongly skewed towards English-to-Tamil. For general 3-4B LLMs there is **no Tamil-to-English evaluation** in the sources found; for Tamil-to-English only the dedicated MT models (IndicTrans2, NLLB, MADLAD-400) have published numbers.
3. The test sets (FLORES-200, IN22, WMT24++) are general-domain or India-centric news, Wikipedia and conversation. None is academic engineering prose.
4. Tamil grammatical-error-correction (GEC) evidence rests on very small test sets (65 sentences in the only shared task).

---

### 6.1 Models for English-Tamil translation on a CPU laptop

#### 6.1.1 Candidate models

| Model | Size | Licence (from the model card) | Tamil coverage and directions | Input limit | CPU serving route | Label |
|---|---|---|---|---|---|---|
| IndicTrans2 en-indic / indic-en **dist-200M** | 211M per direction in the paper; card shows "0.3B params" | **MIT**; Hugging Face files gated behind an "accept conditions" form | 22 scheduled Indian languages incl. Tamil (`tam_Taml`); one model per direction | Card example uses `max_length=256`; separate RoPE variants handle "upto 2048 tokens" | Transformers on CPU with `IndicTransToolkit` pre/post-processing; CTranslate2 checkpoints shipped for the fairseq release; **no OpenAI-compatible server**, needs a small wrapper | M (T2, T3); F (T1) |
| IndicTrans2 en-indic / indic-en **1B** | ~1B | MIT | as above | as above | as above | M (T3); F (T1) |
| IndicTrans3-beta (AI4Bharat) | **Not stated on card**; built on Gemma 3 | **CC BY 4.0**; gated | Tamil listed as a primary language; English-Indic and Indic-English, sentence and document level | Not stated | Card gives only a vLLM script; no evaluation results | M (T4) |
| Sarvam-Translate | 4B (fine-tune of Gemma 3 4B IT) | **GPL-3.0** | Tamil among 22; open checkpoint supports **only English-Indic and Indic-English** (pivot through English for Indic-Indic) | 8K | Card shows `vllm serve` with an OpenAI client; GGUF and llama.cpp not mentioned | M (T5) |
| TranslateGemma 4B / 12B | 4B / 12B | Gemma Terms of Use | **Tamil appears only in the "Languages from English" SFT table**, i.e. English-to-Tamil; Tamil-to-English is not in the SFT pair lists | **2K input tokens** | Community GGUF builds exist (e.g. 42ailab); Ollama chat-template behaviour unverified | F (T7, appendix); M (dossier #7); S (T8) |
| NLLB-200 distilled 600M / 1.3B | 0.6B / 1.3B | **CC-BY-NC-4.0** | `tam_Taml` covered (evaluated in T1); any direction | Inputs capped at 512 tokens; card: "not intended to be used for document translation", "not released for production deployment" | CTranslate2 lists NLLB as supported; needs a wrapper for an OpenAI-style API | M (T9, T12); F (T1) |
| MADLAD-400 3B-MT | 3B (T5) | **Apache-2.0** | `ta` in the training and evaluation tables; any direction via a `<2ta>` prefix | Not stated | CTranslate2 supports T5 (a MADLAD conversion is not documented); card offers a Q4K GGUF (1.65 GB) for the Candle runtime; llama.cpp not mentioned | M (T10, T12); F (T11) |
| Gemma 3 4B IT | 4B | Gemma Terms of Use | Not named on the card; evaluated on English-to-Tamil in T6 | 128K | llama.cpp GGUF | F (T6) |
| Gemma 4 E4B | 4.5B effective | Apache-2.0 | Tamil not named on the card | 128K | GGUF | M (dossier #9); R (tokeniser, 6.3.7) |
| Tiny Aya Global / **Fire** | 3.35B | **CC-BY-NC-4.0** | Tamil in the South Asia cluster; the Fire card lists Tamil as a focus language | 8K | Quantisations for llama.cpp, Ollama, LM Studio linked from the card | F (T6); M (T13) |
| Qwen3-4B-Instruct-2507 | 4B | Apache-2.0 | Tamil listed in the Qwen3 language list (Dravidian group) | 262K | GGUF | M (T14); F (T6) |
| Qwen3.5-4B | 4B | Apache-2.0 | 201 languages | 262K | GGUF; thinking on by default | M (dossier #3); F (T6) |
| Sarvam-1 | Card text "2-billion parameter", Safetensors panel "3B" | **Sarvam non-commercial licence** | Tamil among 10 Indic languages | 8,192 | **Base text-completion model**; card: cannot be used directly as a chat or instruction-following model | M (T15) |
| Sarvam-M | 24B (Mistral Small 3.1 base) | Apache-2.0 | 11 language tags; Tamil not named | not checked | Thinking on by default (`enable_thinking`); quantisations linked; too slow for routine CPU use [I] | M (T16) |
| Sarvam-30B | MoE, 32B total, 2.4B active (non-embedding) | Apache-2.0 | "22 Indian languages"; Tamil not named; no translation results | Benchmarks run at 65,536 | Card lists quantisations for llama.cpp, Ollama, LM Studio; whether mainline llama.cpp supports the architecture was not verified | M (T17, T18) |
| Llama 3.2 3B Instruct | 3B | Llama 3.2 Community Licence | **Not supported**: officially English, German, French, Italian, Portuguese, Hindi, Spanish, Thai; other languages out of scope | 128K | | M (T19) |
| Phi-4-mini-instruct | 3.8B | MIT | **Not in the 23-language list** | 128K | | M (T20) |
| Aya Expanse 8B | 8B | CC-BY-NC-4.0 | **Not in its 23 languages** | 8K | | M (T21) |

#### 6.1.2 Evidence on English-Tamil translation quality

**(a) IndicTrans2 paper (Gala et al., TMLR 2023, arXiv:2305.16307) [F, Tables 12-14, 22, 26].** Primary metric chrF++ (0-100), Indic side tokenised with IndicNLP. The authors chose chrF++ because COMET's XLM-R base does not cover all 22 languages and BLEU penalises morphological variants [F].

| Test set | Direction | IT2 (1B) | NLLB 1.2B distilled | NLLB 54B MoE | Google | Azure | GPT-3.5 |
|---|---|---|---|---|---|---|---|
| IN22-Gen | en-ta | **49.5** | 47.0 | 47.5 | 48.5 | 49.4 | 34.0 |
| IN22-Gen | ta-en | **59.8** | 56.9 | 59.1 | 59.6 | 56.8 | 41.3 |
| FLORES-200 devtest | en-ta | **57.2** | 53.3 | 54.0 | 56.0 | 56.1 | not reported |
| FLORES-200 devtest | ta-en | 61.3 | 58.9 | 60.8 | **61.5** | 57.9 | not reported |
| IN22-Conv | en-ta | **39.1** | 37.2 | 37.1 | 38.7 | **39.1** | 29.7 |
| IN22-Conv | ta-en | 45.8 | 45.7 | **46.8** | **46.8** | 46.4 | 38.0 |

- The distilled 200M models lose little on Tamil: IN22-Gen ta-en 59.8 to 58.4 (-1.4), en-ta 49.5 to 49.3 (-0.2) [F, Table 22].
- Conversational text (IN22-Conv) scores 10-14 points lower than general text for every system, so spoken-style Tamil is harder for all of them [F].
- GPT-3.5 trailed IT2 by 15.5 (en-ta) and 18.5 (ta-en) chrF++ on IN22-Gen [F, Table 26]. This is an old LLM and says nothing about current models.

**(b) Tiny Aya report (Cohere Labs, arXiv:2603.11510) [F, Tables 21, 22, 24, 25 read in the arXiv HTML].** The only head-to-head of current 3-4B models on Tamil. English-to-Tamil only; chrF on a 0-1 scale (sacreBLEU default chrF, not chrF++); greedy decoding.

| Model | Flores en-ta | WMT24++ en-ta_IN | mDolly Tamil, judge mean | mDolly Tamil, naturalness | mArenaHard-v2 Tamil, judge mean |
|---|---|---|---|---|---|
| **TranslateGemma 4B** | **0.53** | **0.48** | not evaluated | not evaluated | not evaluated |
| Gemma 3 4B | 0.47 | 0.40 | **0.930** | **0.972** | **0.774** |
| Tiny Aya Global | 0.37 | 0.40 | 0.896 | 0.960 | 0.696 |
| Tiny Aya Fire (South Asia) | 0.30 | 0.40 | not evaluated | not evaluated | not evaluated |
| Tiny Aya Water / Earth | 0.31 / 0.26 | 0.34 / 0.37 | | | |
| Qwen3.5-4B | 0.28 | 0.30 | 0.824 | 0.883 | 0.747 |
| Ministral-3-3B | 0.28 | 0.16 | 0.739 | 0.797 | 0.709 |
| Qwen3-4B | 0.20 | 0.16 | 0.729 | 0.788 | 0.715 |
| SmolLM3-3B | 0.02 | 0.03 | 0.246 | 0.319 | 0.126 |

- The mDolly and mArenaHard scores come from a GPT-4.1 judge (averaged rubrics; naturalness is one rubric). The FastText language pass rate for Tamil was 0.94-0.995 across models (Gemma 3 4B: 0.99 on mDolly, 0.94 on mArenaHard) [F].
- Note: the PDF text layer of these tables is misaligned; the values above were taken from the HTML tables, which disagree with a naive PDF extraction [R, checked].
- It is not stated whether Qwen3.5-4B was run with thinking on.

**(c) TranslateGemma technical report (arXiv:2601.09012) [F, appendix Table 4 and Tables 5-7].** MetricX-24 on WMT24++ English-to-Tamil (lower is better; positions checked with a coordinate-level PDF extraction because the plain text layer is shifted):

| | 27B | 12B | 4B |
|---|---|---|---|
| TranslateGemma | 2.87 | 2.98 | 3.90 |
| Gemma 3 baseline | 3.53 | 3.83 | 5.04 |

Fine-tuning cut the 4B error score by about a quarter on Tamil, and the 12B TranslateGemma is close to the 27B. Tamil appears in the "Languages from English" list only (Table 6), together with Bengali, Gujarati, Kannada, Malayalam, Marathi, Punjabi, Telugu and Urdu, whereas Hindi is in the "both directions" list (Table 5) [F]. Tamil-to-English is therefore not a trained direction for TranslateGemma.

**(d) MADLAD-400 (Kudugunta et al., arXiv:2309.04662) [F, rows of Tables 17 and 19, coordinate-level extraction].** sacreBLEU BLEU/chrF:

| Test set | Direction | NLLB-54B | MT-3B | MT-7.2B | MT-10.7B |
|---|---|---|---|---|---|
| FLORES-200 | en-ta | 19.8 / 59.4 | 12.4 / 51.4 | 13.0 / 52.6 | 13.9 / 54.1 |
| FLORES-200 | ta-en | 36.8 / 62.8 | 30.9 / 57.4 | 32.3 / 58.0 | 33.1 / 59.3 |
| NTREX | en-ta | n/a | 7.8 / 45.1 | 8.3 / 45.3 | 8.4 / 45.8 |
| NTREX | ta-en | n/a | 27.3 / 53.5 | 28.4 / 54.0 | 29.4 / 54.9 |

The MADLAD MT models trail NLLB-54B by 5-8 chrF on Tamil in both directions.

**(e) ITEM benchmark (Yari et al., arXiv:2510.07061) [Fx].** Six Indian languages including Tamil; MT outputs from Command R+, GPT-4o mini, IndicBART and IndicTrans2. The authors report that IndicTrans2 "dominates MT for most languages", with GPT-4o mini ahead only in Hindi. Tamil-specific values are only in a heatmap figure and were not read.

**(f) Cross-paper comparison [I].** The metrics are not directly comparable (chrF++ with IndicNLP tokenisation in T1; plain sacreBLEU chrF in T6 and T11). NLLB-54B appears in both T1 and T11 on FLORES English-to-Tamil: 54.0 chrF++ versus 59.4 chrF, a gap of about 5 points caused by the metric set-up. Using it as an anchor:

- IndicTrans2 (57.2 chrF++) corresponds to roughly 62 chrF, which would place it several points above TranslateGemma 4B (53 chrF) and MADLAD-3B (51.4 chrF) on FLORES English-to-Tamil.
- For Tamil-to-English, IndicTrans2 (61.3 chrF++) and NLLB-54B lead; MADLAD-3B trails at 57.4 chrF.
- The rough ordering for English-to-Tamil at laptop scale is therefore IndicTrans2 > NLLB 1.3B > TranslateGemma 4B ≈ MADLAD-3B > Gemma 3 4B > Tiny Aya > Qwen3.5-4B > Qwen3-4B.
- This is an inference across papers, test-set versions and scoring scripts. It must be confirmed on the user's own text.

**(g) Models without Tamil numbers.** Sarvam-Translate's blog reports only an in-house evaluation (Gemini 2.5 Flash as judge on 1,000 documents per format category; pairwise human preference on 100 English documents against Gemma 3 27B, Llama 3.1 405B and Llama 4 Scout); no Tamil figure and no public benchmark [M, T5b]. It claims format preservation for Markdown, HTML, LaTeX and code, and warns that very large LaTeX or HTML files should be split [M]. IndicTrans3-beta has no evaluation on its card [M]. Sarvam-30B reports only LLM-judge win rates on its own "indivibe" prompts, without naming the comparison models [M, T18].

**(h) Shared tasks.** WMT20 had a Tamil-English news task (cited in T1) [F]. The WMT23 and WMT24 quality-estimation tasks include English-Tamil (6.4). No current WMT general-MT task with Tamil was found in this pass (see 6.7).

#### 6.1.3 Serving through an OpenAI-compatible API

- **Gemma-3-architecture models** (Gemma 3 4B, TranslateGemma, Sarvam-Translate, IndicTrans3-beta): llama.cpp `llama-server` as in dossier 1.5 [I]. Community TranslateGemma GGUFs exist [S]. TranslateGemma needs its structured user message (`source_lang_code`, `target_lang_code`, text) [M], and the Ollama `hf.co` route may substitute a generic template [S]. The safest route is `llama-server` with the embedded Jinja template, or `/v1/completions` with the prompt string built by the tool [I].
- **IndicTrans2, NLLB, MADLAD-400** are encoder-decoder models. CTranslate2 supports NLLB and T5 but provides no HTTP server [M]. A small FastAPI wrapper exposing `/v1/chat/completions` (one model per direction, sentence splitting, IndicTransToolkit pre/post-processing) is needed [I]. No evidence was found that `llama-server` serves T5-family models; treat that route as unverified.
- **Sarvam-Translate**: the card's own route is vLLM's OpenAI server [M]. vLLM on CPU is possible but GPU-first (dossier 1.5).

---

### 6.2 Tamil proofreading and grammatical error correction

#### 6.2.1 Datasets, shared tasks and models

| Resource | What it is | Size | Licence / access | Label |
|---|---|---|---|---|
| **IndicGEC shared task, BHASHA 2025** (Bhattacharyya et al.) | Sentence-level GEC for Hindi, Bangla, Telugu, Tamil, Malayalam; essays written in 20 minutes under proctored conditions, corrected by experts; four categories (spelling, word, punctuation, multiple) | **Tamil: 91 train / 16 dev / 65 test sentences** | Data on GitHub (BHASHA-Workshop/IndicGEC2025); licence not checked | F (T22) |
| Neural Tamil grammar error detection (Murugesapillai et al., PAIL 2021) | IndicBERT classifier for subject-predicate agreement errors; "first-ever grammar error annotated corpus for Tamil" | not stated in abstract | not checked | A (T25) |
| TamilSandhi (Yazhmozhi, Waller, Visser, SGAI AI-2025, LNCS 16301) | 12 vallinam-addition and 8 deletion rules from Tolkappiyam and Nannool (300 unit tests) plus an mBART model for one complex rule (*panbu thokai*); 10,434 annotated sentence pairs; mBART 97.9% exact match | rule library on PyPI (`tamilsandhi-toolkit`) | Software licence not stated on the portal; check the GitHub repository | A (T26) |
| TamilMayangoliSpell (same authors, DravidianLangTech 2026) | Context-sensitive errors between phonetically similar letters (ல/ள/ழ, ண/ந/ன, ர/ற); 30,000 synthetic sentence pairs; mT5 93.50% exact match | | not checked | A (T27) |
| TamilSpell corpus (University of Dundee) | 10.16M entries, 8.86M isolated errors: non-word, real-word, sandhi | | CC BY-NC 4.0 (per search snippet) | S (T28) |
| Contextual Tamil spelling and grammar correction (arXiv:2609.03273, 2026) | mT5-small and mBART-50 fine-tuned progressively on up to 657,720 synthetic pairs | 1,000-sentence diagnostic set | article CC BY 4.0; no code or data link | A (T29) |

#### 6.2.2 Results that bear on small LLMs

- **IndicGEC Tamil leaderboard** [F, T22]: best GLEU 91.57 (team AiMNLP), then 86.52, 86.30, 86.29, 86.03 and down to 84.48 (nine teams). Fine-tuned mT5 systems scored 84.5-86.0.
- **The winning Tamil system was Gemini-2.5-Flash, few-shot** (GLEU 91.57; GPT-4.1 mini 85.5-86.0; Llama-4-Maverick zero-shot 88.70, few-shot 85.62) [F, T23]. For the Dravidian languages, few-shot exemplars sometimes hurt Llama-4 [F].
- **Returning the input unchanged scores higher.** Vajjala (arXiv:2511.15260) computed the GLEU of copying the input to the output: **92.17 for Tamil**, above every Tamil submission, including the winner (91.57). For Tamil, Bangla and Malayalam "just returning the input without doing anything else gives a GLEU score close to 95". In Vajjala's own Gemma 3 runs, every model scored below the copy baseline except for Hindi. *Verification note:* in the shared task itself, Malayalam entries beat the baseline (96.02 and 95.06 against 94.42) and the Bangla and Telugu winners equalled it; Tamil is the only language where copying the input beat the winner [F, T24].
- In the same paper Gemma 3 4B, 12B and 27B were run zero-shot and few-shot through OpenRouter. The author describes the 4B model as having "some notion of grammar" (GLEU near 90 on Malayalam). Few-shot prompting mostly harmed results [F]. Tamil per-model values are in a figure only.
- **Data and metric problems**: about 30% of 100 sampled Telugu gold outputs contained errors; many inputs had several correct outputs or needed context from the previous sentence; GLEU varied from 85.3 to 100 for outputs differing by one or two Unicode characters [F, T24]. AiMNLP found that naive tokenisation distorts GLEU for Indic scripts and recommends the IndicNLP tokeniser. They also had to add an explicit "return the text unchanged if correct" instruction because models edited correct sentences [F, T23].
- **Tamil-LLaMA-7B-Instruct** reached 19.0% exact match zero-shot and 24.7% with three examples, **against a 20.0% copy baseline**, while the fine-tuned mBART-50 reached 69.3% overall (sandhi 87.5%, subject-verb agreement 43.5%) [A, T29].
- **ILAKKANAM** (820 questions from Sri Lankan school Tamil examinations): Gemini 2.5 scored highest, open-source models lagged, and all models declined as linguistic complexity increased. The authors suggest that performance "may be driven by exposure rather than genuine understanding" [A, T30].
- **Error profile of MT output** (IndicMT Eval, 6.4): Tamil was the only one of five languages where mistranslation was not the most common error type; accuracy and fluency errors were about equally frequent [F, T33].

#### 6.2.3 Assessment [I]

- No study shows that a 3-4B model can proofread Tamil reliably. In the two direct measurements found (IndicGEC Tamil, the 1,000-sentence diagnostic set), LLMs, even frontier ones, did not beat leaving the text unchanged on the official metric.
- Sandhi and *mayangoli* errors are handled best by rules or small fine-tuned seq2seq models, not by prompted LLMs.
- A small model should therefore **flag and explain**, never silently rewrite Tamil. Rewrites should come from the author, a deterministic rule with a stated reason, or a frontier model under the same minimal-edit constraints.

---

### 6.3 Written register, script and tokenisation

#### 6.3.1 Formal written versus spoken Tamil (diglossia)

- Tamil has had its standard written form since the 13th century. Growing diglossia has pushed the spoken dialects so far from the written standard that no single dialect serves as a common spoken medium; a spoken koiné ("Standard Spoken Tamil") is emerging, heard most clearly in films (Schiffman 1998, *Language in Society*) [A, T34].
- The *Reference Grammar of Spoken Tamil* (Schiffman, CUP 1999, ISBN 978-0-521-64074-9) describes spoken Tamil as radically different from the literary variety and gives an appendix of literary equivalents for spoken paradigms [V; the DOI listed for the book in Crossref, 10.1017/CBO9780511519925, resolves to Crossref's "deleted DOI" page, so cite by ISBN; T35].
- MT systems score far lower on conversational IN22-Conv than on written IN22-Gen (6.1.2a) [F].
- [I] For academic text the target is formal written Tamil (*eḻuttu tamiḻ*, often called *centamiḻ* in its high form). Typical spoken intrusions a checker can flag include:
  - spoken verb forms such as இருக்கு for இருக்கிறது, போச்சு for போயிற்று / போய்விட்டது, -ங்க for -ங்கள்;
  - the clipped locative -ல for -இல் (as in வீட்டுல for வீட்டில்);
  - the quotative -ன்னு for என்று.

  Such a list must be curated with a Tamil editor before use; no validated list was found.

#### 6.3.2 Sandhi (*puṇarcci*)

- Sandhi errors are spelling errors at word boundaries, caused by wrongly inserted or omitted hard consonants (*vallinam*: க், ச், த், ப்), for example அந்தப் பையன் versus அந்த பையன் [A, T26]. The PAIL 2021 authors describe the rule-based Vaani system as a partial grammar checker because it handles sandhi errors [A, T25].
- Rule inventories exist (12 addition and 8 deletion rules) [A, T26]. Fine-tuned seq2seq reaches 87.5% on sandhi sites [A, T29]. No evidence was found that prompted LLMs apply these rules reliably [I].
- [I] Sandhi interacts with term checks: a glossary term may appear with a doubled consonant at its right edge before the next word, or with a case suffix (6.6.3).

#### 6.3.3 Grantha letters, Sanskrit loans and pure Tamil (*taṉit tamiḻ*)

- Tamil has fewer consonants than other Indic scripts. Grantha-derived letters (ஜ, ஷ, ஸ, ஹ, and ஶ added in Unicode 4.1) are used for loans, and the conjuncts க்ஷ and ஸ்ரீ survive [F, T36]. The aytham ஃ is "frequently used as a modifying prefix before consonants used to represent foreign sounds", especially English loans, for example ஃப for /f/ [F, T36].
- The pure-Tamil movement, associated with Maraimalai Adigal from 1916, promoted Tamil-origin words over Sanskrit loans and Grantha letters. It is studied in Ramaswamy, *Passions of the Tongue* (UC Press 1997, DOI 10.1525/9780520918795), and its diaspora form in Das, "Purism across the Seas" (in *Linguistic Rivalries*, OUP 2016, DOI 10.1093/acprof:oso/9780190461775.003.0002) [V, T37, T38].
- [I] The choice between a Grantha or Sanskrit-derived form and a pure-Tamil equivalent is a stylistic and sometimes ideological choice of the author, not an error. Examples are ஜனநாயகம் / மக்களாட்சி (democracy), விஞ்ஞானம் / அறிவியல் (science) and ஷ / ச spellings. A proofreading tool must not "correct" either direction. It should follow the author's glossary and flag inconsistency within one document.

#### 6.3.4 English technical terminology in academic Tamil

- **Tamil Virtual Academy (TVA)**, Government of Tamil Nadu: a Technical Glossary in 27 subject areas (mathematics, physics and biology through engineering, social sciences and commerce), released on CD and in the TVA digital library, which offers English-Tamil equivalent search [M, T39]. Several TVA glossaries were uploaded to Tamil Wikisource [S]. No machine-readable bulk download was found.
- **Sorkuvai** (Tamil Nadu Government word-bank project, launched 2018-2019): sorkuvai.com / sorkuvai.tn.gov.in offers word look-up with English meanings and new coinages vetted by a scholarly panel, including medical and engineering terms. News reports give 1.4-1.55 million entries, and a monthly bulletin, *Solvayal*, publishes new equivalents [S, T40]. The official site refused connections during this pass.
- **Observed practice** [R]: three Tamil Wikipedia science articles (photosynthesis, climate change, computer; 4,970 words) contained 134 Latin-script tokens, mostly English terms or symbols in parentheses after the Tamil term (for example "Photosynthesis", "chlorophyll", "ATP", "NADPH"). They also used Sri Lankan terminology in places (e.g. காபனீரொக்சைட்டு rather than the Tamil Nadu form கார்பன் டை ஆக்சைடு).
- [I] Indian and Sri Lankan Tamil differ in technical vocabulary and some orthographic conventions. The tool should fix the variety in the prompt (as it fixes MSA for Arabic in dossier 2.8) and keep a variety-tagged glossary.

#### 6.3.5 Numerals and punctuation

- **Digits.** The Unicode Standard encodes modern Tamil decimal digits at U+0BE6-U+0BEF. It warns that some are confusable with letters: ௧/க (one/ka), ௨/உ (two/u), ௭/எ (seven/e), ௮/அ (eight/a). Distinct numerals for 10, 100 and 1000 (U+0BF0-0BF2) are "used for historical numbers" [F, T36].
- **CLDR for `ta`**: default numbering system `latn` (Western digits), native `tamldec`, traditional `taml`. Decimal pattern `#,##,##0.###` (Indian lakh/crore grouping), percent `#,##,##0%` [M, T41].
- **Observed** [R]: the Tamil UDHR (1,280 words) has 57 Western digits and 0 Tamil digits; the Wikipedia sample has 331 Western and 0 Tamil. Numbers carry case or ordinal suffixes directly, as in "10ம் திகதி".
- **Punctuation.** Unicode notes that danda and double danda "used with Tamil" are encoded in the Devanagari block [F, T36]. Neither sample contained a danda; both used the Western full stop (78 and 343 occurrences) [R]. [I] Modern Tamil prose uses Western punctuation (. , ? ! ; : and quotation marks). Danda in model output is an error to flag.

#### 6.3.6 Unicode pitfalls (all from the Unicode Standard, Ch. 12.6, unless marked) [F, T36]

| Pitfall | Detail | Tool action [I] |
|---|---|---|
| Two-part vowels | ொ U+0BCA ≡ ெ+ா (0BC6 0BBE); ோ U+0BCB ≡ ே+ா (0BC7 0BBE); ௌ U+0BCC ≡ ெ+ௗ (0BC6 0BD7). The single code point is "the preferred form and the form in common use". These are canonical equivalents | Normalise every input and output to NFC before comparing, diffing or counting |
| **Visually identical, not canonically equivalent** | ஔ (0B94) and ௌ (0BCC) decompose with U+0BD7 AU LENGTH MARK, which "looks exactly like" ள U+0BB3 LLA. So ஒ+ள and ெ+ள render like ஔ and ௌ but are different text; NFC does not merge them | Never auto-convert. ெ+ள is the normal spelling of common words: in the Wikipedia sample all 42 instances were legitimate (வெளி, தெளிவு, வெள்ளை), against 3 genuine ௌ [R]. Flag only lexicon-listed AU words written with ள (e.g. மெளனம் for மௌனம்) |
| Independent vowel misspelt from parts | Use ஆ U+0B86, not அ+ூ (0B85 0BC2) | Flag |
| **Two encodings of ஸ்ரீ (shri)** | Before Unicode 4.1 `<0BB8 0BCD 0BB0 0BC0>`; afterwards `<0BB6 0BCD 0BB0 0BC0>`. "Both representations are widespread"; the standard recommends treating them as equivalent | Fold both to one form for matching, glossary checks and deduplication; preserve the author's form in output |
| Pulli versus anusvara | The pulli (virama, U+0BCD) may render as a small circle, but must not be encoded as U+0B82 TAMIL SIGN ANUSVARA | Flag U+0B82 inside words |
| க்ஷ and ZWNJ | Kssa is traditionally a ligature, now often shown with a visible pulli; ZWNJ after the pulli forces the visible form | Strip or keep ZWNJ/ZWJ consistently; do not count them as edits |
| Tamil digits confusable with letters | see 6.3.5 | Flag Tamil digits in output unless the author uses them |
| Old and reformed letter shapes | Traditional ligatures for ணா, றா, னா and ணை, லை, ளை, னை differ from the modern shapes only in rendering (same code points). Ra-ligature shapes differ between India, Malaysia/Singapore and Sri Lanka | No text change needed; a font issue only. OCR of older print may mis-recognise these |
| Legacy 8-bit fonts | Pre-Unicode Tamil fonts (TSCII, TAM/TAB, Bamini) produce Latin-looking text when extracted from PDFs | [I, not verified from a source] Detect a low Tamil-block ratio in text that should be Tamil and refuse to process it |

One decomposed vowel was found in the 15,299-character UDHR text; the Wikipedia extract was already NFC [R].

#### 6.3.7 Tokenisation cost [R]

Tokens per whitespace word, measured with each model's `tokenizer.json` (Hugging Face `tokenizers` 0.23.3). Samples: the Tamil and English Universal Declaration of Human Rights from the NLTK `udhr2` corpus (parallel; 1,280 Tamil / 1,747 English words) and 4,970 words of Tamil Wikipedia science text. Gemma 3, Llama 3.2 and Tiny Aya tokenisers were taken from public mirrors (unsloth, 1-800-LLMs) because the originals are gated. Script: not included.

| Tokeniser | Vocab | Tamil UDHR tok/word | English UDHR tok/word | Tamil/English tokens for the same text | Tamil Wikipedia tok/word | Tamil chars per token |
|---|---|---|---|---|---|---|
| Gemma 3 (also TranslateGemma, Sarvam-Translate) | 262K | 3.31 | 1.38 | **1.76** | 2.66 | 3.65 |
| Gemma 4 E4B | 262K | 3.31 | 1.38 | 1.76 | 2.66 | 3.65 |
| Sarvam-30B | 262K | 3.31 | 1.38 | 1.76 | 2.66 | 3.65 |
| Sarvam-1 | 68K | 3.32 | 1.58 | **1.54** | 2.65 | 3.66 |
| NLLB-200 | 256K | 3.07 | 1.26 | 1.78 | 2.91 | 3.35 |
| Tiny Aya Global | 261K | 3.28 | 1.27 | 1.89 | 2.88 | 3.38 |
| MADLAD-400 | 256K | 3.89 | 1.53 | 1.86 | 3.25 | 2.99 |
| Phi-4-mini | 200K | 4.05 | 1.26 | 2.35 | 3.44 | 2.83 |
| Qwen3.5 | 248K | 5.40 | 1.31 | 3.03 | 4.54 | 2.14 |
| **Qwen3 (incl. Qwen3-4B-Instruct-2507)** | 152K | **12.03** | 1.28 | **6.91** | **10.38** | 0.94 |
| **Llama 3.2** | 128K | **15.21** | 1.26 | **8.82** | **12.83** | 0.76 |

- Gemma 3, Gemma 4 and Sarvam-30B produced identical counts on both samples. Whether Sarvam-30B shares Gemma's vocabulary was not checked.
- Qwen3 and Llama 3.2 fall back to roughly one token per Tamil character or per byte. The same Tamil content costs 7-9 times the tokens of its English original, and so 7-9 times the generation time and context. This alone disqualifies them for Tamil work on a CPU [I].
- Tamil has fewer, longer words than English (1,280 versus 1,747 words for the same UDHR text; 15,299 versus 12,321 characters) [R]. Length-ratio checks should therefore use characters or tokens, not words.
- [I] With Gemma-family tokenisers, TranslateGemma's 2K-token input holds roughly 600-750 Tamil words. A 150-word English paragraph (~200 Gemma tokens) needs about 350 output tokens in Tamil.
- Tamil-LLaMA added 16,000 Tamil tokens to Llama 2 for the same reason [A, T31]. Sarvam reports 1.4-2.1 tokens per word for Sarvam-1 across its languages [M, T15]. Petrov et al. (dossier #39) give the general cross-language disparity.

---

### 6.4 Quality estimation and checks for Tamil on a CPU

#### 6.4.1 Human-correlation evidence that includes Tamil

**WMT23 QE shared task, English-Tamil sentence-level DA** (Blain et al., DOI 10.18653/v1/2023.wmt-1.52) [F, Table 18 and Section 2]. Translations came from NLLB 1.3B. Sources were curated from the Anuvaad (general, healthcare, legal), NPTEL and Spoken Tutorial corpora, with LaBSE filtering at 0.85-0.99. Professional native translators scored 0-100.

| System | Spearman | Params | Note |
|---|---|---|---|
| HW-TSC | **0.775** | 6.9B, ensemble of 12 | winner |
| IOL Research | 0.740 | 0.59B, ensemble of 5 | |
| Unbabel-IST (CometKiwi-based) | 0.739 | 10.7B, ensemble of 4 | |
| SurreyAI (TransQuest) | 0.674 | 0.63B | |
| MMT | 0.547 | | |
| Baseline (COMET-QE, WMT21) | 0.507 | 0.57B | |

**WMT24 QE shared task, English-Tamil DA** (Zerva et al., DOI 10.18653/v1/2024.wmt-1.3) [F, Table 3; values checked against coordinates]. 1,000 new Tamil test segments; the Tamil set had fewer very bad and more moderate segments (DA 20-60).

| System | Spearman en-ta |
|---|---|
| HW-TSC | **0.683** (winner) |
| Unbabel (CometKiwi-based) | **0.675** (winner) |
| TMU-HIT | 0.603 |
| **Baseline = CometKiwi-22 (`wmt22-cometkiwi-da`)** | **0.592** |
| Pister Labs (prompted Llama 3.1) | 0.478 |

- Off-the-shelf CometKiwi-22, the encoder model usable on a CPU, reaches about 0.59 Spearman on English-Tamil. Fine-tuned ensembles reach 0.68-0.78. A prompted Llama 3.1 was clearly worse than CometKiwi-22 [F].
- In the WMT24 English-Tamil post-editing task, no automatic post-editing system significantly beat the unedited MT (TER 24.71). Systems edited only 3.8-4.8% of segments, with a precision (improved among changed segments) of 54-59% [F]. This is a warning against automatic "improvement" passes on Tamil.

**IndicMT Eval** (Sai B et al., ACL 2023, DOI 10.18653/v1/2023.acl-long.795) [F, Tables 1, 9, Section 3.4]. MQM annotations of English-to-Tamil outputs from 7 systems (IndicTrans, Google, Bing, NLLB, mT5, mBART, CVIT); Tamil inter-annotator Kendall 0.55. Segment-level Pearson / Kendall on Tamil:

| Metric (type) | Tamil Pearson / Kendall |
|---|---|
| COMET-MQM (reference-based) | **0.597 / 0.432** |
| COMET-QE-MQM (**reference-free**) | 0.571 / 0.399 |
| COMET-QE-DA (**reference-free**) | 0.531 / 0.391 |
| COMET-DA (reference-based) | 0.529 / 0.412 |
| BLEURT-20 | 0.491 / 0.374 |
| BERTScore with mBERT / IndicBERT / MuRIL | 0.413 / 0.281; 0.402 / 0.282; 0.410 / 0.290 |
| chrF++ | 0.361 / 0.250 |
| LaBSE embedding cosine (hypothesis vs reference) | 0.339 / 0.286 |
| SacreBLEU | 0.244 / 0.189 |
| LASER embedding cosine | 0.126 / 0.099 |
| PRISM | -0.040 / -0.040 |

- Values were taken with a coordinate-level PDF extraction, because the plain text layer shifts the row labels by one.
- Metrics captured accuracy errors better than fluency errors in all languages, and embedding-based scores were bunched at the top of their range, making individual scores uninterpretable [F].
- A Tamil-tuned Indic-COMET improved correlations modestly [F; exact values in a misaligned table, not quoted].

**ITEM** [Fx, T32]: across six languages including Tamil, the MT correlations (overall) were MetricX-24 0.343, GEMBA (GPT-4.1, reference-free) 0.331 and LaBSE 0.200. LLM-based evaluators aligned best as a group. Tamil-specific values were not read.

#### 6.4.2 Coverage of the CPU-feasible metrics (dossier 5.1)

| Metric | Tamil covered? | Tamil validation | Label |
|---|---|---|---|
| CometKiwi-22 (InfoXLM) | Yes | Spearman 0.592 (WMT24 en-ta) | F |
| COMET-QE (WMT20/21) | Yes | 0.507 Spearman (WMT23 en-ta); Pearson 0.53-0.57 against MQM (IndicMT Eval) | F |
| xCOMET-lite (mDeBERTa-v3) | not documented on card | none found | I |
| MetricX-24 Hybrid (mT5) | mT5 pretraining includes Tamil (not re-checked) | none for Tamil; TranslateGemma uses MetricX-24-QE as a reward and reports en-ta MetricX, which is not a validation | V; F |
| LaBSE | Yes (used by WMT23 organisers to filter en-ta pairs) | weak as a quality score (0.34 / 0.29 hypothesis-reference) but adequate for gross omission or misalignment | F |
| IndicBERT / MuRIL BERTScore | Yes | reference-based only; 0.40-0.41 Pearson | F |

#### 6.4.3 Back-translation with chrF

No Tamil-specific study of round-trip QE was found. The general evidence and cautions in dossier 5.2 apply. [I] For English-to-Tamil, the backward pass should use a model from a different family, for example IndicTrans2 indic-en for a TranslateGemma or Gemma forward pass. chrF should then be computed on the English side (source versus back-translation). This avoids the Tamil tokenisation sensitivity documented for GLEU and BLEU (6.2.2) and IndicNLP-dependent chrF++. Use it as a ranking signal only.

---

### 6.5 Effect of 4-bit quantisation on Indic-script output

- **Marie and Fujita (arXiv:2508.20893) [Fx, T42].** Per-language tables cover Bengali and **Malayalam** (Dravidian, Brahmi-derived script, agglutinative; the nearest proxy for Tamil). Tamil itself is not reported.
  - English-to-X COMET, Qwen3-8B: full precision 76.1 (bn) / 57.9 (ml); GGUF Q4_K_M 75.2 / 56.4; AWQ 74.1 / 55.4; bitsandbytes 74.0 / 55.1.
  - Llama-3.3-70B Q4_K_M: 80.9 to 80.5 (bn), 67.6 to 67.2 (ml).
  - X-to-English, Llama-3.1-8B with bitsandbytes 4-bit: Bengali 72.2 to 64.5 and Malayalam 71.8 to 62.1, "collapses for the Indic pairs", against under 2 points for Japanese and French.
  - At 2-bit GGUF, Qwen3-8B English-to-Malayalam fell from 57.9 to 40.6.
  - The authors conclude that quantisation degrades "especially Indic languages", and that "the worse the baseline score of a language, the more it suffers".
- Marchisio et al. (dossier #26): non-Latin scripts lose most; automatic metrics understate human-perceived loss [F]. The Tiny Aya report (dossier #10) finds smaller Q4_K_M degradation for languages with more web data [Fx].
- An older study of BLOOMZ, Llama 2 and others on Arabic, English and Indic tasks found 4- and 8-bit quantisation "effective in maintaining model accuracy" [A, T43]. It predates current GGUF methods and does not report translation.
- No study measured Q4_K_M against Q8_0 for a 3-4B model on Tamil. [I] With 34 GB of RAM there is no memory reason to go below Q8_0 for 4B models (about 4-4.5 GB of weights) or below Q6_K for 12B (about 10 GB). Approximate GGUF sizes: 8.5 bits per weight for Q8_0, 6.6 for Q6_K, 4.8 for Q4_K_M. Keep GGUF K-quants; avoid bitsandbytes 4-bit for Tamil. For the small encoder-decoder MT models (200M-1.3B), run in FP32 or INT8 (CTranslate2) and test before using INT8.

---

### 6.6 Recommendations for the tool (Tamil)

#### 6.6.1 Model per task

| Task | Laptop default (34 GB RAM, CPU) | Quantisation | Step up (about 8-12B) | Frontier |
|---|---|---|---|---|
| **English to Tamil** | Run two candidates per paragraph and select with the checks in 6.6.3: **IndicTrans2 en-indic** (dist-200M, or 1B if speed allows; MIT; sentence-split) and **TranslateGemma 4B** (paragraph-level, under 2K tokens) | IndicTrans2 FP32 or CTranslate2 INT8 after a test; TranslateGemma **Q8_0** | TranslateGemma 12B, Q6_K (MetricX en-ta 2.98 vs 3.90 for 4B) | Escalate flagged paragraphs |
| **Tamil to English** | **IndicTrans2 indic-en** (dist-200M or 1B). Strongest published ta-en evidence; TranslateGemma has no trained ta-en direction | as above | IndicTrans2 1B; or Gemma 3 12B (Q6_K) as a second candidate, untested on ta-en | Escalate |
| **Tamil proofreading** | **Detection only.** Deterministic layer (Unicode, sandhi rules, register markers, numbers) plus Gemma 3 4B (Q8_0) asked to *list* suspected errors with reasons, never to rewrite | Q8_0 | Gemma 3 12B (Q6_K), still detection only | Rewrites only on request, minimal-edit, shown as tracked changes |
| **Tamil drafting** | Preferred: draft in English with the English model (dossier 1.6), then translate with the English-to-Tamil pipeline and its checks. Direct Tamil drafting: **Gemma 3 4B** (highest Tamil mDolly score and naturalness among 3-4B models) | Q8_0 | Gemma 3 12B (Q6_K); test Sarvam-30B (MoE, 2.4B active, Apache-2.0, efficient Tamil tokeniser) if llama.cpp supports it | Final polish |

**Exclude for Tamil:** Qwen3-4B-Instruct-2507 (the English default in dossier 1.6: chrF 0.20 en-ta and 10-12 tokens per Tamil word), Llama 3.2 3B (unsupported; 13-15 tokens per word), Phi-4-mini and Aya Expanse 8B (Tamil not supported), SmolLM3 and Sarvam-1 (base model only). Qwen3.5-4B is usable only as a last resort (chrF 0.28; 4.5-5.4 tokens per word).

**Licences:** IndicTrans2 MIT; MADLAD-400 Apache-2.0; Gemma-family Gemma Terms (Gemma 4 Apache-2.0); NLLB and Tiny Aya non-commercial; Sarvam-Translate **GPL-3.0**; IndicTrans3-beta CC BY 4.0. [I] Sarvam-Translate and IndicTrans3-beta are Gemma derivatives, so the Gemma Terms probably also apply; this was not confirmed. Do not bundle GPL or non-commercial weights in a redistributed tool; let the user download them.

**Before fixing the routing:** build a 40-60 paragraph English-Tamil test set from the user's own papers, translated or approved by a Tamil-speaking colleague. Compare IndicTrans2, TranslateGemma 4B, Gemma 3 4B and NLLB 1.3B on it with chrF, CometKiwi-22 and a blind preference judgement. The 6.1.2f ordering is an inference, not a measurement.

#### 6.6.2 Prompt rules for Tamil (additions to dossier 2.8)

1. **State variety and register explicitly**: "Translate into formal written Tamil as used in academic writing in Tamil Nadu, India. Do not use spoken or colloquial forms." Make Sri Lankan Tamil a user option. Give one or two user-approved example paragraphs, if any, in the same format.
2. **Terminology policy, chosen once by the author**:
   - (a) Tamil term with the English term in parentheses at first mention, then Tamil only (default, matching observed practice);
   - (b) English technical terms kept in Latin script;
   - (c) pure-Tamil coinages from the glossary.

   Pass only the glossary entries present in the paragraph, as "English term -> Tamil term" lines (dossier 2.4). For TranslateGemma, which accepts no free instructions in its template, enforce terms by post-check and repair, or route glossary-heavy paragraphs to Gemma 3 with an instruction prompt.
3. **Grantha and pure-Tamil choices**: "Keep the author's word choices. Do not replace Sanskrit-derived words with pure Tamil words or the reverse."
4. **Numbers**: "Write all numbers in Western digits exactly as in the source. Do not convert to Tamil digits, words, lakh or crore." Allow Tamil case or ordinal suffixes after a number or placeholder (e.g. `2020-ஆம்`, `⟦3⟧-இல்`) and tell the model this is permitted.
5. **Punctuation**: "Use Western punctuation (full stop, comma). Do not use ।."
6. **Proofreading prompt**: "List grammar, spelling and sandhi errors in this Tamil sentence as JSON {span, suggestion, reason}. If there is no error, return an empty list. Do not rewrite the sentence and do not change word choice or register."
7. **Decoding**: thinking off (Qwen3.5 and Sarvam models default to thinking on); T 0-0.2; fixed seed. Set `max_tokens` from the source token count: about 3 times the English source tokens for Gemma-family Tamil output (1.76 times measured, plus margin).
8. **Templates**: for TranslateGemma send `source_lang_code: "en"`, `target_lang_code: "ta"` (or `ta-IN`) in its structured format. Verify the template in the served GGUF; otherwise build the prompt string and call `/v1/completions`.

#### 6.6.3 Checks for Tamil (additions to dossier 5.6)

Deterministic, on every segment:
1. **NFC normalisation** of input and output before any diff, count or comparison. Fold both ஸ்ரீ encodings. Flag U+0B82 inside words, Tamil digits, danda and a low Tamil-block letter ratio (wrong language, legacy-font text).
2. **AU/LLA confusable**: flag only lexicon-listed AU words spelt with ள; never auto-replace ெ+ள.
3. **Numbers**: extract digit sequences even when glued to Tamil suffixes. Normalise Indian (1,00,000) and Western (100,000) grouping and decimal points. Compare multisets with the source. Flag லட்சம் / கோடி / மில்லியன் / ஆயிரம் in output when the source had digits.
4. **Glossary**: match the required Tamil term as a prefix of a word (Tamil attaches case suffixes and sandhi consonants). Exact-token matching will produce false alarms.
5. **Length**: Tamil/English character ratio, calibrated on the user's approved translations (about 1.24 in the UDHR sample [R]). Do not use word ratios.
6. **Register**: flag curated spoken-Tamil markers (6.3.1) in output meant to be formal.
7. **Proofreading guard**: compute the character-level edit rate per sentence. Treat "no change" as the expected default; it beat every system on the only Tamil GEC benchmark. Every suggested edit must carry a reason. Edits that only swap Grantha and pure-Tamil forms or change register are rejected.
8. **Sandhi**: run a rule-based sandhi checker (TamilSandhi rules, once its licence is confirmed) as a separate flagger. Its output is a suggestion, not an automatic fix.

Learned, optional:

9. **CometKiwi-22** per paragraph for ranking review (personal academic use; CC BY-NC-SA). It is the only CPU-size metric with a Tamil human-correlation figure (0.59 Spearman). MetricX-24 and xCOMET-lite have no Tamil validation; document that.
10. **LaBSE** source-target cosine, only for gross omission or misalignment.
11. **Round-trip** with a different model family, scored with chrF on the English side; tie-breaker only.

Thresholds are set on the user's own reviewed Tamil, separately per direction and model (dossier 5.6).

#### 6.6.4 What to escalate to a frontier model

1. Paragraphs that still fail a deterministic check after one targeted repair.
2. Paragraphs in the lowest-scoring 10-20% by CometKiwi-22 or where the two candidate translations disagree strongly (low chrF between them).
3. Any Tamil rewrite in proofreading (as opposed to flagging), and any paragraph where the small model's flags conflict with the sandhi rules.
4. Register and terminology decisions not covered by the glossary, including new coinages and Indian versus Sri Lankan forms.
5. Final polish of directly drafted Tamil text, and document-level consistency (terms, honorific level, tense).

Frontier models are not reliable Tamil proofreaders either. Gemini-2.5-Flash did not beat the copy baseline on IndicGEC Tamil, and ILAKKANAM accuracy fell with linguistic complexity. Frontier output therefore goes to the author as tracked changes, with the same checks applied.

---

### 6.7 Not verified, gaps and deliberate omissions

- No source evaluates any 3-4B general LLM on **Tamil-to-English**. No source evaluates Gemma 4, Sarvam-Translate, IndicTrans3-beta, Sarvam-30B or Sarvam-M on any public Tamil MT benchmark.
- No **human evaluation** of small LLMs on English-Tamil was found. The ITEM per-language human scores were not read (figure only).
- **TranslateGemma Tamil-to-English** quality is unknown. The direction is absent from its SFT tables, but the model may still translate it through Gemma 3's general ability.
- **llama.cpp support** for T5-family models in `llama-server`, and for the Sarvam-30B architecture, was not verified. CPU throughput was not measured for any model.
- **Licences not confirmed**: TamilSandhi toolkit, IndicGEC data, IndicTrans2 RoPE variants, and whether the Gemma Terms bind Gemma-derived models released under other licences.
- **WMT Indic shared tasks**: the 2023-2024 WMT "low-resource Indic" tasks are recalled as covering Assamese, Manipuri, Khasi and Mizo, not Tamil; this was not checked.
- **Sorkuvai and TVA**: no machine-readable glossary download was found; the Sorkuvai site refused connections; sizes come from news reports only.
- The spoken-Tamil marker list (6.3.1), the AU-word lexicon (6.3.6) and legacy-font detection are proposals, not validated resources.
- The tokeniser measurements use two small samples (UDHR legal register in Sri Lankan Tamil; three Wikipedia articles). Values for academic prose in Indian Tamil may differ by about ±15% [I].
- Three PDF tables (Tiny Aya, TranslateGemma Table 4, IndicMT Eval Table 1) have misaligned text layers. Values here come from the HTML tables or coordinate-level extraction. Anyone re-extracting with plain `pdftotext` will get different, wrong numbers.

---

## Source table (Tamil section)

| # | Source | Identifier | Access |
|---|---|---|---|
| T1 | IndicTrans2 (Gala et al., TMLR 2023) | arXiv:2305.16307 | F (Sections 6.3-7.1; Tables 12, 13, 14, 22, 26) |
| T2 | IndicTrans2 en-indic dist-200M model card | https://huggingface.co/ai4bharat/indictrans2-en-indic-dist-200M | M |
| T3 | IndicTrans2 GitHub README (licences, CT2, RoPE variants, IndicTransToolkit) | https://github.com/AI4Bharat/IndicTrans2 | M |
| T4 | IndicTrans3-beta model card | https://huggingface.co/ai4bharat/IndicTrans3-beta | M |
| T5 | Sarvam-Translate model card | https://huggingface.co/sarvamai/sarvam-translate | M |
| T5b | Sarvam-Translate blog | https://sarvam.ai/blogs/sarvam-translate | M (official blog) |
| T6 | Tiny Aya report (Cohere Labs, 2026) | arXiv:2603.11510 (HTML tables 1, 11, 21, 22, 24, 25) | F (tables); otherwise Fx in dossier #10 |
| T7 | TranslateGemma Technical Report | arXiv:2601.09012 | F (appendix A Table 4; appendix C Tables 5-7); A for main text |
| T8 | Community TranslateGemma GGUF; Ollama template thread | https://huggingface.co/42ailab/TranslateGemma-4B-GGUF ; https://discuss.huggingface.co/t/ollama-model-registry-provides-wrong-chat-template/176139 | S |
| T9 | NLLB-200 distilled 600M model card | https://huggingface.co/facebook/nllb-200-distilled-600M | M |
| T10 | MADLAD-400 3B-MT model card | https://huggingface.co/google/madlad400-3b-mt | M |
| T11 | MADLAD-400 (Kudugunta et al., NeurIPS D&B 2023) | arXiv:2309.04662 | F (Tables 17 and 19, Tamil rows only) |
| T12 | CTranslate2 Transformers guide | https://opennmt.net/CTranslate2/guides/transformers.html | M |
| T13 | Tiny Aya Fire model card | https://huggingface.co/CohereLabs/tiny-aya-fire | M |
| T14 | Qwen3 release blog (language list) | https://qwenlm.github.io/blog/qwen3/ | M |
| T15 | Sarvam-1 model card | https://huggingface.co/sarvamai/sarvam-1 | M |
| T16 | Sarvam-M model card | https://huggingface.co/sarvamai/sarvam-m | M |
| T17 | Sarvam-30B model card | https://huggingface.co/sarvamai/sarvam-30b | M |
| T18 | Sarvam 30B / 105B blog | https://www.sarvam.ai/blogs/sarvam-30b-105b | M (official blog) |
| T19 | Llama 3.2 3B Instruct model card | https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct | M |
| T20 | Phi-4-mini-instruct model card | https://huggingface.co/microsoft/Phi-4-mini-instruct | M |
| T21 | Aya Expanse 8B model card | https://huggingface.co/CohereLabs/aya-expanse-8b | M |
| T22 | Findings of the IndicGEC and IndicWG Shared Task at BHASHA 2025 (Bhattacharyya et al.) | https://aclanthology.org/2025.bhasha-1.12 | F |
| T23 | AiMNLP at BHASHA Task 1 IndicGEC (De, Kumar, Arun Prakash) | arXiv:2511.20120 | F |
| T24 | IndicGEC: Powerful Models, or a Measurement Mirage? (Vajjala) | arXiv:2511.15260 | F |
| T25 | Neural-based Tamil Grammar Error Detection (Murugesapillai et al., PAIL 2021) | https://aclanthology.org/2021.pail-1.4 | A |
| T26 | TamilSandhi: Neuro-Symbolic Toolkit for Sandhi Errors (Yazhmozhi, Waller, Visser; LNCS 16301) | DOI 10.1007/978-3-032-11402-0_18; PyPI `tamilsandhi-toolkit` | A (institutional abstract); PyPI page did not load |
| T27 | TamilMayangoliSpell (Yazhmozhi, Waller, Visser; DravidianLangTech 2026) | DOI 10.18653/v1/2026.dravidianlangtech-1.6 | A |
| T28 | TamilSpell corpus (University of Dundee) | https://discovery.dundee.ac.uk/en/datasets/tamilspell-a-tamil-spelling-error-corpus/ | S (search snippet) |
| T29 | Contextual Tamil Spelling and Grammar Correction (Karthikeyan A et al., 2026) | arXiv:2609.03273 | A |
| T30 | From Phonemes to Meaning: ILAKKANAM (Varsha et al., 2025) | arXiv:2511.12387 | A |
| T31 | Tamil-Llama (Balachandran, 2023) | arXiv:2311.05845 | A |
| T32 | ITEM: Revisiting Metric Reliability ... in Indian Languages (Yari et al.) | arXiv:2510.07061 | Fx (HTML, first 100k characters) |
| T33 | IndicMT Eval (Sai B et al., ACL 2023) | DOI 10.18653/v1/2023.acl-long.795; arXiv:2212.10180 | F (Sections 3-6; Tables 1, 9) |
| T34 | Standardization or restandardization: the case for "Standard" Spoken Tamil (Schiffman, *Language in Society* 27, 1998) | DOI 10.1017/S0047404500020017 | A |
| T35 | A Reference Grammar of Spoken Tamil (Schiffman, CUP 1999) | ISBN 978-0-521-64074-9 (Crossref DOI 10.1017/CBO9780511519925 resolves to "deleted DOI") | V; S (publisher description via search) |
| T36 | The Unicode Standard 15.0, Chapter 12.6 Tamil | https://www.unicode.org/versions/Unicode15.0.0/ch12.pdf | F |
| T37 | Passions of the Tongue (Ramaswamy, UC Press 1997) | DOI 10.1525/9780520918795 | V |
| T38 | Purism across the Seas (Das, in *Linguistic Rivalries*, OUP 2016) | DOI 10.1093/acprof:oso/9780190461775.003.0002 | V |
| T39 | Tamil Virtual Academy FAQ (Technical Glossary, digital library) | https://www.tamilvu.org/coresite/html/cwfaqqueen.htm | M |
| T40 | Sorkuvai project (news reports; official site unreachable) | e.g. https://www.dtnext.in/news/tamilnadu/tn-govt-to-create-corpus-of-tamil-words-for-technical-terms ; https://sorkuvai.tn.gov.in/ | S |
| T41 | Unicode CLDR `ta` numbers data (cldr-json) | https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-numbers-full/main/ta/numbers.json | M (data file via fetch tool) |
| T42 | The Uneven Impact of Post-Training Quantization in MT (Marie and Fujita) | arXiv:2508.20893 | Fx (HTML via fetch tool) |
| T43 | Towards Inclusive NLP: Compressed Multilingual Transformers (Alshehhi et al., 2025) | arXiv:2507.19699 | A |
| T44 | Findings of the WMT 2023 Shared Task on Quality Estimation (Blain et al.) | DOI 10.18653/v1/2023.wmt-1.52 | F (Section 2, Tables 5, 18) |
| T45 | Findings of the QE Shared Task at WMT 2024 (Zerva et al.) | DOI 10.18653/v1/2024.wmt-1.3 | F (Sections 3-4, 6; Tables 3, 5, 6) |
| T46 | WMT24++ (Deutsch et al., 2025): language list incl. `ta_IN` | arXiv:2502.12404 | F (language list only); A otherwise (dossier #24) |
| T47 | UDHR in Tamil and English (NLTK `udhr2` corpus), used for R measurements | https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/udhr2.zip | R (data) |
| T48 | Tamil Wikipedia articles ஒளித்தொகுப்பு, காலநிலை மாற்றம், கணினி (extracts via MediaWiki API, 12 Nov 2026), used for R measurements | https://ta.wikipedia.org/w/api.php | R (data) |
| T49 | Hugging Face `tokenizers` 0.23.3 and tokenizer.json files of the models in 6.3.7 (Gemma 3 via unsloth mirror, Llama 3.2 via unsloth mirror, Tiny Aya via 1-800-LLMs mirror) | https://huggingface.co/{model}/resolve/main/tokenizer.json | R |

Also relied on, from the main dossier: llama.cpp server README (dossier #29), Ollama docs (#30, #31), Marchisio et al. (#26), Petrov et al. (#39), CometKiwi-22 card (#108), xCOMET-lite card (#113), MetricX-24 card (#115), LaBSE card (#123), Gemma Terms (#8), Gemma 4 card (#9), Qwen3.5 card (#3), TranslateGemma card (#7).
