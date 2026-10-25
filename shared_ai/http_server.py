from __future__ import annotations

import json
import math
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


def reject_json_constant(value):
    raise ValueError("non_finite_json_number")


class Handler(BaseHTTPRequestHandler):
    server_version = "EnguruSharedAI/0.1"
    max_body_bytes = 1024 * 1024
    body_read_timeout = 5.0

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return

    def _reject(self, status: int, reason: str) -> None:
        # Keep unread or ambiguous body bytes outside subsequent requests.
        self.close_connection = True
        self._send(status, {"state": "BLOCKED", "reason": reason})

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
        lengths = self.headers.get_all("Content-Length", [])
        if self.headers.get_all("Transfer-Encoding", []):
            self._reject(400, "unsupported_transfer_encoding")
            return
        if len(lengths) != 1:
            self._reject(411 if not lengths else 400, "single_content_length_required")
            return
        raw_length = lengths[0].strip()
        if not raw_length.isascii() or not raw_length.isdecimal():
            self._reject(400, "invalid_content_length")
            return
        try:
            length = int(raw_length)
        except ValueError:
            self._reject(400, "invalid_content_length")
            return
        if length > self.max_body_bytes:
            self._reject(413, "request_body_too_large")
            return
        previous_timeout = self.connection.gettimeout()
        try:
            self.connection.settimeout(self.body_read_timeout)
            body = self.rfile.read(length)
        except TimeoutError:
            self._reject(408, "request_body_timeout")
            return
        finally:
            self.connection.settimeout(previous_timeout)
        if len(body) != length:
            self._reject(400, "incomplete_request_body")
            return
        try:
            payload = json.loads(body.decode("utf-8"), parse_constant=reject_json_constant)
            if type(payload) is not dict:
                raise ValueError("request_object_required")
            cost = payload.get("cost_ceiling", 0)
            if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
                raise ValueError("finite_nonnegative_cost_required")
            request = RequestEnvelope.from_dict(payload)
            result = RUNTIME.execute(request)
            self._send(200 if result.state == "PASS" else 503, result.as_dict())
        except (KeyError, ValueError, TypeError, RecursionError, OverflowError) as exc:
            self._reject(400, type(exc).__name__)


def main() -> None:
    host = os.getenv("ENGURU_SHARED_AI_HOST", "127.0.0.1")
    port = int(os.getenv("ENGURU_SHARED_AI_PORT", "8787"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
