# -*- coding: utf-8 -*-
"""Humanizer for small local models: proofread, translate, humanize and draft with checks.

Small models (3 to 4 billion parameters) cannot follow the full SKILL.md, and they drop numbers, citations
and negations more often than large models. This runner gives them one short task at a time and moves the
checking into code:

  1. Split the document into paragraphs. Code blocks, tables, display math and front matter stay untouched.
  2. Mask what must not change (numbers with units, citations, math, code, links, protected terms) as {{n}}.
  3. Writer: the model rewrites or translates one paragraph and writes several candidates.
  4. Checks in code: every mask back exactly once, no new numbers, negations kept, length in range,
     no chatbot residue, and a count of the AI-writing tells listed in SKILL.md.
  5. Repair: a candidate with problems goes back once with the list of problems.
  6. Meaning check: a second prompt compares source and candidate (SAME or CHANGED). Translations are
     back-translated first and also scored with chrF against the source.
  7. Choose the best passing candidate. If none passes, keep the original paragraph (proofread, humanize) or
     mark the paragraph for review (translate, draft), and say so in the audit file.

Any server with an OpenAI-compatible chat API works: llama.cpp server, Ollama, LM Studio, vLLM, or a hosted
frontier model. Nothing is sent anywhere except the base URL you give.

Examples
  python hzlocal.py proofread paper.md -o paper.edited.md --model qwen3:4b
  python hzlocal.py translate paper_en.md -o paper_ar.md --target Arabic --source English --glossary terms.tsv
  python hzlocal.py humanize draft.md -o draft.edited.md --protect terms.txt --audit draft.audit.json
  python hzlocal.py draft notes.md -o section.md --genre "results section of a journal article"
  python hzlocal.py flag kattrai.md -o kattrai.review.md --lang Tamil      (suggestions only, no rewriting)
  HZ_API_KEY=... python hzlocal.py proofread a.md -o b.md --base-url https://api.example.com/v1 --model big-model

Exit status: 0 all paragraphs passed; 3 some paragraphs were kept or marked for review; 1 server or input error.
"""
import argparse, hashlib, json, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request

VERSION = "0.2.0"
HERE = os.path.dirname(os.path.abspath(__file__))
PROMPTS = os.path.join(HERE, "prompts")

# ---------------------------------------------------------------------------------------------------- masks
UNIT = (r"(?:\s?(?:%|‰|°C|°F|°|K|kWh/m²(?:·yr)?|kWh|MWh|kW|W/m²·K|W/m·K|W/m²|W|kJ/kg·K|kJ/kg|J|kg/m³|kg|g|t|mm|cm|km|m²|m³|m|"
        r"MPa|GPa|kPa|Pa|kN|N|Hz|ms|s|min|h|days?|years?|ppm|dB|lx|ach|L/s))?(?![A-Za-z])")
NUM = r"[−-]?\d+(?:[.,]\d+)*"
MASKS = [
    ("code", r"`[^`\n]+`"),
    ("math", r"\$\$.+?\$\$|\$[^$\n]+\$|\\\(.+?\\\)"),
    ("link", r"\]\([^)\s]+\)|https?://[^\s)>\]]+|\b10\.\d{4,9}/[^\s)\]]+"),
    ("cite", r"\[\d+(?:\s*[,–-]\s*\d+)*\]|\[@[^\]]+\]"),
    ("cite", r"\((?:[A-Z][A-Za-z'\-]+(?: (?:et al\.|and|&) ?[A-Z]?[A-Za-z'\-]*)?,? (?:19|20)\d{2}[a-z]?(?:[;,] ?)?)+\)"),
    ("range", NUM + r"\s?[–-]\s?" + NUM + UNIT),
    ("number", r"(?<![A-Za-z0-9_])" + NUM + UNIT),
]
TOKEN = re.compile(r"\{\{\s*(\d+)\s*\}\}")


