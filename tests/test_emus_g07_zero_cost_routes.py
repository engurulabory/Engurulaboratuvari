"""EMUS GH-09-C3 deterministic zero-cost and fallback adversarial checks."""
import os
import unittest
from unittest.mock import patch
from shared_ai.http_server import build_runtime_from_env
from shared_ai.runtime import ProviderRecord, RequestEnvelope, SharedAIRuntime


class Adapter:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = 0
    def invoke(self, request):
        self.calls += 1
        if self.fail:
            raise RuntimeError("offline")
        return {"output": "local verified"}


def provider(name, adapter, *, local=True, cost=0, approved=True):
    return ProviderRecord(name=name, model=name, adapter=adapter, local=local,
        production_approved=approved, privacy_verified=True,
        commercial_use_verified=True, cost_verified=True,
        estimated_cost=cost, capabilities={"text","reasoning"})


def request(data_class="INTERNAL"):
    return RequestEnvelope(request_id="emus-cost", task_type="mac_engineer_chat",
        data_class=data_class, required_capabilities=frozenset({"text","reasoning"}),
        cost_ceiling=0, input="fixed test")


class EmusZeroPaidAPIGateTests(unittest.TestCase):
    def test_environment_registers_only_explicit_local_provider(self):
        with patch.dict(os.environ, {
            "ENGURU_LOCAL_ENABLED":"1", "ENGURU_LOCAL_MODEL":"qwen3:14b",
            "ENGURU_LOCAL_COMMERCIAL_USE_VERIFIED":"1",
            "ENGURU_LOCAL_BASE_URL":"http://127.0.0.1:11434",
            "ENGURU_LOCAL_NATIVE_OLLAMA":"1"}, clear=True):
            runtime = build_runtime_from_env()
        self.assertEqual(len(runtime.providers), 1)
        self.assertEqual(runtime.providers[0].name, "local_runtime")
        self.assertEqual(runtime.providers[0].estimated_cost, 0.0)

    def test_paid_provider_skipped_even_after_local_failure(self):
        local, paid = Adapter(fail=True), Adapter()
        result = SharedAIRuntime([provider("local",local),provider("paid",paid,local=False,cost=0.001)]).execute(request())
        self.assertEqual(result.state,"HOLD")
        self.assertEqual(paid.calls,0)

    def test_all_paid_fallbacks_blocked(self):
        a,b=Adapter(),Adapter()
        result=SharedAIRuntime([provider("paid1",a,cost=0.01),provider("paid2",b,cost=0.001)]).execute(request())
        self.assertEqual(result.state,"HOLD")
        self.assertEqual((a.calls,b.calls),(0,0))

    def test_secret_nonlocal_free_provider_blocked(self):
        outside=Adapter()
        result=SharedAIRuntime([provider("free_external",outside,local=False)]).execute(request("SECRET"))
        self.assertEqual(result.state,"HOLD")
        self.assertEqual(outside.calls,0)

    def test_unapproved_free_provider_blocked(self):
        a=Adapter()
        result=SharedAIRuntime([provider("free_unapproved",a,approved=False)]).execute(request())
        self.assertEqual(result.state,"HOLD")
        self.assertEqual(a.calls,0)


if __name__=="__main__":
    unittest.main()
