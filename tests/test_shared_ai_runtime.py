import json
import threading
import time
import unittest
import urllib.error
import urllib.request
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