def mask(text, protect=(), keep_numbers=False):
    """Replace protected spans by {{n}}. Returns (masked text, list of originals). keep_numbers leaves numbers,
    ranges and units visible (translation into languages whose nouns agree with the number)."""
    spans = []

    def keep(m):
        spans.append(m.group(0))
        return "{{%d}}" % len(spans)

    for term in sorted(protect, key=len, reverse=True):
        if term:
            edge = r"\b" if term[0].isalnum() else ""
            text = re.sub(edge + re.escape(term) + (r"\b" if term[-1].isalnum() else ""), keep, text)
    for name, pat in MASKS:                  # existing placeholders match first, so their digits are never masked
        if keep_numbers and name in ("range", "number"):
            continue
        text = re.sub(r"\{\{\s*\d+\s*\}\}|" + pat, lambda m: m.group(0) if TOKEN.fullmatch(m.group(0)) else keep(m), text)
    return text, spans


def unmask(text, spans):
    return TOKEN.sub(lambda m: spans[int(m.group(1)) - 1] if 0 < int(m.group(1)) <= len(spans) else m.group(0), text)


# ---------------------------------------------------------------------------------------------------- checks
NEGATION = re.compile(r"\b(?:not|no|never|nor|none|neither|without|cannot)\b|n't\b", re.I)
HEDGE = re.compile(r"\b(?:may|might|could|likely|unlikely|possibl[ey]|probabl[ey]|suggests?|suggested|appears?|"
                   r"approximately|about|around|roughly|indicates?|potential(?:ly)?|perhaps)\b", re.I)
RESIDUE = re.compile(r"^\s*(?:Sure|Certainly|Of course|Great question|Here(?:'s| is| are) (?:the|your|a)\b[^:\n]*:?|"
                     r"(?:The )?(?:revised|edited|corrected|translated|rewritten) (?:text|paragraph|version)\s*:)|"
                     r"I hope this helps|Let me know if|Would you like|As an AI\b|I cannot assist", re.I | re.M)
TELLS = [  # SKILL.md section numbers in brackets; English output only
    ("em dash [8]", re.compile("\u2014")),
    ("not X but Y [1]", re.compile(r"\bnot (?:just|only|merely|simply)?\s?[^.;:]{1,60}?,?\s+but\b", re.I)),
    ("AI word [12]", re.compile(r"\b(?:delve[sd]?|delving|tapestry|testament|pivotal|intricate|intricacies|meticulous(?:ly)?|"
                                r"showcas(?:e|es|ed|ing)|underscor(?:e|es|ed|ing)|garner(?:s|ed)?|interplay|vibrant|bolstered|"
                                r"deep dive|crucial|additionally|enduring|landscape)\b", re.I)),
    ("stock framing [13-18]", re.compile(r"\b(?:it is (?:important|worth|crucial) to note|plays? a (?:key|crucial|vital|pivotal) role|"
                                         r"in today's|ever-evolving|a testament to|serves as a|stands as a)\b", re.I)),
    ("closer [2]", re.compile(r"(?:^|\n)\s*(?:In conclusion|In summary|Overall|Ultimately)\b,?", re.I)),
    ("bold label [19]", re.compile(r"\*\*[^*]{1,40}:\*\*")),
    ("curly quotes [21]", re.compile("[\u201c\u201d\u2018\u2019]")),
]
DIGITS = re.compile(r"\d+(?:[.,]\d+)*")
EASTERN = {ord(c): str(i) for i, c in enumerate("\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669")}
EASTERN.update({ord(c): str(i) for i, c in enumerate("\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9")})
EASTERN.update({0x066B: ".", 0x066C: ",", 0x2212: "-"})


def numbers_of(text):
    """Numbers as a sorted list, in Western digits, thousands separators removed."""
    t = TOKEN.sub(" ", unicodedata.normalize("NFC", text).translate(EASTERN))
    out = []
    for n in DIGITS.findall(t):
        if re.fullmatch(r"\d{1,3}(?:,\d{2,3})+(?:\.\d+)?", n):   # 100,000 and the Indian 1,00,000 alike
            n = n.replace(",", "")
        out.append(n)
    return sorted(out)


