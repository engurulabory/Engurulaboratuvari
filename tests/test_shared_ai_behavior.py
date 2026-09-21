import unittest

from shared_ai.behavior import BehaviorEngine
from shared_ai.context_state import ContextEnvelope, apply_steering, compact_context
from shared_ai.tool_runtime import ToolRegistry, ToolSpec
from shared_ai.runtime import ProviderRecord, RequestEnvelope, SharedAIRuntime


class FakeAdapter:
    def __init__(self, output="ok", outputs=None, error=None):
        self.output = output
        self.outputs = list(outputs) if outputs is not None else None
        self.error = error
        self.calls = 0
        self.instructions = []

    def invoke(self, request):
        self.calls += 1
        self.instructions.append(getattr(request, "behavior_instruction", ""))
        if self.error:
            raise self.error
        if self.outputs is not None:
            index = min(self.calls - 1, len(self.outputs) - 1)
            return {"output": self.outputs[index]}
        return {"output": self.output}


def request(**overrides):
    values = {
        "request_id": "behavior-1",
        "task_type": "test",
        "data_class": "INTERNAL",
        "required_capabilities": frozenset({"text"}),
        "cost_ceiling": 0.0,
        "input": "hello",
        "intent": "complete the requested task",
        "success_criteria": ("verified result",),
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


class FrontierBehaviorTests(unittest.TestCase):
    def test_high_consequence_escalates_to_deep_with_budget(self):
        req = request(consequence_level="HIGH")
        engine = BehaviorEngine()
        preflight = engine.preflight(req)
        evidence = engine.evidence(req, preflight)
        self.assertEqual(preflight.reasoning_effort, "DEEP")
        self.assertEqual(evidence["step_budget"], 12)

    def test_high_uncertainty_escalates_to_deep(self):
        verdict = BehaviorEngine().preflight(request(uncertainty=0.75))
        self.assertEqual(verdict.reasoning_effort, "DEEP")

    def test_grounded_profile_requires_provenance_before_provider(self):
        adapter = FakeAdapter()
        result = SharedAIRuntime([provider(adapter)]).execute(
            request(verification_profile="GROUNDED")
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "missing_provenance")
        self.assertEqual(adapter.calls, 0)

    def test_grounded_profile_records_provenance(self):
        result = SharedAIRuntime([provider()]).execute(
            request(
                verification_profile="GROUNDED",
                provenance=("source:a", "source:b"),
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.behavior_evidence["provenance_count"], 2)

    def test_resume_requires_context_id(self):
        result = SharedAIRuntime([provider()]).execute(
            request(resume_from="checkpoint-1")
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "invalid_resume_state")

    def test_resume_state_is_exposed_without_context_content(self):
        result = SharedAIRuntime([provider()]).execute(
            request(context_id="task-1", resume_from="checkpoint-1")
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.behavior_evidence["context_state"], "RESUMED")

    def test_unknown_capability_holds_before_route(self):
        result = SharedAIRuntime([provider()]).execute(
            request(required_capabilities=frozenset({"telepathy"}))
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "unknown_capability")

    def test_multimodal_capability_still_requires_provider_support(self):
        result = SharedAIRuntime([provider()]).execute(
            request(required_capabilities=frozenset({"vision"}))
        )
        self.assertEqual(result.state, "HOLD")
        self.assertIn("local_runtime:SKIP:capability", result.path)

    def test_tool_requirement_is_behavior_metadata_not_authority(self):
        req = request(required_capabilities=frozenset({"tool_calling"}))
        engine = BehaviorEngine()
        preflight = engine.preflight(req)
        evidence = engine.evidence(req, preflight)
        self.assertTrue(evidence["tool_required"])

    def test_structured_verification_uses_one_bounded_correction(self):
        adapter = FakeAdapter(outputs=["not-structured", {"ok": True}])
        p = provider(adapter)
        p.capabilities.add("structured_output")
        result = SharedAIRuntime([p]).execute(
            request(
                verification_profile="STRUCTURED",
                required_capabilities=frozenset({"structured_output"}),
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(result.behavior_evidence["correction_attempts"], 1)
        self.assertEqual(adapter.calls, 2)
        self.assertIn(
            "ENGURU_LANGUAGE_GOVERNANCE:ACTIVE",
            adapter.instructions[0],
        )
        self.assertIn(
            "LANGUAGE_MODE:POSITIVE_CONSTRUCTIVE_TRUTHFUL",
            adapter.instructions[0],
        )
        self.assertIn("structured_output_required", adapter.instructions[1])

    def test_correction_budget_stops_after_one_retry(self):
        adapter = FakeAdapter(outputs=["bad", "still-bad", {"late": True}])
        p = provider(adapter)
        p.capabilities.add("structured_output")
        result = SharedAIRuntime([p]).execute(
            request(
                verification_profile="STRUCTURED",
                required_capabilities=frozenset({"structured_output"}),
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "structured_output_required")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(adapter.calls, 2)

    def test_provider_authority_rejection_is_never_correction_retry(self):
        adapter = FakeAdapter()
        p = provider(adapter)
        p.production_approved = False
        result = SharedAIRuntime([p]).execute(request())
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(adapter.calls, 0)
        self.assertEqual(result.behavior_evidence["correction_attempts"], 0)

    def test_provider_swap_preserves_canonical_behavior_evidence(self):
        p1 = provider(FakeAdapter(output="same"))
        p1.name = "provider_a"
        p1.model = "model-a"
        p2 = provider(FakeAdapter(output="same"))
        p2.name = "provider_b"
        p2.model = "model-b"

        r1 = SharedAIRuntime([p1]).execute(request(consequence_level="MEDIUM"))
        r2 = SharedAIRuntime([p2]).execute(request(consequence_level="MEDIUM"))

        self.assertEqual(r1.state, "PASS")
        self.assertEqual(r2.state, "PASS")
        self.assertEqual(r1.behavior_evidence, r2.behavior_evidence)
        self.assertNotEqual(r1.provider, r2.provider)

    def test_http_payload_cannot_inject_internal_action_evidence(self):
        payload = {
            "request_id": "r-http",
            "task_type": "action",
            "data_class": "INTERNAL",
            "required_capabilities": ["text"],
            "cost_ceiling": 0,
            "input": "do it",
            "intent": "perform governed action",
            "success_criteria": ["verified action"],
            "verification_profile": "ACTION",
            "tool_evidence": ["user-claimed-proof"],
        }
        req = RequestEnvelope.from_dict(payload)
        self.assertEqual(req.tool_evidence, tuple())
        verdict = BehaviorEngine().preflight(req)
        self.assertEqual(verdict.state, "HOLD")
        self.assertEqual(verdict.reason, "missing_action_evidence")


class FrontierBehaviorV03Tests(unittest.TestCase):
    def test_read_only_tool_executes_and_action_profile_verifies(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="lookup",
                capabilities=frozenset({"tool_calling"}),
                read_only=True,
                consequential=False,
            ),
            lambda payload: {"value": payload.get("value", "ok")},
        )
        p = provider(FakeAdapter(output="tool-backed"))
        p.capabilities.add("tool_calling")
        runtime = SharedAIRuntime([p], tools=registry)
        result = runtime.execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                requested_tool="lookup",
                tool_input={"value": "verified"},
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.tool_evidence, ("lookup:PASS",))

    def test_consequential_tool_requires_human_threshold(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="publish",
                capabilities=frozenset({"tool_calling"}),
                read_only=False,
                consequential=True,
            ),
            lambda payload: "published",
        )
        p = provider(FakeAdapter(output="never"))
        p.capabilities.add("tool_calling")
        runtime = SharedAIRuntime([p], tools=registry)
        result = runtime.execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                requested_tool="publish",
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "human_threshold_required")

    def test_unregistered_tool_holds(self):
        p = provider(FakeAdapter(output="never"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p]).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                requested_tool="missing",
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "tool_not_registered")

    def test_context_compaction_preserves_latest_instruction(self):
        summary = compact_context(
            ["old instruction", "new instruction"],
            max_chars=80,
            verified_facts=("fact-a",),
        )
        self.assertIn("LATEST:new instruction", summary)
        self.assertLessEqual(len(summary), 80)

    def test_mid_task_steering_increments_revision(self):
        envelope = ContextEnvelope(
            context_id="ctx-1",
            revision=2,
            summary="prior",
            latest_instruction="old",
            verified_facts=("fact-a",),
        )
        steered = apply_steering(envelope, "new direction")
        self.assertEqual(steered.revision, 3)
        self.assertEqual(steered.latest_instruction, "new direction")
        self.assertEqual(steered.verified_facts, ("fact-a",))

    def test_runtime_marks_compacted_context_and_steering(self):
        result = SharedAIRuntime([provider()]).execute(
            request(
                context_messages=("old", "latest"),
                steering_instruction="override now",
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertTrue(result.behavior_evidence["context_compacted"])
        self.assertTrue(result.behavior_evidence["steering_applied"])

    def test_grounded_claim_without_known_truth_holds_as_unsupported(self):
        output = {"claims": ["claim-a"], "citations": ["source:a"]}
        result = SharedAIRuntime([provider(FakeAdapter(output=output))]).execute(
            request(
                verification_profile="GROUNDED",
                provenance=("source:a",),
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "unsupported_claim")
        self.assertEqual(result.behavior_evidence["unsupported_claim_count"], 1)

    def test_grounded_known_claim_passes_and_renders_citation(self):
        output = {"claims": ["claim-a"], "citations": ["source:a"]}
        req = request(
            verification_profile="GROUNDED",
            provenance=("source:a",),
            known_truths=("claim-a",),
        )
        result = SharedAIRuntime([provider(FakeAdapter(output=output))]).execute(req)
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.citations, ({"index": 1, "ref": "source:a"},))

    def test_unknown_citation_holds(self):
        output = {"claims": ["claim-a"], "citations": ["source:unknown"]}
        req = request(
            verification_profile="GROUNDED",
            provenance=("source:a",),
            known_truths=("claim-a",),
        )
        result = SharedAIRuntime([provider(FakeAdapter(output=output))]).execute(req)
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "unknown_citation")

    def test_explicit_contradiction_holds(self):
        output = {"contradictions": ["claim-a conflicts with claim-b"]}
        result = SharedAIRuntime([provider(FakeAdapter(output=output))]).execute(request())
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "contradiction_detected")

    def test_http_caller_cannot_inject_known_truths_or_tool_evidence(self):
        req = RequestEnvelope.from_dict({
            "request_id": "r-v03",
            "task_type": "test",
            "data_class": "INTERNAL",
            "required_capabilities": ["text"],
            "cost_ceiling": 0,
            "input": "hello",
            "known_truths": ["caller-truth"],
            "tool_evidence": ["caller-tool-proof"],
        })
        self.assertEqual(req.known_truths, tuple())
        self.assertEqual(req.tool_evidence, tuple())


