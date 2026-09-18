from __future__ import annotations

import json
import urllib.request

from shared_ai.runtime import RequestEnvelope


class LocalOpenAICompatibleAdapter:
    """Local-only adapter for an OpenAI-compatible runtime such as Ollama/vLLM/llama.cpp."""

    def __init__(self, base_url: str, model: str, timeout_seconds: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def invoke(self, request: RequestEnvelope) -> dict:
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": request.input}],
            "stream": False,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        output = payload["choices"][0]["message"]["content"]
        return {"output": output, "raw": payload}