def finish_arabic(text, digits="keep"):
    """Arabic punctuation and one digit system, done in code: comma, semicolon and question mark after Arabic
    letters; no tatweel; optional Eastern Arabic digits outside Latin-script runs. Values are unchanged."""
    ar = "\u0600-\u06FF"
    text = text.replace("\u0640", "")
    text = re.sub(r"(?<=[%s])\s?," % ar, "\u060c", text)            # comma right after an Arabic word

    def mark(m):                                                     # ? and ; when their sentence is Arabic
        ends = [e.end() for e in re.finditer(r"[.!?\u061f](?:\s|$)|\n", text[:m.start()])]   # not decimal points
        start = ends[-1] if ends else 0
        return {"?": "\u061f", ";": "\u061b"}[m.group(1)] if re.search("[%s]" % ar, text[start:m.start()]) \
            else m.group(0)
    text = re.sub(r"\s?([?;])", mark, text)
    if digits == "arabic-indic":
        conv = str.maketrans("0123456789", "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669")

        def to_eastern(m):                                           # keep Latin digits inside Latin-script runs
            before = re.findall(r"[A-Za-z%s]" % ar, text[max(0, m.start() - 40):m.start()])
            if before and re.match(r"[A-Za-z]", before[-1]):
                return m.group(0)
            return m.group(0).replace(".", "\u066b").translate(conv)
        text = re.sub(r"(?<![A-Za-z0-9_/\[.-])\d+(?:\.\d+)?(?![A-Za-z0-9_/\]-])", to_eastern, text)
    elif digits == "latin":
        text = text.translate(EASTERN)
    return text


def edit_rate(a, b):
    """Share of words changed between two versions (0 = identical)."""
    import difflib
    return 1 - difflib.SequenceMatcher(None, a.split(), b.split(), autojunk=False).ratio()


LANG_CODES = {"english": "en", "arabic": "ar", "tamil": "ta"}
SCRIPTS = {"arabic": "[\u0600-\u06FF]", "tamil": "[\u0B80-\u0BFF]"}   # output languages checked by script


