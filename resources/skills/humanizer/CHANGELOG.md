# Changelog

## 3.3.0

- Added `local/hzlocal.py`, which applies the skill with small local models (3 to 4 billion parameters) or hosted models through any OpenAI-compatible API. Tasks: proofread, humanize, translate, draft and flag (list errors without rewriting). One paragraph at a time, it protects citations, math, code, links and protected terms, checks every candidate in code (numbers, placeholders, negations, length, script, chatbot wording, the tells the edit introduced), repairs once, asks a separate meaning check, back-translates translations with chrF, can escalate a failed paragraph to a larger model, and keeps the original or marks the paragraph for review.
- English, Arabic and Tamil: writing notes per language, numbers kept visible and checked for Arabic and Tamil targets, Arabic punctuation and digit system set in code, Tamil digit, danda and number-word checks, glossary use checked, and an optional TranslateGemma message format.
- Added `research/small-models.md`, `research/tamil.md` and `research/verification.md`: model choice, prompting, quantisation, translationese, watermarking and detection evidence for English, Arabic and Tamil, with an independent check of the claims the recommendations rest on.

## 3.2.0

- Added academic editing priorities and an evidence review covering venue differences, historical examples, citation tracing and evaluation design.
- Corrected the pre-ChatGPT authorship claim and qualified unvalidated pattern rankings.
- Added a tested local-model integration patch with conservative scientific checks and candidate audit trails.

## Earlier releases

Versions up to 3.1.0 are documented in the upstream project, [blader/humanizer](https://github.com/blader/humanizer/blob/main/CHANGELOG.md).
