import unittest

from tools.shared_ai_offline_harness import Provider, Request, run

class SharedAIOfflineTests(unittest.TestCase):
    def test_success_200(self):
        r = run(Request(), [Provider("p1")])
        self.assertEqual(r.state, "PASS")
        self.assertEqual(r.provider, "p1")

    def test_timeout_retries_then_succeeds(self):
        p = Provider("p1", failures=["timeout", "200"])
        r = run(Request(), [p])
        self.assertEqual(r.state, "PASS")
        self.assertEqual(r.attempts, 2)

    def test_500_failover(self):
        p1 = Provider("p1", failures=["500", "500"])
        p2 = Provider("p2")
        r = run(Request(), [p1, p2])
        self.assertEqual(r.provider, "p2")

    def test_503_failover(self):
        p1 = Provider("p1", failures=["503", "503"])
        p2 = Provider("p2")
        r = run(Request(), [p1, p2])
        self.assertEqual(r.provider, "p2")

    def test_429_no_blind_retry_same_provider(self):
        p1 = Provider("p1", failures=["429"])
        p2 = Provider("p2")
        r = run(Request(), [p1, p2])
        self.assertEqual(p1.calls, 1)
        self.assertEqual(r.provider, "p2")

    def test_auth_401_no_retry(self):
        p1 = Provider("p1", failures=["401"])
        p2 = Provider("p2")
        r = run(Request(), [p1, p2])
        self.assertEqual(p1.calls, 1)
        self.assertEqual(r.provider, "p2")

    def test_policy_403_no_retry(self):
        p1 = Provider("p1", failures=["403"])
        p2 = Provider("p2")
        r = run(Request(), [p1, p2])
        self.assertEqual(p1.calls, 1)
        self.assertEqual(r.provider, "p2")

    def test_secret_external_blocked_local_used(self):
        ext = Provider("external")
        local = Provider("local", local=True)
        r = run(Request(data_class="SECRET"), [ext, local])
        self.assertEqual(ext.calls, 0)
        self.assertEqual(r.provider, "local")

    def test_paid_cost_blocked(self):
        paid = Provider("paid", estimated_cost=0.01)
        free = Provider("free", estimated_cost=0.0)
        r = run(Request(cost_ceiling=0.0), [paid, free])
        self.assertEqual(paid.calls, 0)
        self.assertEqual(r.provider, "free")

    def test_unverified_privacy_blocked(self):
        bad = Provider("bad", privacy_verified=False)
        good = Provider("good")
        r = run(Request(), [bad, good])
        self.assertEqual(bad.calls, 0)
        self.assertEqual(r.provider, "good")

    def test_unverified_commercial_use_blocked(self):
        bad = Provider("bad", commercial_use_verified=False)
        good = Provider("good")
        r = run(Request(), [bad, good])
        self.assertEqual(bad.calls, 0)
        self.assertEqual(r.provider, "good")

    def test_capability_mismatch_skipped(self):
        p1 = Provider("p1", supports={"text"})
        p2 = Provider("p2", supports={"text", "vision"})
        r = run(Request(required_capabilities={"vision"}), [p1, p2])
        self.assertEqual(p1.calls, 0)
        self.assertEqual(r.provider, "p2")

    def test_all_external_down_local_fallback(self):
        p1 = Provider("p1", healthy=False)
        p2 = Provider("p2", healthy=False)
        local = Provider("local", local=True)
        r = run(Request(), [p1, p2, local])
        self.assertEqual(r.provider, "local")

    def test_all_unavailable_hold(self):
        r = run(Request(), [Provider("p1", healthy=False)])
        self.assertEqual(r.state, "HOLD")

    def test_malformed_json_failover(self):
        p1 = Provider("p1", failures=["malformed_json"])
        p2 = Provider("p2")
        r = run(Request(), [p1, p2])
        self.assertEqual(r.provider, "p2")

    def test_invalid_structured_output_failover(self):
        p1 = Provider("p1", failures=["invalid_structured_output"])
        p2 = Provider("p2")
        r = run(Request(required_capabilities={"structured_output"}), [p1, p2])
        self.assertEqual(r.provider, "p2")

    def test_tool_call_mismatch_failover(self):
        p1 = Provider("p1", failures=["tool_call_mismatch"], supports={"text","tool_calling"})
        p2 = Provider("p2", supports={"text","tool_calling"})
        r = run(Request(required_capabilities={"tool_calling"}), [p1, p2])
        self.assertEqual(r.provider, "p2")

    def test_context_overflow_failover(self):
        p1 = Provider("p1", failures=["context_overflow"])
        p2 = Provider("p2")
        r = run(Request(), [p1, p2])
        self.assertEqual(r.provider, "p2")

    def test_partial_stream_retry_then_success(self):
        p = Provider("p1", failures=["partial_stream","200"])
        r = run(Request(), [p])
        self.assertEqual(r.state, "PASS")
        self.assertEqual(r.attempts, 2)

    def test_circuit_breaker_opens_after_three_failures(self):
        p = Provider("p1", failures=["500","500","500","200"])
        run(Request(), [p], max_attempts_per_provider=2)
        run(Request(), [p], max_attempts_per_provider=2)
        self.assertTrue(p.circuit_open)

    def test_retry_storm_bounded(self):
        p = Provider("p1", failures=["timeout"] * 10)
        r = run(Request(), [p], max_attempts_per_provider=2)
        self.assertEqual(r.attempts, 2)

    def test_no_authority_no_execution(self):
        p = Provider("p1", production_approved=False)
        r = run(Request(), [p])
        self.assertEqual(p.calls, 0)
        self.assertEqual(r.state, "HOLD")

if __name__ == "__main__":
    unittest.main()