def strip_model_text(text):
    """Remove reasoning blocks, wrapping quotes or fences, and chatbot wrappers around the answer."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    text = re.sub(r"^```[a-zA-Z]*\n(.*)\n```$", r"\1", text, flags=re.S).strip()
    lines = text.split("\n")
    while lines and RESIDUE.match(lines[0]) and len(lines[0]) < 120:
        lines.pop(0)
    while lines and RESIDUE.search(lines[-1]) and len(lines[-1]) < 160:
        lines.pop()
    text = "\n".join(lines).strip()
    if len(text) > 1 and text[0] == text[-1] == '"' and text.count('"') == 2:
        text = text[1:-1]
    return text


def words(s):
    return len(re.findall(r"\w+", s))


def check(task, src_masked, cand, n_masks, english_out, src_had=(), out_lang="English", numbers_visible=False,
          max_edit=1.0):
    """Hard problems block a candidate; soft problems lower its score and trigger a repair round."""
    hard, soft = [], []
    cand, src_masked = unicodedata.normalize("NFC", cand), unicodedata.normalize("NFC", src_masked)
    seen = [int(t) for t in TOKEN.findall(cand)]
    missing = [i for i in range(1, n_masks + 1) if seen.count(i) == 0]
    doubled = [i for i in set(seen) if seen.count(i) > 1]
    extra = [i for i in seen if i < 1 or i > n_masks]
    if missing:
        hard.append("missing placeholders %s" % ", ".join("{{%d}}" % i for i in missing))
    if doubled or extra:
        hard.append("placeholders repeated or invented: %s" % ", ".join("{{%d}}" % i for i in sorted(set(doubled + extra))))
    bare = DIGITS.findall(TOKEN.sub(" ", cand))
    if numbers_visible:
        a, b = numbers_of(src_masked), numbers_of(cand)
        if a != b:
            lost = [x for x in set(a) if a.count(x) > b.count(x)]
            new = [x for x in set(b) if b.count(x) > a.count(x)]
            hard.append("numbers changed (missing: %s; added: %s)" % (", ".join(lost) or "none", ", ".join(new) or "none"))
    elif bare and task != "draft":
        hard.append("numbers written outside placeholders: %s" % ", ".join(bare[:5]))
    if task in ("proofread", "humanize") and english_out:      # cue lists exist for English only
        if len(NEGATION.findall(cand)) < len(NEGATION.findall(src_masked)):
            hard.append("a negation was removed")
        if len(HEDGE.findall(cand)) < len(HEDGE.findall(src_masked)):
            soft.append("a hedge (may, likely, about ...) was removed")
    if "\n\n" in cand.strip() and "\n\n" not in src_masked.strip():
        hard.append("the paragraph was split into several paragraphs")
    if task == "proofread":
        r = edit_rate(src_masked, cand)
        if r > max_edit:
            soft.append("edit rate %.0f%% is above %.0f%% for proofreading" % (100 * r, 100 * max_edit))
    if task in ("proofread", "humanize"):
        ratio = words(cand) / max(1, words(src_masked))
        if not 0.6 <= ratio <= 1.4:
            hard.append("length changed too much (%.0f%% of the source)" % (100 * ratio))
    if task == "translate":
        ratio = len(cand) / max(1, len(src_masked))
        if not 0.4 <= ratio <= 2.5:
            hard.append("length implausible for a translation (%.0f%% of the source)" % (100 * ratio))
    rx = SCRIPTS.get(out_lang.lower())
    if rx:
        plain = TOKEN.sub(" ", cand)
        own, latin = len(re.findall(rx, plain)), len(re.findall(r"[A-Za-z]", plain))
        if own < max(1, latin):
            hard.append("output is not mainly in %s script" % out_lang)
        stray = re.findall(r"[A-Za-z]{3,}", plain)
        if len(stray) > 6:
            soft.append("%d Latin-script words left untranslated (%s)" % (len(stray), ", ".join(stray[:4])))
    if out_lang.lower() == "tamil":
        if re.search("[\u0BE6-\u0BEF]", cand):
            soft.append("Tamil digits used; write numbers in Western digits as in the source")
        if "\u0964" in cand:
            soft.append("danda (\u0964) used; Tamil academic text uses the full stop")
        if DIGITS.search(src_masked) and re.search("\u0BB2\u0B9F\u0BCD\u0B9A|\u0B95\u0BCB\u0B9F\u0BBF|\u0BAE\u0BBF\u0BB2\u0BCD\u0BB2\u0BBF\u0BAF", cand):
            soft.append("number written as a word (lakh, crore or million); keep the digits of the source")
    if RESIDUE.search(cand):
        hard.append("chatbot wording left in the text")
    if english_out:
        for label, rx in TELLS:
            if label.startswith("curly") and "curly" in src_had:
                continue
            if label.startswith("bold") and "bold" in src_had:
                continue
            n = len(rx.findall(cand)) - (len(rx.findall(src_masked)) if task != "translate" else 0)
            if n > 0:                                      # count only tells the edit introduced
                soft.append("%s x%d" % (label, n))
    return hard, soft


def chrf(hyp, ref, n=6, beta=2.0):
    """Character n-gram F-score (Popovic 2015), 0 to 100; whitespace removed as in sacreBLEU's default."""
    h, r = re.sub(r"\s+", "", hyp), re.sub(r"\s+", "", ref)
    precs, recs = [], []
    for k in range(1, n + 1):
        hc, rc = {}, {}
        for i in range(len(h) - k + 1):
            hc[h[i:i + k]] = hc.get(h[i:i + k], 0) + 1
        for i in range(len(r) - k + 1):
            rc[r[i:i + k]] = rc.get(r[i:i + k], 0) + 1
        if not hc or not rc:
            continue
        m = sum(min(c, rc.get(g, 0)) for g, c in hc.items())
        precs.append(m / sum(hc.values())); recs.append(m / sum(rc.values()))
    if not precs:
        return 0.0
    p, rr = sum(precs) / len(precs), sum(recs) / len(recs)
    return 0.0 if p + rr == 0 else 100 * (1 + beta ** 2) * p * rr / (beta ** 2 * p + rr)