class PolishP1IntentGroundingGovernanceTests(unittest.TestCase):
    def test_missing_intent_holds_before_provider(self):
        adapter = FakeAdapter()
        result = SharedAIRuntime([provider(adapter)]).execute(request(intent=""))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "missing_intent")
        self.assertEqual(adapter.calls, 0)

    def test_missing_success_criteria_holds(self):
        result = SharedAIRuntime([provider()]).execute(request(success_criteria=tuple()))
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "missing_success_criteria")

    def test_missing_critical_context_holds(self):
        result = SharedAIRuntime([provider()]).execute(
            request(critical_context_complete=False)
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "missing_critical_context")

    def test_stale_conflicting_incomplete_ambiguous_unknown_grounding_hold(self):
        expected = {
            "STALE": "grounding_stale",
            "CONFLICTING": "grounding_conflicting",
            "INCOMPLETE": "grounding_incomplete",
            "AMBIGUOUS": "grounding_ambiguous",
            "UNKNOWN": "grounding_unknown",
        }
        for status, reason in expected.items():
            with self.subTest(status=status):
                result = SharedAIRuntime([provider()]).execute(
                    request(grounding_status=status)
                )
                self.assertEqual(result.state, "HOLD")
                self.assertEqual(result.reason, reason)

    def test_freshness_requires_authoritative_current_source(self):
        result = SharedAIRuntime([provider()]).execute(
            request(freshness_required=True)
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "authoritative_current_source_required")

        result = SharedAIRuntime([provider()]).execute(
            request(
                freshness_required=True,
                authoritative_provenance=("authority:current",),
            )
        )
        self.assertEqual(result.state, "PASS")

    def test_irreversible_action_requires_human_threshold_before_provider(self):
        adapter = FakeAdapter()
        result = SharedAIRuntime([provider(adapter)]).execute(
            request(reversibility="IRREVERSIBLE")
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "human_threshold_required")
        self.assertEqual(adapter.calls, 0)

    def test_external_reversible_action_can_continue(self):
        result = SharedAIRuntime([provider()]).execute(
            request(reversibility="EXTERNAL_REVERSIBLE")
        )
        self.assertEqual(result.state, "PASS")

    def test_http_caller_cannot_self_grant_human_approval(self):
        payload = {
            "request_id": "p1-authority",
            "task_type": "action",
            "data_class": "INTERNAL",
            "required_capabilities": ["text"],
            "cost_ceiling": 0,
            "input": "perform action",
            "intent": "perform governed action",
            "success_criteria": ["completed"],
            "reversibility": "IRREVERSIBLE",
            "human_approval": True,
        }
        req = RequestEnvelope.from_dict(payload)
        self.assertFalse(req.human_approval)
        result = SharedAIRuntime([provider()]).execute(req)
        self.assertEqual(result.reason, "human_threshold_required")

    def test_secret_remains_local_only(self):
        remote = provider()
        remote.name = "remote"
        remote.local = False
        result = SharedAIRuntime([remote]).execute(request(data_class="SECRET"))
        self.assertEqual(result.state, "HOLD")
        self.assertIn("remote:SKIP:secret_local_only", result.path)

    def test_cost_ceiling_remains_fail_closed(self):
        paid = provider()
        paid.estimated_cost = 0.5
        result = SharedAIRuntime([paid]).execute(request(cost_ceiling=0.0))
        self.assertEqual(result.state, "HOLD")
        self.assertIn("local_runtime:SKIP:cost", result.path)

    def test_current_request_input_is_distinct_from_prior_context(self):
        adapter = FakeAdapter(output="ok")
        result = SharedAIRuntime([provider(adapter)]).execute(
            request(
                input="current request truth",
                context_messages=("stale prior context",),
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(adapter.calls, 1)


class PolishP2ReplanningMultiToolRecoveryTests(unittest.TestCase):
    def test_sequential_multi_tool_plan_executes_in_order(self):
        registry = ToolRegistry()
        calls = []
        registry.register(
            ToolSpec("one", frozenset({"tool_calling"}), read_only=True),
            lambda payload: calls.append("one") or "one-ok",
        )
        registry.register(
            ToolSpec("two", frozenset({"tool_calling"}), read_only=True),
            lambda payload: calls.append("two") or "two-ok",
        )
        p = provider(FakeAdapter(output="done"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                tool_plan=(
                    {"name": "one", "payload": {}},
                    {"name": "two", "payload": {}},
                ),
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(calls, ["one", "two"])
        self.assertEqual(result.tool_evidence, ("one:PASS", "two:PASS"))

    def test_parallel_plan_only_allows_read_only_non_consequential_tools(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec("a", frozenset({"tool_calling"}), read_only=True),
            lambda payload: "a-ok",
        )
        registry.register(
            ToolSpec("b", frozenset({"tool_calling"}), read_only=True),
            lambda payload: "b-ok",
        )
        p = provider(FakeAdapter(output="done"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                parallel_tools=True,
                tool_plan=(
                    {"name": "a", "payload": {}},
                    {"name": "b", "payload": {}},
                ),
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(set(result.tool_evidence), {"a:PASS", "b:PASS"})

    def test_parallel_plan_rejects_side_effecting_tool(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec("write", frozenset({"tool_calling"}), read_only=False),
            lambda payload: "write-ok",
        )
        p = provider(FakeAdapter(output="never"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                parallel_tools=True,
                tool_plan=({"name": "write", "payload": {}},),
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "parallel_side_effect_forbidden")

    def test_tool_failure_re_evaluates_to_declared_fallback(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec("broken", frozenset({"tool_calling"}), read_only=True),
            lambda payload: (_ for _ in ()).throw(RuntimeError("down")),
        )
        registry.register(
            ToolSpec("backup", frozenset({"tool_calling"}), read_only=True),
            lambda payload: "backup-ok",
        )
        p = provider(FakeAdapter(output="done"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                tool_plan=(
                    {
                        "name": "broken",
                        "payload": {},
                        "fallbacks": ["backup"],
                    },
                ),
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.tool_evidence, ("backup:PASS",))

    def test_human_threshold_tool_rejection_is_not_fallback(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                "publish",
                frozenset({"tool_calling"}),
                read_only=False,
                consequential=True,
            ),
            lambda payload: "published",
        )
        registry.register(
            ToolSpec("backup", frozenset({"tool_calling"}), read_only=True),
            lambda payload: "backup-ok",
        )
        p = provider(FakeAdapter(output="never"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                tool_plan=(
                    {
                        "name": "publish",
                        "payload": {},
                        "fallbacks": ["backup"],
                    },
                ),
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "human_threshold_required")

    def test_contradiction_triggers_one_bounded_replan(self):
        adapter = FakeAdapter(
            outputs=[
                {"contradictions": ["a conflicts b"]},
                "corrected",
            ]
        )
        result = SharedAIRuntime([provider(adapter)]).execute(request())
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(adapter.calls, 2)
        self.assertIn("contradiction_detected", adapter.instructions[1])

    def test_provider_failure_routes_to_next_safe_provider(self):
        bad = provider(FakeAdapter(output="unused"))
        bad.name = "bad"
        bad.adapter = FakeAdapter(error=RuntimeError("down"))
        good = provider(FakeAdapter(output="ok"))
        good.name = "good"
        result = SharedAIRuntime([bad, good]).execute(request())
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.provider, "good")
        self.assertIn("bad:ERROR:RuntimeError", result.path)


class PolishP3ExecutionObservationTests(unittest.TestCase):
    def test_execution_envelope_records_route_model_tools_attempts_latency_cost_and_evidence(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec("lookup", frozenset({"tool_calling"}), read_only=True),
            lambda payload: "lookup-ok",
        )
        p = provider(FakeAdapter(output="done"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                requested_tool="lookup",
                latency_class="LOW",
            )
        )
        self.assertEqual(result.state, "PASS")
        evidence = result.execution_evidence
        self.assertEqual(evidence["source_name"], "local_runtime")
        self.assertEqual(evidence["model"], "qwen3:14b")
        self.assertEqual(evidence["tools"], ["lookup"])
        self.assertEqual(evidence["attempts"], 1)
        self.assertEqual(evidence["latency_class"], "LOW")
        self.assertEqual(evidence["estimated_cost"], 0.0)
        self.assertIn("lookup:PASS", evidence["evidence_refs"])
        self.assertIn("local_runtime:PASS", evidence["route"])

    def test_malformed_provider_response_is_observed_and_routes_to_next_provider(self):
        class MalformedAdapter:
            def invoke(self, request):
                return "not-a-dict"

        bad = provider(MalformedAdapter())
        bad.name = "bad"
        good = provider(FakeAdapter(output="ok"))
        good.name = "good"
        result = SharedAIRuntime([bad, good]).execute(request())
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.provider, "good")
        self.assertIn("bad:OBSERVE:malformed_provider_response", result.path)

    def test_partial_provider_output_is_observed_and_not_accepted(self):
        class PartialAdapter:
            def invoke(self, request):
                return {"output": "half", "partial": True}

        bad = provider(PartialAdapter())
        bad.name = "partial"
        good = provider(FakeAdapter(output="complete"))
        good.name = "good"
        result = SharedAIRuntime([bad, good]).execute(request())
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.provider, "good")
        self.assertIn("partial:OBSERVE:partial_output", result.path)

    def test_provider_timeout_is_observed_and_routes_to_next_provider(self):
        bad = provider(FakeAdapter(error=TimeoutError("slow")))
        bad.name = "slow"
        good = provider(FakeAdapter(output="ok"))
        good.name = "good"
        result = SharedAIRuntime([bad, good]).execute(request())
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.provider, "good")
        self.assertIn("slow:TIMEOUT", result.path)

    def test_tool_capability_mismatch_holds_before_provider(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec("lookup", frozenset({"tool_calling"}), read_only=True),
            lambda payload: "ok",
        )
        p = provider(FakeAdapter(output="never"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                tool_plan=(
                    {
                        "name": "lookup",
                        "payload": {},
                        "required_capabilities": ["vision"],
                    },
                ),
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "tool_capability_mismatch")
        self.assertIn("tool_capability_mismatch", result.execution_evidence["observations"])

    def test_consequential_action_without_completion_evidence_holds_after_side_effect(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                "publish",
                frozenset({"tool_calling"}),
                read_only=False,
                consequential=True,
            ),
            lambda payload: {"published": True},
        )
        p = provider(FakeAdapter(output="never"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                requested_tool="publish",
                reversibility="IRREVERSIBLE",
                human_approval=True,
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "missing_completion_evidence")
        self.assertEqual(result.execution_evidence["side_effect_state"], "COMPLETED")
        self.assertEqual(result.execution_evidence["completion_evidence"], [])

    def test_consequential_action_with_completion_evidence_is_separate_from_generation(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                "publish",
                frozenset({"tool_calling"}),
                read_only=False,
                consequential=True,
            ),
            lambda payload: {
                "published": True,
                "completion_evidence": ["receipt:123"],
            },
        )
        p = provider(FakeAdapter(output="reported"))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                requested_tool="publish",
                reversibility="IRREVERSIBLE",
                human_approval=True,
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.execution_evidence["side_effect_state"], "COMPLETED")
        self.assertEqual(
            result.execution_evidence["completion_evidence"],
            ["receipt:123"],
        )
        self.assertTrue(result.execution_evidence["output_present"])

    def test_side_effect_completion_survives_generation_failure(self):
        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                "publish",
                frozenset({"tool_calling"}),
                read_only=False,
                consequential=True,
            ),
            lambda payload: {
                "published": True,
                "completion_evidence": ["receipt:456"],
            },
        )
        p = provider(FakeAdapter(error=RuntimeError("provider down")))
        p.capabilities.add("tool_calling")
        result = SharedAIRuntime([p], tools=registry).execute(
            request(
                verification_profile="ACTION",
                required_capabilities=frozenset({"text", "tool_calling"}),
                requested_tool="publish",
                reversibility="IRREVERSIBLE",
                human_approval=True,
            )
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.execution_evidence["side_effect_state"], "COMPLETED")
        self.assertEqual(
            result.execution_evidence["completion_evidence"],
            ["receipt:456"],
        )


class PolishP4OutputMultimodalTests(unittest.TestCase):
    def test_requested_language_length_and_structure_reach_generation(self):
        adapter = FakeAdapter(output="yanıt")
        result = SharedAIRuntime([provider(adapter)]).execute(
            request(
                response_language="TR",
                response_length="CONCISE",
                response_structure="GOVERNED",
            )
        )
        self.assertEqual(result.state, "PASS")
        instruction = adapter.instructions[0]
        self.assertIn("RESPONSE_LANGUAGE:TR", instruction)
        self.assertIn("RESPONSE_LENGTH:CONCISE", instruction)
        self.assertIn("RESPONSE_STRUCTURE:GOVERNED", instruction)

    def test_governed_output_preserves_state_claim_evidence_next_action_order(self):
        output = {
            "answer": "claim-a",
            "next_action": "do-next",
            "facts": ["fact-a"],
        }
        result = SharedAIRuntime([provider(FakeAdapter(output=output))]).execute(
            request(response_structure="GOVERNED")
        )
        self.assertEqual(result.state, "PASS")
        keys = list(result.output.keys())
        self.assertEqual(keys[:4], ["state", "claim", "evidence", "next_action"])
        self.assertEqual(result.output["state"], "PASS")
        self.assertEqual(result.output["claim"], "claim-a")
        self.assertEqual(result.output["next_action"], "do-next")

    def test_claim_types_are_kept_distinct(self):
        output = {
            "answer": "summary",
            "facts": ["fact-a"],
            "inferences": ["inference-a"],
            "proposals": ["proposal-a"],
            "uncertainties": ["uncertain-a"],
        }
        result = SharedAIRuntime([provider(FakeAdapter(output=output))]).execute(
            request(response_structure="STRUCTURED")
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.output["facts"], ["fact-a"])
        self.assertEqual(result.output["inferences"], ["inference-a"])
        self.assertEqual(result.output["proposals"], ["proposal-a"])
        self.assertEqual(result.output["uncertainties"], ["uncertain-a"])

    def test_structured_output_is_machine_readable_when_requested(self):
        result = SharedAIRuntime([provider(FakeAdapter(output="hello"))]).execute(
            request(
                response_language="EN",
                response_length="CONCISE",
                response_structure="STRUCTURED",
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertIsInstance(result.output, dict)
        self.assertEqual(result.output["answer"], "hello")
        self.assertEqual(result.output["language"], "EN")
        self.assertEqual(result.output["length"], "CONCISE")
        self.assertEqual(result.output["structure"], "STRUCTURED")

    def test_technical_evidence_is_hidden_by_default_and_exposed_on_request(self):
        hidden = SharedAIRuntime([provider(FakeAdapter(output="hello"))]).execute(
            request(response_structure="STRUCTURED")
        )
        self.assertNotIn("technical_evidence", hidden.output)

        exposed = SharedAIRuntime([provider(FakeAdapter(output="hello"))]).execute(
            request(
                response_structure="STRUCTURED",
                include_technical_evidence=True,
            )
        )
        self.assertIn("technical_evidence", exposed.output)
        self.assertEqual(
            exposed.output["technical_evidence"]["source_name"],
            "local_runtime",
        )

    def test_plain_default_remains_backward_compatible(self):
        result = SharedAIRuntime([provider(FakeAdapter(output="plain"))]).execute(
            request()
        )
        self.assertEqual(result.output, "plain")

    def test_multimodal_aliases_normalize_before_provider_routing(self):
        p = provider(FakeAdapter(output="multi-ok"))
        p.capabilities.update({"vision", "file", "audio"})
        result = SharedAIRuntime([p]).execute(
            request(
                required_capabilities=frozenset(
                    {"text", "image", "document", "speech"}
                )
            )
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.provider, "local_runtime")

    def test_normalized_modality_still_requires_provider_support(self):
        p = provider(FakeAdapter(output="never"))
        result = SharedAIRuntime([p]).execute(
            request(required_capabilities=frozenset({"image"}))
        )
        self.assertEqual(result.state, "HOLD")
        self.assertIn("local_runtime:SKIP:capability", result.path)

    def test_invalid_output_profile_holds_before_provider(self):
        adapter = FakeAdapter(output="never")
        result = SharedAIRuntime([provider(adapter)]).execute(
            request(response_structure="UNKNOWN")
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "invalid_response_structure")
        self.assertEqual(adapter.calls, 0)

class PositiveGovernanceLanguageTests(unittest.TestCase):
    def test_canonical_governance_instruction_is_action_oriented(self):
        instruction = BehaviorEngine.governance_instruction()

        required = [
            "ENGURU_LANGUAGE_GOVERNANCE:ACTIVE",
            "PRINCIPLE:mevcut hakikat + gerekli fark",
            "LANGUAGE_MODE:POSITIVE_CONSTRUCTIVE_TRUTHFUL",
            "INSTRUCTION_STYLE:ACTION_ORIENTED",
            "STATE:",
            "CLAIM:",
            "EVIDENCE:",
            "NEXT_ACTION:",
            "AUTHORITY_RULE:",
            "FINISH_RULE:",
            "CLOSURE_RULE:",
        ]

        for item in required:
            self.assertIn(item, instruction)

        for negative_command in [
            "DO NOT",
            "MUST NOT",
            "NEVER ",
        ]:
            self.assertNotIn(negative_command, instruction.upper())

    def test_every_provider_request_receives_governance_alignment(self):
        adapter = FakeAdapter(output="aligned")
        result = SharedAIRuntime([provider(adapter)]).execute(request())

        self.assertEqual(result.state, "PASS")
        self.assertEqual(adapter.calls, 1)

        instruction = adapter.instructions[0]

        self.assertIn(
            "ENGURU_LANGUAGE_GOVERNANCE:ACTIVE",
            instruction,
        )
        self.assertIn(
            "LANGUAGE_MODE:POSITIVE_CONSTRUCTIVE_TRUTHFUL",
            instruction,
        )
        self.assertIn(
            "NEXT_ACTION: state the safest necessary constructive forward action.",
            instruction,
        )

    def test_behavior_version_records_positive_language_revision(self):
        self.assertEqual(BehaviorEngine.version, "0.8")

