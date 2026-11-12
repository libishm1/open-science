# -*- coding: utf-8 -*-
"""Tests for hzlocal.py against a fake OpenAI-compatible server (no model weights needed).
Run: python -m unittest discover -s local/tests -v
"""
import http.server, json, os, sys, tempfile, threading, unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import hzlocal as H  # noqa: E402

REPLY = {"fn": None, "model": None}


class Fake(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        system, user = body["messages"][0]["content"], body["messages"][1]["content"]
        REPLY["model"] = body["model"]
        text = REPLY["fn"](system, user)
        out = json.dumps({"choices": [{"message": {"role": "assistant", "content": text}}]}).encode("utf-8")
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)

    def do_GET(self):                                # Ollama's model list, for --model auto
        out = json.dumps({"models": [{"name": n} for n in REPLY.get("tags", [])]}).encode("utf-8")
        self.send_response(200); self.send_header("Content-Length", str(len(out))); self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


def payload(user):
    """The paragraph sent to the writer: text after the last 'Text:' line."""
    return user.split("Text:\n")[-1].split("\n\n")[0].split("\n/no_think")[0]


def judge(system):
    return "compare two texts" in system


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.HTTPServer(("127.0.0.1", 0), Fake)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = "http://127.0.0.1:%d/v1" % cls.srv.server_port

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()

    def run_tool(self, task, text, *extra):
        d = tempfile.mkdtemp()
        src, out, aud = (os.path.join(d, n) for n in ("in.md", "out.md", "audit.json"))
        open(src, "w", encoding="utf-8").write(text)
        code = H.main([task, src, "-o", out, "--base-url", self.url, "--model", "m", "--audit", aud] + list(extra))
        return code, open(out, encoding="utf-8").read(), json.load(open(aud, encoding="utf-8"))


class Units(unittest.TestCase):
    def test_mask_roundtrip(self):
        t = "Savings of 3.5% at 24–36 °C [12] (Smith et al., 2020) in `run.py` with $x^2$ at https://a.b/c for Phase Change."
        m, spans = H.mask(t, ["Phase Change"])
        self.assertNotIn("3.5", m); self.assertNotIn("[12]", m); self.assertNotIn("Phase Change", m)
        self.assertEqual(H.unmask(m, spans), t)
        m2, _ = H.mask(t, keep_numbers=True)
        self.assertIn("3.5%", m2); self.assertIn("24–36 °C", m2); self.assertNotIn("[12]", m2)

    def test_checks(self):
        src = "The wall did not cool {{1}} and may help."
        hard, _ = H.check("proofread", src, "The wall cooled and may help.", 1, True)
        self.assertTrue(any("missing" in h for h in hard)); self.assertTrue(any("negation" in h for h in hard))
        hard, _ = H.check("proofread", src, "The wall did not cool 5 and may help {{1}}.", 1, True)
        self.assertTrue(any("outside placeholders" in h for h in hard))
        hard, soft = H.check("proofread", src, "The wall did not cool {{1}} — and may help.", 1, True)
        self.assertFalse(hard); self.assertTrue(any("em dash" in s for s in soft))

    def test_split_paragraph_and_introduced_tells(self):
        hard, soft = H.check("humanize", "It is crucial. It works.", "It is crucial.\n\nIt works.", 0, True)
        self.assertTrue(any("split" in h for h in hard))
        self.assertFalse(any("AI word" in x for x in soft))      # 'crucial' was already in the source

    def test_numbers_and_arabic_finishing(self):
        hard, _ = H.check("translate", "It saved 4.3%.", "وفّر ٥٫٣%.", 0, False, (), "Arabic", True)
        self.assertTrue(any("numbers changed" in h for h in hard))
        self.assertEqual(H.numbers_of("وفّر ٤٫٣% و 1,524"), ["1524", "4.3"])
        t = H.finish_arabic("وفّر الجدار 4.3 من الطاقة , في EnergyPlus 25.2 ?", "arabic-indic")
        self.assertIn("٤٫٣", t); self.assertIn("EnergyPlus 25.2", t)
        self.assertIn("،", t); self.assertIn("؟", t)

    def test_tamil_numbers_and_marks(self):
        self.assertEqual(H.numbers_of("1,00,000 and 100,000 in 2020-ஆம்"), ["100000", "100000", "2020"])
        hard, soft = H.check("translate", "It cost 100000.", "இது ஒரு லட்சம் ஆனது।", 0, False, (), "Tamil", True)
        self.assertTrue(any("numbers changed" in h for h in hard))
        self.assertTrue(any("danda" in x for x in soft)); self.assertTrue(any("lakh" in x for x in soft))

    def test_strip(self):
        self.assertEqual(H.strip_model_text("<think>x</think>\nHere is the revised text:\nGood text."), "Good text.")
        self.assertEqual(H.strip_model_text("```\nGood.\n```"), "Good.")

    def test_chrf(self):
        self.assertAlmostEqual(H.chrf("same text", "same text"), 100.0)
        self.assertLess(H.chrf("other words", "same text"), 50)

    def test_segments_keep_code_and_tables(self):
        doc = "# Title\n\nPara one.\n\n```\ncode 1-2\n```\n\n| a | b |\n|---|---|\n\nPara two."
        kinds = [k for k, _ in H.segments(doc) if k != "blank"]
        self.assertEqual(kinds, ["heading", "prose", "keep", "keep", "prose"])