# ---------------------------------------------------------------------------------------------------- model
class Model:
    def __init__(self, base_url, model, api_key="", timeout=300, max_tokens=1200, no_think=False, seed=7):
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.model, self.key, self.timeout, self.max_tokens, self.no_think = model, api_key, timeout, max_tokens, no_think
        self.calls, self.seed = 0, seed

    def chat(self, system, user, temperature=0.2, max_tokens=None, structured=None):
        """structured=(source_code, target_code): TranslateGemma's format, one user entry and no system role."""
        if self.no_think and not structured:
            user += "\n/no_think"
        body = {"model": self.model, "temperature": temperature, "max_tokens": max_tokens or self.max_tokens,
                "seed": self.seed, "top_p": 1.0,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
        if structured:
            body["messages"] = [{"role": "user", "content": [{"type": "text", "source_lang_code": structured[0],
                                                              "target_lang_code": structured[1], "text": user}]}]
        req = urllib.request.Request(self.url, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json",
                                              **({"Authorization": "Bearer " + self.key} if self.key else {})})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as f:
                    out = json.loads(f.read().decode("utf-8"))
                self.calls += 1
                return strip_model_text(out["choices"][0]["message"]["content"] or "")
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:
                err = e
                time.sleep(2 * (attempt + 1))
        raise RuntimeError("model server error at %s: %s" % (self.url, err))


def load_prompt(name):
    with open(os.path.join(PROMPTS, name + ".txt"), encoding="utf-8") as f:
        return f.read().strip()


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------------------------------- document
def segments(text):
    """Yield (kind, text) blocks. Only 'prose' and 'heading' blocks are edited."""
    out, buf, fence = [], [], None
    lines = text.split("\n")
    i = 0
    if lines and lines[0].strip() == "---":                        # YAML front matter
        j = next((k for k in range(1, len(lines)) if lines[k].strip() == "---"), None)
        if j:
            out.append(("keep", "\n".join(lines[:j + 1]))); i = j + 1

    def flush():
        if buf:
            block = "\n".join(buf)
            if all(l.lstrip().startswith("|") for l in buf) or block.strip().startswith(("$$", "<", "![", "    ")):
                out.append(("keep", block))
            elif re.match(r"^#{1,6} ", block) and len(buf) == 1:
                out.append(("heading", block))
            else:
                out.append(("prose", block))
            buf.clear()

    for line in lines[i:]:
        if fence is not None:
            out[-1] = ("keep", out[-1][1] + "\n" + line)
            if line.strip().startswith(fence):
                fence = None
            continue
        m = re.match(r"^\s*(```|~~~)", line)
        if m:
            flush(); out.append(("keep", line)); fence = m.group(1); continue
        if not line.strip():
            flush(); out.append(("blank", line)); continue
        buf.append(line)
    flush()
    return out


