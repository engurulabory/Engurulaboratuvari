from __future__ import annotations

import json
import urllib.request

from shared_ai.runtime import RequestEnvelope


class LocalOpenAICompatibleAdapter:
    """Local adapter with a backward-compatible OpenAI path and an optional Ollama-native path."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 90.0,
        native_ollama: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.native_ollama = native_ollama

    @staticmethod
    def _messages(request: RequestEnvelope) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if request.behavior_instruction:
            messages.append({"role": "system", "content": request.behavior_instruction})
        messages.append({"role": "user", "content": request.input})
        return messages

    def _invoke_openai_compatible(self, request: RequestEnvelope) -> dict:
        body = json.dumps({
            "model": self.model,
            "messages": self._messages(request),
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

    def _invoke_ollama_native(self, request: RequestEnvelope) -> dict:
        structured = (
            request.verification_profile == "STRUCTURED"
            or "structured_output" in request.required_capabilities
        )
        payload: dict = {
            "model": self.model,
            "messages": self._messages(request),
            "stream": False,
        }

        # INTERACTIVE means bounded user-facing latency. For thinking models, keep
        # hidden reasoning disabled so useful output can complete inside the
        # interactive provider budget. BATCH/default modes keep model defaults.
        if request.latency_class == "INTERACTIVE":
            payload["think"] = False

        if structured:
            payload["format"] = "json"

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
            raw = json.loads(response.read().decode("utf-8"))

        output = raw["message"]["content"]
        if structured:
            try:
                output = json.loads(output)
            except (TypeError, json.JSONDecodeError):
                # Preserve the raw model output so the governed verifier can
                # classify/correct malformed structured output rather than the
                # adapter silently manufacturing authority.
                pass
        return {"output": output, "raw": raw}

    def invoke(self, request: RequestEnvelope) -> dict:
        if self.native_ollama:
            return self._invoke_ollama_native(request)
        return self._invoke_openai_compatible(request)
