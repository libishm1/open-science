---
name: tamil-translator
description: Professional English↔Tamil document translation with automatic language detection, OCR from scanned images/WhatsApp photos, line-by-line bilingual drafts, and a polished final Tamil (or English) version. Use when the user asks to translate documents or images between English and Tamil, mentions Tamil OCR, government orders (G.O./அரசாணை), legal/revenue documents, or asks for line-by-line translation.
compatibility: Claude, Codex, local models, Herdr and Omarchy. Runs on Windows, macOS and Linux.
---

# Tamil Translator (English ↔ Tamil)

Professional document translation workflow modeled on how a human professional translator works: detect → transcribe → draft → refine → finalize. Works on text files, pasted text, and scanned images (photos of documents, WhatsApp images, PDFs).

## Quick start (for small local models)

1. Detect the source language of each paragraph.
2. If the input is an image, transcribe it first. Mark unreadable words as [unclear].
3. Write a line-by-line bilingual draft.
4. Refine the target text for natural phrasing. Keep names, numbers and order numbers unchanged.
5. Deliver the final text and list any [unclear] items for review.

## Workflow

### Step 1 — Ingest & detect languages
- Read every source image/file with the Read tool (it performs vision OCR on images natively — no external OCR library needed).
- If pages are rotated/sideways, still transcribe them; note orientation.
- Determine correct page order from page numbers, continuation markers (`//p.t.o//`, para numbering), and content flow — WhatsApp filenames rarely match page order.
- **Detect and report the language mix**: which portions are English, which are Tamil (e.g., Tamil calendar date lines like "சுபகிருது வருடம், சித்திரை 27, திருவள்ளுவர் ஆண்டு 2053" in TN Government Orders). Text already in the target language is retained as-is, marked "(already Tamil in source — retained)".

### Step 2 — Transcribe (OCR pass)
- Produce a faithful English/Tamil transcription of each page, preserving structure: headings, numbered paragraphs, sub-clauses (i)(ii)(iii), a)/b), addresses, signature blocks.
- Preserve original typos but flag them: transcribe as-is, then add a translator's note (e.g., "If should be ensured" → intended "It should be ensured"; "rocky outcome" → "rocky outcrop"). Translate per intended meaning.

### Step 3 — Draft 1: line-by-line bilingual draft
- For every sentence/line: source line in **bold**, then `➤` and the target-language rendering directly below.
- Keep clause numbering, layout, and document register identical to the source.
- Save as `<docname>_bilingual_draft.md` in the working directory.

### Step 4 — Draft 2 → Final: polished target-language-only version
- Rewrite as a clean, publication-ready document entirely in the target language, in official register (formal written Tamil / செந்தமிழ் administrative style for government documents).
- Save as `<docname>_final_tamil.md` (or `_final_english.md`).
- Show the final version inline in the chat as well.

## Conventions (professional TN Government / legal register)

- Retain technical English terms in parentheses on first occurrence for legal precision: துறப்பு (relinquishment), ஒதுக்கீடு (assignment), இடையக மண்டலம் (buffer zone), திறந்தவெளி இட ஒதுக்கீடு (open space reservation).
- Keep numbers, dates, section references (26(A), LD3(1)), road classes (MDR/SH/NH), and PIN codes unchanged.
- Keep proper-name initials in Latin script (திரு. N. முருகானந்தம்), as done in official bilingual G.O.s.
- Add a "Translator's notes" section at the end listing corrected source typos and any ambiguous readings.

## Glossary — Tamil Nadu Government / Revenue terminology

| English | Tamil |
|---|---|
| Government Order — G.O.(Ms) | அரசாணை (நிலை) |
| Abstract | சுருக்கம் |
| Order / Read: | ஆணை / படிக்கப்பட்டது:- |
| Revenue Standing Order (RSO) | வருவாய் நிலையான ஆணை |
| Revenue and Disaster Management Department | வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை |
| Land Disposal Wing | நிலக் கையளிப்புப் பிரிவு |
| Principal Secretary to Government | அரசு முதன்மைச் செயலாளர் |
| Special Secretary | சிறப்புச் செயலாளர் |
| Commissioner of Land Administration | நில நிர்வாக ஆணையர் |
| District Collector | மாவட்ட ஆட்சியர் |
| District Revenue Officer | மாவட்ட வருவாய் அலுவலர் |
| Section Officer | பிரிவு அலுவலர் |
| Secretariat | தலைமைச் செயலகம் |
| Special Personal Assistant to Minister | அமைச்சர் அவர்களின் சிறப்பு நேர்முக உதவியாளர் |
| I.A.S. | இ.ஆ.ப. |
| Thiru / Tmt. | திரு. / திருமதி |
| patta land | பட்டா நிலம் |
| poramboke | புறம்போக்கு |
| land exchange | நிலப் பரிமாற்றம் |
| alienation / transfer | நிலமாற்றம் / உரிமை மாற்றம் |
| consolidation (of land) | நில ஒருங்கிணைப்பு |
| guideline value | வழிகாட்டு மதிப்பு |
| market value | சந்தை மதிப்பு |
| encumbrance | வில்லங்கம் |
| encroachment | ஆக்கிரமிப்பு |
| litigation / dispute | வழக்கு / சர்ச்சை |
| clear title | தெளிவான உரிமை |
| possession | உடைமை |
| holdings / landholdings | நில உடைமைகள் |
| block of land | நிலத் தொகுதி |
| parcel | நிலத் துண்டு |
| extent (of land) | (நில) அளவு |
| assessed / unassessed waste | தீர்வை செய்யப்பட்ட / செய்யப்படாத தரிசு |
| water course / water ways | நீர்வழிப் பாதை |
| water bodies, odais, kalams, meikkals | நீர்நிலைகள், ஓடைகள், களங்கள், மேய்க்கால்கள் |
| relinquishment | துறப்பு |
| assignment | ஒதுக்கீடு |
| Major District Road / State Highway / National Highway | முக்கிய மாவட்டச் சாலை / மாநில நெடுஞ்சாலை / தேசிய நெடுஞ்சாலை |
| buffer zone | இடையக மண்டலம் |
| Eco Sensitive Zone | சுற்றுச்சூழல் உணர்திறன் மண்டலம் |
| Hill Area Conservation Authority | மலைப்பகுதி பாதுகாப்பு ஆணையம் |
| Elephant/Tiger corridor | யானை/புலி வழித்தடம் |
| Forest Department | வனத்துறை |
| win-win situation | இரு தரப்புக்கும் நன்மை பயக்கும் சூழல் |
| By Order of the Governor | ஆளுநரின் ஆணைப்படி |
| Forwarded by order | ஆணைப்படி அனுப்பப்படுகிறது |
| Copy to / To | நகல் / பெறுநர் |
| applicant | விண்ணப்பதாரர் |
| local body | உள்ளாட்சி அமைப்பு |
| public authority | பொது ஆணையம் |

## Output checklist
1. Language-detection summary (what was English, what was Tamil).
2. Draft 1 — bilingual line-by-line file saved to disk.
3. Final — polished target-language-only file saved to disk and shown in chat.
4. Translator's notes (typos corrected, ambiguities, page-order determination).
5. Offer a .docx/PDF conversion if the user needs an office format.