# ---------------------------------------------------------------------------------------------------- pipeline
def run_segment(task, kind, text, m, args, ctx):
    """Edit one block. Returns (text, record)."""
    head = ""
    if kind == "heading":
        head, text = re.match(r"^(#{1,6} )(.*)$", text, re.S).groups()
        if task != "translate":
            return head + text, {"kind": kind, "status": "unchanged"}
    out_lang0 = args.target if task == "translate" else args.lang
    keep_numbers = task == "translate" and not out_lang0.lower().startswith("english") and not args.mask_numbers
    masked, spans = mask(text, ctx["protect"], keep_numbers)
    budget = max(args.max_tokens, 3 * len(text) if not out_lang0.lower().startswith("english") else len(text))
    tg = ((args.source_code or LANG_CODES.get(args.source.lower(), args.source[:2].lower())),
          (args.target_code or LANG_CODES.get(args.target.lower(), args.target[:2].lower()))) \
        if task == "translate" and args.writer_format == "translategemma" else None
    src_had = tuple(x for x, rx in (("curly", "[\u201c\u201d\u2018\u2019]"), ("bold", r"\*\*")) if re.search(rx, text))
    out_lang = args.target if task == "translate" else args.lang
    english_out = out_lang.lower().startswith("english")
    note = ctx["lang_notes"].get(out_lang.title(), "")
    system = ctx["system"][task] + ("\nLanguage: %s. %s" % (out_lang, note)
                                    if task == "translate" or not english_out else "")
    if task == "translate":
        terms = [g for g in ctx["glossary"] if g[0].lower() in text.lower()]
        note_g = ("Use these term translations exactly:\n" + "\n".join("%s = %s" % g for g in terms) + "\n") if terms else ""
        prev = ctx.get("prev")
        note_p = ("Previous paragraph, for context only; do not translate it again:\n%s\n%s\n\n" % prev) if prev else ""
        user = "%sTranslate from %s into %s.\n%s\nText:\n%s" % (note_p, args.source, args.target, note_g, masked)
    elif task == "draft":
        user = "Write the %s in %s from these notes.\nNotes:\n%s" % (args.genre, args.lang, text)
    else:
        user = "Text:\n" + masked
    rec = {"kind": kind, "source_sha": sha(text), "masks": len(spans), "candidates": []}
    best = None
    for c in range(args.candidates):
        if tg:
            cand = m.chat("", masked, temperature=0.0, max_tokens=budget, structured=tg)
        else:
            cand = m.chat(system, user, temperature=args.temperature + 0.3 * c, max_tokens=budget)
        hard, soft = check(task, masked if task != "draft" else text, cand, len(spans) if task != "draft" else 0,
                           english_out, src_had, out_lang, keep_numbers, args.max_edit_rate)
        if task == "draft":
            hard += draft_facts(text, cand)
        rounds = 0
        while (hard or soft) and rounds < (0 if tg else args.repairs):     # TranslateGemma takes no instructions
            rounds += 1
            fix = ctx["repair"] + "\nProblems:\n- " + "\n- ".join(hard + soft) + "\n\nYour text:\n" + cand
            cand2 = m.chat(system, user + "\n\n" + fix, temperature=args.temperature, max_tokens=budget)
            hard2, soft2 = check(task, masked if task != "draft" else text, cand2,
                                 len(spans) if task != "draft" else 0, english_out, src_had, out_lang, keep_numbers,
                                 args.max_edit_rate)
            if task == "draft":
                hard2 += draft_facts(text, cand2)
            if (len(hard2), len(soft2)) <= (len(hard), len(soft)):
                cand, hard, soft = cand2, hard2, soft2
        final = unmask(cand, spans)
        if task == "translate" and out_lang.lower() == "arabic":
            final = finish_arabic(final, args.digits)
        if task == "translate":
            low = unicodedata.normalize("NFC", final).lower()
            soft += ["glossary term not used: %s = %s" % g for g in terms
                     if unicodedata.normalize("NFC", g[1]).lower() not in low]
        crec = {"text": final, "hard": hard, "soft": soft, "repairs": rounds}
        if task == "proofread":
            crec["edit_rate"] = round(edit_rate(text, final), 3)
        if not hard and not args.no_meaning_check:
            crec.update(meaning_check(task, text, final, m, args, ctx))
        crec["score"] = (0 if hard else 1, 1 if crec.get("meaning", "SAME") == "SAME" else 0,
                         crec.get("chrf", 0.0), -len(soft))
        rec["candidates"].append(crec)
        if best is None or crec["score"] > best["score"]:
            best = crec
        if not hard and not soft and crec.get("meaning", "SAME") == "SAME" and task != "translate":
            break
    ok = not best["hard"] and best.get("meaning", "SAME") == "SAME"
    if task == "translate":
        ctx["prev"] = (text, best["text"])
    if ok:
        rec["status"] = "ok"; rec["chosen"] = rec["candidates"].index(best)
        return head + best["text"], rec
    if task in ("proofread", "humanize"):
        rec["status"] = "kept_original"
        return head + text, rec
    rec["status"] = "needs_review"; rec["chosen"] = rec["candidates"].index(best)
    return head + best["text"], rec


def draft_facts(notes, out):
    """A draft may not add numbers, citations or links that are not in the notes, nor drop a number."""
    hard = []
    n_notes, n_out = set(DIGITS.findall(notes)), set(DIGITS.findall(out))
    new = sorted(n_out - n_notes)
    lost = sorted(n_notes - n_out)
    if new:
        hard.append("numbers not in the notes: %s" % ", ".join(new[:6]))
    if lost:
        hard.append("numbers from the notes missing: %s" % ", ".join(lost[:6]))
    for label, pat in (("citations", r"\[\d+(?:[,–-]\d+)*\]|\([A-Z][A-Za-z\-]+(?: et al\.)?,? (?:19|20)\d{2}\)"),
                       ("links", r"https?://\S+|\b10\.\d{4,9}/\S+")):
        add = set(re.findall(pat, out)) - set(re.findall(pat, notes))
        if add:
            hard.append("%s not in the notes: %s" % (label, ", ".join(sorted(add)[:4])))
    return hard


