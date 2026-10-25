"""Provider tests. They use fake SDK clients, so they need no keys and no network.

Live calls to Claude and OpenAI are checked separately in benchmarks/run_benchmarks.py (B7),
which reports NOT VERIFIED when the key is missing or rejected.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawb import llm  # noqa: E402


class FakeAnthropicMessages:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type="thinking", thinking="..."),
                                        SimpleNamespace(type="text", text=" fixed "),
                                        SimpleNamespace(type="text", text="ok")])


class FakeAnthropic:
    def __init__(self):
        self.messages = FakeAnthropicMessages()


class FakeOpenAICompletions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=" fixed "))])


class FakeOpenAI:
    def __init__(self):
        self.chat = SimpleNamespace(completions=FakeOpenAICompletions())


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._old_home = os.environ.get("LAWB_HOME")
        os.environ["LAWB_HOME"] = self._tmp.name  # isolated config: cloud disabled by default

    def tearDown(self):
        if self._old_home is None:
            os.environ.pop("LAWB_HOME", None)
        else:
            os.environ["LAWB_HOME"] = self._old_home
        self._tmp.cleanup()

    def test_split_spec(self):
        self.assertEqual(llm.split_spec("qwen3:8b"), ("ollama", "qwen3:8b"))
        self.assertEqual(llm.split_spec("ollama:qwen3:8b"), ("ollama", "qwen3:8b"))
        self.assertEqual(llm.split_spec("anthropic:claude-opus-5-5"), ("anthropic", "claude-opus-5-5"))
        self.assertEqual(llm.split_spec("openai:gpt-x"), ("openai", "gpt-x"))

    def test_cloud_is_off_by_default(self):
        self.assertEqual(llm.cloud_status("anthropic"), "disabled")
        with self.assertRaises(llm.CloudDisabledError):
            llm.RouterClient().chat("anthropic:claude-opus-5-5", "hi")

    def test_cloud_needs_a_key_even_when_enabled(self):
        from lawb import config, secrets
        config.save_config({**config.load_config(), "cloud": {"enabled": True}})
        original = secrets.get_key
        secrets.get_key = lambda provider: (None, None)  # no key in the store or the environment
        try:
            self.assertEqual(llm.cloud_status("anthropic"), "no key")
        finally:
            secrets.get_key = original

    def test_cloud_ready_when_enabled_and_key_present(self):
        from lawb import config, secrets
        config.save_config({**config.load_config(), "cloud": {"enabled": True}})
        original = secrets.get_key
        secrets.get_key = lambda provider: ("test-value", "keyring")
        try:
            self.assertEqual(llm.cloud_status("openai"), "ready")
        finally:
            secrets.get_key = original

    def test_status_never_returns_the_key(self):
        from lawb import secrets
        original = secrets.get_key
        secrets.get_key = lambda provider: ("SECRET-VALUE", "keyring")
        try:
            rows = secrets.status_rows()
            self.assertTrue(all("SECRET-VALUE" not in " ".join(r) for r in rows))
        finally:
            secrets.get_key = original

    def test_anthropic_chat_builds_a_messages_call(self):
        fake = FakeAnthropic()
        out = llm.anthropic_chat("claude-opus-5-5", "Fix it", "Be brief", 300, client=fake)
        call = fake.messages.calls[0]
        self.assertEqual(call["model"], "claude-opus-5-5")
        self.assertEqual(call["max_tokens"], 300)
        self.assertEqual(call["system"], "Be brief")
        self.assertEqual(call["messages"], [{"role": "user", "content": "Fix it"}])
        self.assertEqual(out, "fixed ok")  # only text blocks, stripped and joined

    def test_anthropic_chat_omits_system_when_absent(self):
        fake = FakeAnthropic()
        llm.anthropic_chat("claude-opus-5-5", "Fix it", None, 300, client=fake)
        self.assertNotIn("system", fake.messages.calls[0])

    def test_openai_chat_uses_max_completion_tokens(self):
        fake = FakeOpenAI()
        out = llm.openai_chat("some-model", "Fix it", "Be brief", 256, client=fake)
        call = fake.chat.completions.calls[0]
        self.assertEqual(call["model"], "some-model")
        self.assertEqual(call["max_completion_tokens"], 256)
        self.assertEqual(call["messages"][0], {"role": "system", "content": "Be brief"})
        self.assertEqual(out, "fixed")

    def test_ollama_refuses_non_local_hosts(self):
        with self.assertRaises(llm.LocalOnlyError):
            llm.OllamaClient("http://example.com:11434")

    def test_router_sends_bare_names_to_ollama(self):
        seen = {}

        class StubOllama:
            def chat(self, model, user, system=None, num_predict=500):
                seen["model"] = model
                return "local"

        router = llm.RouterClient(ollama=StubOllama())
        self.assertEqual(router.chat("qwen3:8b", "hi"), "local")
        self.assertEqual(seen["model"], "qwen3:8b")


if __name__ == "__main__":
    unittest.main()
