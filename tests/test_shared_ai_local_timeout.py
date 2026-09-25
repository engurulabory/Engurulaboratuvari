from __future__ import annotations

import unittest

from shared_ai.adapters.local_openai import (
    LocalOpenAICompatibleAdapter,
)


class LocalRuntimeTimeoutTests(unittest.TestCase):
    def test_default_engineering_timeout_is_90_seconds(self):
        adapter = LocalOpenAICompatibleAdapter(
            base_url="http://127.0.0.1:11434",
            model="qwen3:14b",
            native_ollama=True,
        )

        self.assertEqual(
            adapter.timeout_seconds,
            90.0,
        )


if __name__ == "__main__":
    unittest.main()