def meaning_check(task, src, cand, m, args, ctx):
    """Second opinion from a separate prompt (optionally a separate model). Translations are back-translated."""
    judge = ctx["judge_model"] or m
    out = {}
    if task == "translate":
        back_sys = ctx["system"]["translate"] + "\nLanguage: %s. %s" % (
            args.source, ctx["lang_notes"].get(args.source.title(), ""))
        back = judge.chat(back_sys, "Translate from %s into %s.\nText:\n%s" % (args.target, args.source, cand),
                          temperature=0.0)
        out["back_translation"] = back
        out["chrf"] = round(chrf(back, src), 1)
        a, b = src, back
    elif task == "draft":
        a, b = src, cand
    else:
        a, b = src, cand
    q = ctx["judge_draft"] if task == "draft" else ctx["judge"]
    verdict = judge.chat(q, "Text A:\n%s\n\nText B:\n%s" % (a, b), temperature=0.0)
    word = (re.findall(r"[A-Z]{4,}", verdict.upper()) or ["UNCLEAR"])[0]
    out["meaning"] = "SAME" if word in ("SAME", "SUPPORTED") else "CHANGED"
    out["meaning_note"] = verdict[:300]
    if task == "translate" and out["chrf"] < args.min_chrf:
        out["meaning"] = "CHANGED"
        out["meaning_note"] += " | back-translation chrF %.1f below %.1f" % (out["chrf"], args.min_chrf)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("task", choices=["proofread", "humanize", "translate", "draft", "flag"])
    ap.add_argument("input"); ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--base-url", default=os.environ.get("HZ_BASE_URL", "http://localhost:11434/v1"),
                    help="OpenAI-compatible endpoint (default: Ollama on this computer)")
    ap.add_argument("--model", default=os.environ.get("HZ_MODEL", "qwen3:4b"))
    ap.add_argument("--api-key-env", default="HZ_API_KEY", help="name of the environment variable holding a key")
    ap.add_argument("--judge-model", help="a different model for the meaning check (same server)")
    ap.add_argument("--source", default="English"); ap.add_argument("--target", default="English")
    ap.add_argument("--lang", default="English", help="language of the text for proofread, humanize and draft "
                    "(English, Arabic, Tamil, or any language the model writes well)")
    ap.add_argument("--glossary", help="TSV: source term<TAB>target term, one per line")
    ap.add_argument("--protect", help="file of exact terms to keep unchanged, one per line")
    ap.add_argument("--genre", default="paragraphs of a journal article")
    ap.add_argument("--candidates", type=int, default=2); ap.add_argument("--repairs", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=0.2); ap.add_argument("--min-chrf", type=float, default=45.0)
    ap.add_argument("--no-meaning-check", action="store_true"); ap.add_argument("--no-think", action="store_true",
                    help="append /no_think for models with a reasoning mode (Qwen3)")
    ap.add_argument("--max-tokens", type=int, default=1200, help="minimum token budget per call; longer or "
                    "non-Latin paragraphs get more")
    ap.add_argument("--mask-numbers", action="store_true", help="mask numbers in translation too (default: numbers "
                    "stay visible for non-English targets and are checked in code)")
    ap.add_argument("--digits", choices=["keep", "latin", "arabic-indic"], default="keep",
                    help="digit system for Arabic output")
    ap.add_argument("--max-edit-rate", type=float, default=0.4, help="proofreading: flag a larger share of changed words")
    ap.add_argument("--escalate-model", help="model that retries paragraphs the first model could not pass "
                    "(for example a larger local model or a hosted frontier model)")
    ap.add_argument("--escalate-base-url", help="server of the escalation model (default: --base-url)")
    ap.add_argument("--escalate-key-env", default="HZ_ESCALATE_KEY")
    ap.add_argument("--writer-format", choices=["chat", "translategemma"], default="chat",
                    help="translategemma: send TranslateGemma's structured entry with language codes; needs "
                         "--judge-model, because that model takes no instructions")
    ap.add_argument("--source-code"); ap.add_argument("--target-code")
    ap.add_argument("--audit", help="write a JSON record of every candidate and check")
    a = ap.parse_args(argv)
    if os.path.abspath(a.output) == os.path.abspath(a.input):
        ap.error("never overwrite the input")
    if a.writer_format == "translategemma" and not (a.judge_model or a.no_meaning_check):
        ap.error("--writer-format translategemma needs --judge-model (an instruction model for the meaning check)")
    text = open(a.input, encoding="utf-8").read()
    protect = [l.strip() for l in open(a.protect, encoding="utf-8")] if a.protect else []
    gloss = []
    if a.glossary:
        for line in open(a.glossary, encoding="utf-8"):
            if "\t" in line:
                s, t = line.rstrip("\n").split("\t", 1); gloss.append((s.strip(), t.strip()))
    key = os.environ.get(a.api_key_env, "")
    m = Model(a.base_url, a.model, key, max_tokens=a.max_tokens, no_think=a.no_think)
    ctx = {"protect": protect + [s for s, _ in gloss] if a.task != "translate" else protect,
           "system": {t: load_prompt(t) for t in ("proofread", "humanize", "translate", "draft", "flag")},
           "glossary": gloss,
           "lang_notes": json.load(open(os.path.join(PROMPTS, "languages.json"), encoding="utf-8")),
           "repair": load_prompt("repair"), "judge": load_prompt("judge"), "judge_draft": load_prompt("judge_draft"),
           "judge_model": Model(a.base_url, a.judge_model, key, max_tokens=400, no_think=a.no_think) if a.judge_model else None}
    if a.task == "draft":
        blocks = [("prose", b) for b in re.split(r"\n(?=#{1,6} )", text) if b.strip()]
    else:
        blocks = segments(text)
    out, recs = [], []
    esc = (Model(a.escalate_base_url or a.base_url, a.escalate_model, os.environ.get(a.escalate_key_env, ""),
                 max_tokens=a.max_tokens, no_think=a.no_think) if a.escalate_model else None)
    for kind, block in blocks:
        if a.task == "flag" and kind == "prose":
            note = ctx["lang_notes"].get(a.lang.title(), "")
            tips = m.chat(ctx["system"]["flag"] + ("\nLanguage: %s. %s" % (a.lang, note) if note else ""),
                          "Text:\n" + block, temperature=0.0)
            out.append("> " + block.replace("\n", "\n> ") + "\n\n" + tips)
            recs.append({"kind": kind, "status": "flagged", "source_sha": sha(block), "suggestions": tips})
            continue
        if kind in ("prose", "heading"):
            new, rec = run_segment(a.task, kind, block, m, a, ctx)
            if esc is not None and rec["status"] in ("kept_original", "needs_review"):
                new2, rec2 = run_segment(a.task, kind, block, esc, a, ctx)
                rec["escalation"] = rec2
                if rec2["status"] == "ok":
                    new, rec = new2, dict(rec2, escalated_from=rec)
            out.append(new); recs.append(rec)
            print("[%d/%d] %s" % (len(recs), sum(k in ("prose", "heading") for k, _ in blocks), rec["status"]),
                  file=sys.stderr)
        else:
            out.append(block)
    joined = ("\n\n" if a.task == "draft" else "\n").join(out)
    with open(a.output, "w", encoding="utf-8") as f:
        f.write(joined if joined.endswith("\n") else joined + "\n")
    summary = {s: sum(r["status"] == s for r in recs)
               for s in ("ok", "kept_original", "needs_review", "unchanged", "flagged")}
    summary["escalated"] = sum(1 for r in recs if "escalated_from" in r)
    if a.audit:
        audit = {"tool": "hzlocal", "version": VERSION, "task": a.task, "model": a.model,
                 "judge_model": a.judge_model or a.model, "server": urllib.parse.urlsplit(a.base_url).netloc,
                 "settings": {k: getattr(a, k) for k in ("candidates", "repairs", "temperature", "min_chrf",
                                                         "source", "target", "lang", "genre", "no_think",
                                                         "digits", "mask_numbers", "max_edit_rate", "escalate_model")},
                 "prompt_sha256": {k: sha(v) for k, v in ctx["system"].items()}, "model_calls": m.calls,
                 "summary": summary, "segments": recs}
        with open(a.audit, "w", encoding="utf-8") as f:
            json.dump(audit, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary), file=sys.stderr)
    return 3 if summary["kept_original"] or summary["needs_review"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as e:
        print(e, file=sys.stderr); sys.exit(1)
