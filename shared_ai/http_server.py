from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from shared_ai.adapters.local_openai import LocalOpenAICompatibleAdapter
from shared_ai.runtime import ProviderRecord, RequestEnvelope, SharedAIRuntime


def build_runtime_from_env() -> SharedAIRuntime:
    runtime = SharedAIRuntime()
    if os.getenv("ENGURU_LOCAL_ENABLED") == "1":
        base_url = os.getenv("ENGURU_LOCAL_BASE_URL", "http://127.0.0.1:11434")
        model = os.getenv("ENGURU_LOCAL_MODEL", "")
        commercial = os.getenv("ENGURU_LOCAL_COMMERCIAL_USE_VERIFIED") == "1"
        native_ollama = os.getenv("ENGURU_LOCAL_NATIVE_OLLAMA") == "1"
        if model:
            capabilities = {"text", "reasoning"}
            if native_ollama:
                capabilities.add("structured_output")
            runtime.register(ProviderRecord(
                name="local_runtime",
                model=model,
                adapter=LocalOpenAICompatibleAdapter(
                    base_url=base_url,
                    model=model,
                    native_ollama=native_ollama,
                ),
                local=True,
                production_approved=True,
                privacy_verified=True,
                commercial_use_verified=commercial,
                cost_verified=True,
                estimated_cost=0.0,
                capabilities=capabilities,
            ))
    return runtime


RUNTIME = build_runtime_from_env()


class Handler(BaseHTTPRequestHandler):
    server_version = "EnguruSharedAI/0.1"

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(200, {
                "state": "PASS",
                "service": "ENGURU_SHARED_AI_INFRASTRUCTURE",
                "runtime": "UP",
                "active_providers": len(RUNTIME.providers),
            })
            return
        self._send(404, {"state": "BLOCKED", "reason": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/v1/enguru/respond":
            self._send(404, {"state": "BLOCKED", "reason": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            request = RequestEnvelope.from_dict(payload)
            result = RUNTIME.execute(request)
            self._send(200 if result.state == "PASS" else 503, result.as_dict())
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, {"state": "BLOCKED", "reason": type(exc).__name__})


def main() -> None:
    host = os.getenv("ENGURU_SHARED_AI_HOST", "127.0.0.1")
    port = int(os.getenv("ENGURU_SHARED_AI_PORT", "8787"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
