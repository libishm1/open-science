# Humanizer with small local models

`hzlocal.py` applies the Humanizer skill with a model of 3 to 4 billion parameters running on your own computer,
or with a hosted model. It proofreads, humanizes, translates, drafts and flags errors, in English, Arabic, Tamil
and other languages. Small models cannot follow the 5,000-word skill, and they drop numbers, citations and
negations more often than large models. The runner therefore gives the model one short task per paragraph and
does the checking in code.

It needs Python 3.9 or later and nothing else from pip.

## Quick start

1. Install a model server. Any server with an OpenAI-compatible chat API works:
   - [llama.cpp](https://github.com/ggml-org/llama.cpp): `llama-server -m model.gguf -c 8192 --port 8080`; the API is
     at `http://localhost:8080/v1`. Set the context size with `-c`.
   - [Ollama](https://ollama.com): `ollama pull <model>`; the API is at `http://localhost:11434/v1`. Its OpenAI API
     cannot set the context size, and the default is 4K tokens on machines with less than 24 GiB of video memory.
     Start the server with `OLLAMA_CONTEXT_LENGTH=8192 ollama serve`, or set `PARAMETER num_ctx 8192` in a Modelfile.
   - [LM Studio](https://lmstudio.ai): load a model, set its context length, and start the local server; the API is
     at `http://localhost:1234/v1`.
2. Pick a model from the table below.
3. Run a task:

```
python hzlocal.py proofread paper.md -o paper.edited.md --model <model> --audit paper.audit.json
python hzlocal.py humanize draft.md -o draft.edited.md --model <model> --protect terms.txt
python hzlocal.py translate paper_en.md -o paper_ar.md --source English --target Arabic --glossary terms.tsv --model <model>
python hzlocal.py translate paper_en.md -o paper_ta.md --source English --target Tamil --model <model>
python hzlocal.py flag kattrai.md -o kattrai.review.md --lang Tamil --model <model>
python hzlocal.py draft notes.md -o section.md --genre "results section of a journal article" --model <model>
```

Add `--base-url` for a server other than Ollama, and `--no-think` for models with a reasoning mode such as Qwen3.
For a hosted model, put the key in an environment variable (`HZ_API_KEY` by default) and give the provider's
OpenAI-compatible base URL. Nothing is sent anywhere except the URLs you give.

## Models

Choose on your own text before relying on any default: translate or edit 30 to 60 of your own paragraphs, have a
fluent colleague judge them, and keep the model that wins. The table reflects published evaluations, which are
mostly the developers' own; the sources and their verification are in [`../research/small-models.md`](../research/small-models.md)
and [`../research/tamil.md`](../research/tamil.md).

| Task | Default on a CPU laptop | Quantisation | Step up (8 to 12B) |
|---|---|---|---|
| English proofreading, humanizing, drafting | Qwen3-4B-Instruct-2507 (Apache-2.0) | Q4_K_M or better | Qwen3.5-9B with thinking off (`--no-think`) |
| English to Arabic | Gemma 3 4B instruct; or TranslateGemma 4B with `--writer-format translategemma` | Q6_K or Q8_0 | TranslateGemma 12B or Gemma 3 12B |
| Arabic to English | Gemma 3 4B instruct or TranslateGemma 4B | Q6_K or Q8_0 | TranslateGemma 12B |
| English to Tamil | TranslateGemma 4B (`--writer-format translategemma`) or Gemma 3 4B instruct | Q8_0 | TranslateGemma 12B (Q6_K) |
| Tamil to English | No 3 to 4B chat model has published results; IndicTrans2 (MIT) run outside this tool is the best-supported option | | IndicTrans2 1B |
| Arabic or Tamil proofreading | `flag` task (lists errors, never rewrites) with Gemma 3 4B instruct | Q8_0 | Gemma 3 12B, still `flag` |
| Tamil drafting | Draft in English, then translate | | Gemma 3 12B |

What the evidence says:

- In the only head-to-head of 3 to 4B models found (the Tiny Aya report, arXiv:2603.11510, FLORES chrF), English to
  Tamil scored 0.53 for TranslateGemma 4B, 0.47 for Gemma 3 4B and 0.20 for Qwen3-4B. Qwen3-4B also needs about seven
  times as many tokens for Tamil as for the same English text. Use it for English only.
- TranslateGemma (arXiv:2601.09012; Gemma Terms of Use; 2K input tokens) was trained on English to Arabic, Arabic
  to English and English to Tamil, but not Tamil to English. It accepts only a structured message with language
  codes and no instructions, so with `--writer-format translategemma` the runner sends no system prompt, skips the
  repair round, and needs `--judge-model` (an instruction model such as Gemma 3 4B) for the meaning check. This
  format is untested with live servers; check that yours passes the message through unchanged.
- Llama 3.2 3B does not officially support Arabic or Tamil. SmolLM3-3B and Ministral-3-3B were weakest on Arabic in
  that comparison. Tiny Aya (3.35B) is competitive but licensed for non-commercial use only.
- 4-bit quantisation costs more for non-Latin scripts and for smaller models, so use 6- or 8-bit files for Arabic and
  Tamil output. With 34 GB of RAM, a 4B model at Q8_0 runs on the CPU.
- Proofreading is the weakest area for small models in Arabic and Tamil. Fine-tuned correction models beat
  instruction-tuned ones in Arabic, and on the one Tamil benchmark returning the input unchanged scored higher than
  every system. Use `flag`, read the list, and correct by hand.
- IndicTrans2 (dedicated English and Indic translation models, MIT, distilled 200M and 1B versions) is probably the
  strongest English and Tamil translator that runs on a laptop, but it is not a chat model. Run it with its own
  tools and use `hzlocal.py proofread --lang Tamil` or `flag` on its output if you want the checks.

## What happens to each paragraph

1. **Split.** The document is split into paragraphs. Code blocks, tables, display math, images and YAML front
   matter are never sent to the model. Headings are translated but not otherwise edited.
2. **Protect.** Citations (`[12]`, `(Author et al., 2020)`), inline math, inline code, links, DOIs and your
   protected terms become placeholders such as `{{3}}`. Numbers with their units are masked too, except when
   translating into a language other than English: Arabic and Tamil words change form with the number, so the
   model sees the numbers and the code checks them afterwards (`--mask-numbers` overrides this).
3. **Write.** The task prompt (`prompts/<task>.txt`, 60 to 130 words) and, for Arabic and Tamil, a short writing
   note (`prompts/languages.json`) produce up to `--candidates` versions at rising temperature with a fixed seed.
   Translation also receives the glossary terms that occur in the paragraph and the previous paragraph as context.
4. **Check in code.** A candidate fails if a placeholder is missing, repeated or invented; if a number changed,
   appeared or vanished (Eastern Arabic digits and Indian or Western digit grouping compare as equal); if the
   paragraph was split; if it removed a negation (English); if its length changed implausibly; if chatbot wording
   is left in; or if a translation into Arabic or Tamil is not mainly in that script. It is marked down for removed
   hedges, a high edit rate in proofreading (`--max-edit-rate`), glossary terms not used, Tamil digits, the danda
   (।) or numbers written as words, and, in English, the tells from `SKILL.md` that the edit introduced.
5. **Repair.** A candidate with problems goes back once (`--repairs`) with the exact list of problems.
6. **Meaning check.** A separate prompt (`prompts/judge.txt`), optionally on a different model (`--judge-model`),
   answers SAME or CHANGED. Translations are first translated back into the source language and scored with chrF
   against the source; a score under `--min-chrf` (45 by default) counts as CHANGED.
7. **Choose.** The best candidate that passes is used. If none passes and `--escalate-model` is set, a larger or
   hosted model tries the paragraph once. Otherwise proofreading and humanizing keep the original paragraph, and
   translation and drafting mark it for review.
8. **Arabic finishing, in code.** Arabic comma, semicolon and question mark in Arabic sentences, no tatweel, and one
   digit system (`--digits keep|latin|arabic-indic`). Digits inside Latin-script runs such as "EnergyPlus 25.2" are
   left alone. Tamil text is never auto-corrected: one Tamil letter sequence looks like the "au" vowel but is normal
   spelling.

`draft` works on sections (split at headings) and adds two checks: no number, citation or link that is not in the
notes, and no number from the notes left out. `flag` sends each paragraph once and writes the paragraph followed by
the model's list of suspected errors; nothing is rewritten.

## Reading the result

- Exit status 0: every paragraph passed. 3: some paragraphs were kept or need review. 1: server or input error.
- `--audit file.json` records the model, server host, settings, prompt hashes, number of model calls and, for every
  paragraph, each candidate with its problems, repairs, edit rate, meaning verdict, back-translation and chrF.
- Read every paragraph marked `needs_review` and every `kept_original`. The share of unchanged paragraphs is not a
  quality measure: a system that never edits never fails.

## Limits

- **The checks catch what can be counted.** They catch dropped or changed numbers, citations, placeholders,
  negations in English, wrong script and inserted chatbot wording. They cannot catch a number attached to the wrong
  claim, a fluent mistranslation of an unprotected word, or a hedge expressed in words outside the English cue
  list. The meaning check is a small model's opinion; small models are weak at judging their own output, so use a
  different `--judge-model` and `--escalate-model` for text that matters.
- **Optional quality estimation is for ranking only.** CometKiwi-22 (non-commercial licence) reached a Spearman
  correlation of 0.59 with human judgement for English to Tamil at WMT24 (DOI 10.18653/v1/2024.wmt-1.3). Use such
  scores to choose which paragraphs to read first, with thresholds set on your own reviewed text.
- **Watermarks.** The published watermarking schemes act while the text is generated, through the sampler
  (Kirchenbauer et al., ICML 2023, arXiv:2301.10226; SynthID-Text, Dathathri et al., Nature 634:818-823, 2024,
  DOI 10.1038/s41586-024-08025-4). An open-weight model run through llama.cpp, Ollama or LM Studio applies none unless
  the operator adds one, and none of the model cards above documents a watermark in the weights. Hosted models may
  watermark their output. This tool neither adds nor removes watermarks.
- **AI-text detectors are not a target.** Across 13 detectors, false-positive rates on human-written academic text
  ranged from 0% to 100% (Park, Jeong and Kim, arXiv:2608.26710). A detector score says nothing about whether the
  meaning survived. The aim here is text that says exactly what the author meant, in the register of the field.
- **Disclosure stays with the author.** Journals ask authors to disclose AI-assisted editing, translation or drafting
  according to the operation performed (see the policies linked in [`../research/evidence-map.md`](../research/evidence-map.md)).
  In the EU, Article 50 of the AI Act (Regulation (EU) 2024/1689, applying from 2 August 2026) sets transparency
  duties for providers of generative systems and for deployers who publish AI-generated text on matters of public
  interest without human editorial responsibility; Regulation (EU) 2026/1744 gives generative systems already on the
  market before that date until 2 December 2026 to meet Article 50(2). Read the texts on EUR-Lex for your case.
- **No live benchmark yet.** The runner is tested against a fake server; it has not been evaluated with real models
  on a held-out set. Run the pilot above before trusting it with a manuscript.

## Files you can edit

| File | Purpose |
|---|---|
| `prompts/proofread.txt`, `humanize.txt`, `translate.txt`, `draft.txt`, `flag.txt` | Task prompts |
| `prompts/languages.json` | One writing note per output language; add a language by adding a line |
| `prompts/judge.txt`, `judge_draft.txt` | Meaning check prompts |
| `prompts/repair.txt` | The repair instruction |
| `terms.txt` (yours) | Exact terms to protect, one per line |
| `terms.tsv` (yours) | Glossary for translation: source term, tab, target term |

## Tests

```
python -m unittest discover -s tests -v
```

Nineteen tests run against a fake OpenAI-compatible server, so no model weights are needed. They cover masking, the
checks, repair, keeping the original, escalation, Arabic and Tamil translation with back-translation, visible and
changed numbers, Arabic finishing, the glossary, the TranslateGemma message format, Tamil proofreading, `flag`, and
drafting with an invented number.
