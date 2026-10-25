import json
import http.client
import socket
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
from http.server import ThreadingHTTPServer

import shared_ai.http_server as http_server
from shared_ai.adapters.local_openai import LocalOpenAICompatibleAdapter
from shared_ai.runtime import ProviderRecord, RequestEnvelope, SharedAIRuntime


class FakeAdapter:
    def __init__(self, output="ok", error=None):
        self.output = output
        self.error = error
        self.calls = 0

    def invoke(self, request):
        self.calls += 1
        if self.error:
            raise self.error
        return {"output": self.output}


def req(**kw):
    base = dict(
        request_id="r1",
        task_type="test",
        data_class="PUBLIC",
        required_capabilities=frozenset({"text"}),
        cost_ceiling=0.0,
        input="hello",
        intent="complete the runtime test",
        success_criteria=("verified result",),
    )
    base.update(kw)
    return RequestEnvelope(**base)


def provider(name="p1", adapter=None, **kw):
    base = dict(
        name=name,
        model=f"{name}-model",
        adapter=adapter or FakeAdapter(),
        local=False,
        production_approved=True,
        privacy_verified=True,
        commercial_use_verified=True,
        cost_verified=True,
        estimated_cost=0.0,
        capabilities={"text"},
        health="HEALTHY",
    )
    base.update(kw)
    return ProviderRecord(**base)


class RuntimeTests(unittest.TestCase):
    def test_safe_provider_passes(self):
        r = SharedAIRuntime([provider()]).execute(req())
        self.assertEqual(r.state, "PASS")
        self.assertEqual(r.provider, "p1")
        self.assertEqual(r.estimated_cost, 0.0)
        self.assertEqual(r.as_dict()["route_evidence"]["estimated_cost"], 0.0)

    def test_secret_uses_local_only(self):
        external = provider("external")
        local = provider("local", local=True)
        r = SharedAIRuntime([external, local]).execute(req(data_class="SECRET"))
        self.assertEqual(r.provider, "local")

    def test_paid_provider_is_skipped(self):
        paid = provider("paid", estimated_cost=0.01)
        free = provider("free")
        r = SharedAIRuntime([paid, free]).execute(req())
        self.assertEqual(r.provider, "free")

    def test_unapproved_provider_is_skipped(self):
        blocked = provider("blocked", production_approved=False)
        good = provider("good")
        r = SharedAIRuntime([blocked, good]).execute(req())
        self.assertEqual(r.provider, "good")

    def test_unverified_metadata_is_skipped(self):
        bad = provider("bad", privacy_verified=False)
        good = provider("good")
        r = SharedAIRuntime([bad, good]).execute(req())
        self.assertEqual(r.provider, "good")

    def test_capability_mismatch_is_skipped(self):
        text = provider("text", capabilities={"text"})
        vision = provider("vision", capabilities={"text", "vision"})
        r = SharedAIRuntime([text, vision]).execute(req(required_capabilities=frozenset({"vision"})))
        self.assertEqual(r.provider, "vision")

    def test_provider_error_falls_back(self):
        bad = provider("bad", adapter=FakeAdapter(error=RuntimeError("down")))
        good = provider("good")
        r = SharedAIRuntime([bad, good]).execute(req())
        self.assertEqual(r.provider, "good")

    def test_circuit_opens_after_three_failures(self):
        bad = provider("bad", adapter=FakeAdapter(error=RuntimeError("down")))
        runtime = SharedAIRuntime([bad])
        for _ in range(3):
            runtime.execute(req())
        self.assertTrue(bad.circuit_open)

    def test_no_safe_provider_holds(self):
        r = SharedAIRuntime([provider(production_approved=False)]).execute(req())
        self.assertEqual(r.state, "HOLD")


class HTTPServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), http_server.Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        original = http_server.RUNTIME
        http_server.RUNTIME = SharedAIRuntime([])
        self.addCleanup(setattr, http_server, "RUNTIME", original)

    def wire_post(self, headers, body=b"", half_close=True):
        with socket.create_connection(("127.0.0.1", self.port), timeout=2) as connection:
            raw = ("POST /v1/enguru/respond HTTP/1.1\r\nHost: localhost\r\n" +
                   headers + "\r\n\r\n").encode("ascii") + body
            connection.sendall(raw)
            if half_close:
                connection.shutdown(socket.SHUT_WR)
            response = http.client.HTTPResponse(connection)
            response.begin()
            return response.status, json.loads(response.read())

    def valid_body(self, **changes):
        payload = {"request_id": "web-acceptance", "task_type": "test", "data_class": "PUBLIC",
                   "required_capabilities": ["text"], "cost_ceiling": 0, "input": "hello",
                   "intent": "verify the HTTP boundary", "success_criteria": ["observed response"]}
        payload.update(changes)
        return json.dumps(payload).encode()

    def assert_health_up(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read())["runtime"], "UP")

    def test_health_endpoint(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=2) as r:
            payload = json.loads(r.read())
        self.assertEqual(payload["state"], "PASS")
        self.assertEqual(payload["runtime"], "UP")

    def test_post_without_provider_holds(self):
        old = http_server.RUNTIME
        http_server.RUNTIME = SharedAIRuntime([])
        try:
            body = json.dumps({
                "request_id":"r-http",
                "task_type":"test",
                "data_class":"PUBLIC",
                "required_capabilities":["text"],
                "cost_ceiling":0,
                "input":"hello",
                "intent":"complete the runtime request",
                "success_criteria":["verified result"]
            }).encode()
            request = urllib.request.Request(
                f"http://127.0.0.1:{self.port}/v1/enguru/respond",
                data=body,
                headers={"Content-Type":"application/json"},
                method="POST",
            )
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(request, timeout=2)
            self.assertEqual(ctx.exception.code, 503)
        finally:
            http_server.RUNTIME = old

    def test_real_http_success_200_with_local_test_adapter(self):
        adapter = FakeAdapter(output="http-boundary-ok")
        http_server.RUNTIME = SharedAIRuntime([provider("http-local-test", adapter=adapter, local=True)])
        body = self.valid_body()
        status, payload = self.wire_post(f"Content-Length: {len(body)}", body)
        self.assertEqual(status, 200)
        self.assertEqual(payload["state"], "PASS")
        self.assertEqual(payload["route_evidence"]["provider"], "http-local-test")
        self.assertEqual(adapter.calls, 1)
        print("WEB_REAL_HTTP_SUCCESS=200; PROVIDER=LOCAL_TEST_ADAPTER; OUTBOUND_PROVIDER_CALLS=0")

    def test_real_http_rejects_ambiguous_or_invalid_body_framing(self):
        body = self.valid_body()
        cases = [("Content-Length: -1", body, 400), ("Content-Length: +1", body, 400),
                 ("Content-Length: invalid", body, 400),
                 (f"Content-Length: {len(body)}\r\nContent-Length: {len(body)+1}", body, 400),
                 (f"Transfer-Encoding: chunked\r\nContent-Length: {len(body)}", body, 400),
                 ("", b"", 411),
                 (f"Content-Length: {http_server.Handler.max_body_bytes+1}", b"", 413),
                 ("Content-Length: 5", b"{}", 400)]
        with patch.object(http_server.RUNTIME, "execute", wraps=http_server.RUNTIME.execute) as execute:
            for headers, data, expected in cases:
                with self.subTest(headers=headers):
                    status, payload = self.wire_post(headers, data)
                    self.assertEqual(status, expected)
                    self.assertEqual(payload["state"], "BLOCKED")
                    self.assert_health_up()
            execute.assert_not_called()
        print("WEB_REAL_HTTP_FRAMING=400,411,413; INVALID_REQUEST_DISPATCHES=0; HEALTH=200")

    def test_real_http_incomplete_body_has_idle_timeout(self):
        with patch.object(http_server.Handler, "body_read_timeout", 0.1):
            with patch.object(http_server.RUNTIME, "execute", wraps=http_server.RUNTIME.execute) as execute:
                status, payload = self.wire_post("Content-Length: 10", b"{", half_close=False)
                self.assertEqual(status, 408)
                self.assertEqual(payload["reason"], "request_body_timeout")
                execute.assert_not_called()
        self.assert_health_up()
        print("WEB_REAL_HTTP_IDLE_TIMEOUT=408; HEALTH=200")

    def test_real_http_rejects_malformed_json_and_invalid_cost_before_runtime(self):
        bodies = [b"null", b"[]", b"{invalid", b"\xff", b"["*2000+b"]"*2000]
        bodies += [self.valid_body(cost_ceiling=value) for value in
                   (float("nan"), float("inf"), "NaN", "Infinity", True, -1, {}, [])]
        with patch.object(http_server.RUNTIME, "execute", wraps=http_server.RUNTIME.execute) as execute:
            for body in bodies:
                with self.subTest(body=body[:50]):
                    status, payload = self.wire_post(f"Content-Length: {len(body)}", body)
                    self.assertEqual(status, 400)
                    self.assertEqual(payload["state"], "BLOCKED")
                    self.assert_health_up()
            execute.assert_not_called()
        print("WEB_REAL_HTTP_BAD_JSON_AND_COST=400; INVALID_REQUEST_DISPATCHES=0; HEALTH=200")


if __name__ == "__main__":
    unittest.main()


class LocalAdapterContractTests(unittest.TestCase):
    def test_openai_compatible_local_adapter(self):
        class LocalHandler(http_server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                return

            def do_POST(self):
                self.assert_path = self.path
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length))
                body = json.dumps({
                    "choices": [{"message": {"content": "local-ok"}}],
                    "echo_model": payload.get("model"),
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server = ThreadingHTTPServer(("127.0.0.1", 0), LocalHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            adapter = LocalOpenAICompatibleAdapter(
                base_url=f"http://127.0.0.1:{server.server_address[1]}",
                model="local-test",
                timeout_seconds=2,
            )
            result = adapter.invoke(req())
            self.assertEqual(result["output"], "local-ok")
        finally:
            server.shutdown()
            server.server_close()

    def test_native_ollama_interactive_structured_adapter(self):
        captured = {}

        class LocalHandler(http_server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                return

            def do_POST(self):
                captured["path"] = self.path
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length))
                captured["payload"] = payload
                body = json.dumps({
                    "message": {"content": json.dumps({"ok": True})},
                    "done": True,
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server = ThreadingHTTPServer(("127.0.0.1", 0), LocalHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            adapter = LocalOpenAICompatibleAdapter(
                base_url=f"http://127.0.0.1:{server.server_address[1]}",
                model="qwen3:14b",
                timeout_seconds=2,
                native_ollama=True,
            )
            result = adapter.invoke(req(
                latency_class="INTERACTIVE",
                verification_profile="STRUCTURED",
                required_capabilities=frozenset({"text", "structured_output"}),
            ))
            self.assertEqual(captured["path"], "/api/chat")
            self.assertIs(captured["payload"]["think"], False)
            self.assertEqual(captured["payload"]["format"], "json")
            self.assertEqual(result["output"], {"ok": True})
        finally:
            server.shutdown()
            server.server_close()
