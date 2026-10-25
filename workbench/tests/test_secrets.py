"""Key storage tests. A fake in-memory keyring is used, so the real credential store is never touched."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lawb import secrets  # noqa: E402


class FakeKeyring:
    def __init__(self):
        self.store = {}

    def set_password(self, service, user, value):
        self.store[(service, user)] = value

    def get_password(self, service, user):
        return self.store.get((service, user))

    def delete_password(self, service, user):
        if (service, user) not in self.store:
            raise KeyError(user)
        del self.store[(service, user)]


class SecretsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._old_home = os.environ.get("LAWB_HOME")
        os.environ["LAWB_HOME"] = self._tmp.name
        self._old_kr = secrets._keyring
        self.fake = FakeKeyring()
        secrets._keyring = lambda: self.fake
        self._old_env = os.environ.pop("OPENAI_API_KEY", None)

    def tearDown(self):
        secrets._keyring = self._old_kr
        if self._old_env is not None:
            os.environ["OPENAI_API_KEY"] = self._old_env
        if self._old_home is None:
            os.environ.pop("LAWB_HOME", None)
        else:
            os.environ["LAWB_HOME"] = self._old_home
        self._tmp.cleanup()

    def test_set_then_get_uses_the_store_and_enables_cloud(self):
        secrets.set_key("openai", "sk-test-value-123")
        self.assertEqual(secrets.get_key("openai"), ("sk-test-value-123", "keyring"))
        from lawb import config
        self.assertTrue(config.load_config()["cloud"]["enabled"])

    def test_store_wins_over_environment(self):
        os.environ["OPENAI_API_KEY"] = "env-value"
        secrets.set_key("openai", "store-value")
        self.assertEqual(secrets.get_key("openai"), ("store-value", "keyring"))

    def test_environment_is_the_fallback(self):
        os.environ["OPENAI_API_KEY"] = "env-value"
        self.assertEqual(secrets.get_key("openai"), ("env-value", "environment"))

    def test_delete_removes_the_key(self):
        secrets.set_key("anthropic", "ant-value")
        self.assertTrue(secrets.delete_key("anthropic"))
        self.assertEqual(secrets.get_key("anthropic"), (None, None))

    def test_config_file_never_contains_the_key(self):
        secrets.set_key("anthropic", "ant-secret-value")
        text = (Path(self._tmp.name) / "config.json").read_text(encoding="utf-8")
        self.assertNotIn("ant-secret-value", text)

    def test_call_log_holds_metadata_only(self):
        secrets.record_cloud_call("anthropic", "claude-opus-5-5")
        rows = secrets.read_cloud_log()
        self.assertEqual(set(rows[0]), {"time", "provider", "model"})


if __name__ == "__main__":
    unittest.main()
