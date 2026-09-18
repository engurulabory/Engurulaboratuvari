import unittest

from shared_ai.behavior import BehaviorEngine
from shared_ai.runtime import ProviderRecord, RequestEnvelope, SharedAIRuntime


class FakeAdapter:
    def __init__(self, output="ok"):
        self.output = output
        self.calls = 0

    def invoke(self, request):
        self.calls += 1
        return {"output": self.output}


def request(**overrides):
    values = {
        "request_id": "behavior-1",
        "task_type": "test",
        "data_class": "INTERNAL",
        "required_capabilities": frozenset({"text"}),
        "cost_ceiling": 0.0,
        "input": "hello",
    }
    values.update(overrides)
    return RequestEnvelope(**values)


def provider(adapter=None):
    return ProviderRecord(
        name="local_runtime",
        model="qwen3:14b",
        adapter=adapter or FakeAdapter(),
        local=True,
        production_approved=True,
        privacy_verified=True,
        commercial_use_verified=True,
        cost_verified=True,
        estimated_cost=0.0,
        capabilities={"text", "reasoning"},
    )


class BehaviorEngineTests(unittest.TestCase):
    def test_simple_task_uses_standard_effort(self):
        verdict = BehaviorEngine().preflight(request())
        self.assertEqual(verdict.state, "PASS")
        self.assertEqual(verdict.reasoning_effort, "STANDARD")

    def test_reasoning_task_escalates_to_deep(self):
        verdict = BehaviorEngine().preflight(
            request(task_type="reasoning", required_capabilities=frozenset({"text", "reasoning"}))
        )
        self.assertEqual(verdict.reasoning_effort, "DEEP")

    def test_secret_escalates_to_deep(self):
        verdict = BehaviorEngine().preflight(request(data_class="SECRET"))
        self.assertEqual(verdict.reasoning_effort, "DEEP")

    def test_missing_input_holds_before_provider(self):
        adapter = FakeAdapter()
        result = SharedAIRuntime([provider(adapter)]).execute(request(input="   "))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "missing_input")
        self.assertEqual(adapter.calls, 0)

    def test_invalid_data_class_holds(self):
        result = SharedAIRuntime([provider()]).execute(request(data_class="UNKNOWN"))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "invalid_data_class")

    def test_negative_cost_ceiling_holds(self):
        result = SharedAIRuntime([provider()]).execute(request(cost_ceiling=-1))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "invalid_cost_ceiling")

    def test_missing_capabilities_holds(self):
        result = SharedAIRuntime([provider()]).execute(request(required_capabilities=frozenset()))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "missing_capabilities")

    def test_empty_provider_output_cannot_be_pass(self):
        result = SharedAIRuntime([provider(FakeAdapter(output=""))]).execute(request())
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "empty_output")
        self.assertEqual(result.behavior_evidence["verification"], "HOLD")

    def test_verified_output_passes_with_safe_behavior_evidence(self):
        result = SharedAIRuntime([provider(FakeAdapter(output="done"))]).execute(request())
        payload = result.as_dict()
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.output, "done")
        self.assertEqual(payload["behavior_evidence"]["preflight"], "PASS")
        self.assertEqual(payload["behavior_evidence"]["verification"], "PASS")
        self.assertFalse(payload["behavior_evidence"]["private_chain_of_thought_stored"])

    def test_behavior_does_not_expand_provider_authority(self):
        blocked = provider()
        blocked.production_approved = False
        result = SharedAIRuntime([blocked]).execute(request())
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.provider, None)
        self.assertIn("local_runtime:SKIP:authority", result.path)


if __name__ == "__main__":
    unittest.main()