class Pipeline(Base):
    def test_proofread_repairs_dropped_placeholder(self):
        calls = {"n": 0}

        def fn(system, user):
            if judge(system):
                return "SAME. Meaning kept."
            calls["n"] += 1
            if calls["n"] == 1:                      # first draft drops the placeholder
                return "Here is the revised text:\nThe wall saves energy."
            return payload(user).replace("teh", "the")
        REPLY["fn"] = fn
        code, out, audit = self.run_tool("proofread", "The wall saves 4.3% of teh energy.\n")
        self.assertEqual(code, 0)
        self.assertIn("4.3%", out); self.assertIn("of the energy", out)
        seg = audit["segments"][0]
        self.assertEqual(seg["status"], "ok"); self.assertEqual(seg["candidates"][0]["repairs"], 1)
        self.assertIn("edit_rate", seg["candidates"][0])

    def test_kept_original_when_nothing_passes(self):
        REPLY["fn"] = lambda s, u: "SAME" if judge(s) else "Rewritten without the number."
        code, out, audit = self.run_tool("humanize", "It did not exceed 2 K.\n")
        self.assertEqual(code, 3)
        self.assertEqual(out, "It did not exceed 2 K.\n")
        self.assertEqual(audit["segments"][0]["status"], "kept_original")

    def test_escalation_rescues_a_failed_paragraph(self):
        # the small model drops the number; the escalation model returns the paragraph intact
        REPLY["fn"] = lambda s, u: "SAME" if judge(s) else ("Dropped." if REPLY["model"] == "m" else payload(u))
        code, out, audit = self.run_tool("proofread", "It cut load by 4.3% today.\n", "--candidates", "1",
                                         "--escalate-model", "big")
        self.assertEqual(code, 0)
        self.assertIn("4.3%", out)
        self.assertEqual(audit["summary"]["escalated"], 1)

    def test_translate_to_arabic_numbers_visible(self):
        seen = {}

        def fn(system, user):
            if judge(system):
                return "SAME"
            if "into Arabic" in user:
                seen["user"] = user
                return "وفّر الجدار 4.3% من الطاقة؛ هل يكفي ذلك?"
            return "The wall saved 4.3% of the energy; is that enough?"      # back-translation
        REPLY["fn"] = fn
        code, out, audit = self.run_tool("translate", "The wall saved 4.3% of the energy; is that enough?\n",
                                         "--target", "Arabic", "--min-chrf", "40")
        self.assertEqual(code, 0)
        self.assertIn("4.3%", seen["user"])                    # the model sees the number
        self.assertIn("؟", out)                            # Arabic question mark set in code
        self.assertGreater(audit["segments"][0]["candidates"][0]["chrf"], 40)

    def test_translate_to_tamil(self):
        def fn(system, user):
            if judge(system):
                return "SAME"
            if "into Tamil" in user:
                self.assertIn("Language: Tamil.", system)       # the Tamil writing note reaches the model
                return "சுவர் ஆற்றலில் 4.3% சேமித்தது."
            return "The wall saved 4.3% of the energy."
        REPLY["fn"] = fn
        code, out, audit = self.run_tool("translate", "The wall saved 4.3% of the energy.\n",
                                         "--target", "Tamil", "--min-chrf", "40")
        self.assertEqual(code, 0)
        self.assertIn("4.3%", out); self.assertIn("சுவர்", out)

    def test_glossary_only_terms_in_the_paragraph(self):
        seen = {}

        def fn(system, user):
            if judge(system):
                return "SAME"
            if "into Tamil" in user:
                seen["user"] = user
                return "கட்ட மாற்றப் பொருள் 4.3% சேமித்தது."
            return "The phase change material saved 4.3%."
        REPLY["fn"] = fn
        d = tempfile.mkdtemp(); g = os.path.join(d, "terms.tsv")
        open(g, "w", encoding="utf-8").write("phase change material\tகட்ட மாற்றப் பொருள்\nfacade\tமுகப்பு\n")
        self.run_tool("translate", "The phase change material saved 4.3%.\n", "--target", "Tamil", "--glossary", g,
                      "--min-chrf", "40")
        self.assertIn("phase change material = ", seen["user"]); self.assertNotIn("facade", seen["user"])

    def test_translategemma_format(self):
        seen = {}
        REPLY["fn"] = lambda s, u: "SAME" if judge(s) else "The wall saved 4.3%."   # judge and back-translation
        orig = Fake.do_POST

        def do_post(handler):                       # record the raw message structure sent to the writer
            body = json.loads(handler.rfile.read(int(handler.headers["Content-Length"])).decode("utf-8"))
            REPLY["model"] = body["model"]
            if body["model"] == "tg":
                seen["messages"] = body["messages"]
                text = "சுவர் 4.3% சேமித்தது."
            else:
                text = REPLY["fn"](body["messages"][0]["content"], body["messages"][-1]["content"])
            out = json.dumps({"choices": [{"message": {"role": "assistant", "content": text}}]}).encode("utf-8")
            handler.send_response(200); handler.send_header("Content-Length", str(len(out))); handler.end_headers()
            handler.wfile.write(out)
        Fake.do_POST = do_post
        try:
            d = tempfile.mkdtemp(); src, out = os.path.join(d, "in.md"), os.path.join(d, "out.md")
            open(src, "w", encoding="utf-8").write("The wall saved 4.3%.\n")
            code = H.main(["translate", src, "-o", out, "--base-url", self.url, "--model", "tg", "--target", "Tamil",
                           "--writer-format", "translategemma", "--judge-model", "judge", "--min-chrf", "40"])
        finally:
            Fake.do_POST = orig
        msg = seen["messages"]
        self.assertEqual(len(msg), 1); self.assertEqual(msg[0]["role"], "user")
        entry = msg[0]["content"][0]
        self.assertEqual((entry["type"], entry["source_lang_code"], entry["target_lang_code"]), ("text", "en", "ta"))
        self.assertEqual(code, 0)

    def test_model_auto_picks_by_language(self):
        REPLY["tags"] = ["qwen3:4b", "gemma3:4b", "nomic-embed-text:latest"]
        self.assertEqual(H.pick_model(self.url, "proofread", ["English"]), "qwen3:4b")
        self.assertEqual(H.pick_model(self.url, "translate", ["English", "Tamil"]), "gemma3:4b")
        REPLY["tags"] = ["llama3.2:3b"]
        with self.assertRaises(RuntimeError) as e:
            H.pick_model(self.url, "flag", ["Arabic"])
        self.assertIn("ollama pull gemma3:4b", str(e.exception))
        REPLY["tags"] = ["qwen3:4b"]
        REPLY["fn"] = lambda s, u: "SAME" if judge(s) else payload(u).replace("/no_think", "")
        code, out, audit = self.run_tool("proofread", "It works well.\n", "--model", "auto")
        self.assertEqual(audit["model"], "qwen3:4b"); self.assertTrue(audit["settings"]["no_think"])

    def test_tamil_target_rejects_latin_output(self):
        hard, _ = H.check("translate", "The wall saved 4.3%.", "The wall saved 4.3%.", 0, False, (), "Tamil", True)
        self.assertTrue(any("Tamil script" in h for h in hard))

    def test_proofread_tamil(self):
        def fn(system, user):
            if judge(system):
                return "SAME"
            self.assertIn("formal written Tamil", system)
            return payload(user).replace("செமித்தது", "சேமித்தது")
        REPLY["fn"] = fn
        code, out, audit = self.run_tool("proofread", "சுவர் ஆற்றலில் 4.3% செமித்தது.\n", "--lang", "Tamil")
        self.assertEqual(code, 0)
        self.assertIn("சேமித்தது", out); self.assertIn("4.3%", out)

    def test_flag_task_lists_without_rewriting(self):
        REPLY["fn"] = lambda s, u: "செமித்தது -> சேமித்தது (spelling)"
        code, out, audit = self.run_tool("flag", "சுவர் ஆற்றலில் 4.3% செமித்தது.\n", "--lang", "Tamil")
        self.assertEqual(code, 0)
        self.assertIn("> சுவர் ஆற்றலில் 4.3% செமித்தது.", out); self.assertIn("-> சேமித்தது", out)
        self.assertEqual(audit["summary"]["flagged"], 1)

    def test_draft_flags_invented_number(self):
        REPLY["fn"] = lambda s, u: "SUPPORTED" if "notes" in s and "SUPPORTED" in s else \
            "The prototype saved 12% of cooling energy over 2 years."
        code, out, audit = self.run_tool("draft", "- prototype saved 12% cooling energy\n", "--repairs", "0",
                                         "--candidates", "1")
        self.assertEqual(code, 3)
        self.assertEqual(audit["segments"][0]["status"], "needs_review")
        self.assertTrue(any("not in the notes" in h for h in audit["segments"][0]["candidates"][0]["hard"]))


if __name__ == "__main__":
    unittest.main()
