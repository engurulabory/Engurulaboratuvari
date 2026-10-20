import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools/plive_p02_integrated_six_gate_audit_v1.py"
spec = importlib.util.spec_from_file_location("sixgate", MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture():
    return {"schema": m.SCHEMA, "policySha256": "a"*64, "localHead": "b"*40,
            "gates": {name: {"engineeringEvidenceSha256": "c"*64, "reviewed": True}
                      for name in m.GATES}}

def render(value):
    return json.dumps(value, separators=(",", ":")).encode()

class IntegratedAuditTests(unittest.TestCase):
    def test_all_reviewed_never_native_pass(self):
        r = m.audit(render(fixture()))
        self.assertEqual(r["state"], "PASS_BOUNDED_ENGINEERING_AUDIT__OFFICIAL_HOLD")
        self.assertEqual(len(r["gates"]), 6)
        self.assertEqual(r["verifiedFinish"], "HOLD")
        self.assertEqual(r["officialP02"], "HOLD")
        self.assertTrue(all(g["nativeAcceptance"].startswith("HOLD") for g in r["gates"]))
        self.assertEqual(r["canonicalWrites"], 0)

    def test_missing_evidence(self):
        f = fixture()
        f["gates"][m.GATES[2]]["engineeringEvidenceSha256"] = None
        self.assertEqual(m.audit(render(f))["gates"][2]["engineering"], "HOLD_EVIDENCE")

    def test_false_review(self):
        f = fixture()
        f["gates"][m.GATES[0]]["reviewed"] = False
        self.assertEqual(m.audit(render(f))["gates"][0]["engineering"], "HOLD_EVIDENCE")

    def test_fail_closed_invalid_inputs(self):
        cases = [b"{}", b"{", b'{"a":1,"a":2}', b'{"bad":NaN}', b"x"*(1024*1024+1)]
        for raw in cases:
            with self.subTest(raw=raw[:25]):
                self.assertEqual(m.audit(raw)["state"], "HOLD_INVALID_INPUT")

    def test_injected_authority_is_rejected(self):
        f = fixture()
        f["nativeAuthority"] = "PASS"
        self.assertEqual(m.audit(render(f))["state"], "HOLD_INVALID_INPUT")
        f = fixture()
        f["gates"][m.GATES[0]]["nativeAcceptance"] = "PASS"
        self.assertEqual(m.audit(render(f))["state"], "HOLD_INVALID_INPUT")

    def test_evidence_pin(self):
        raw = render(fixture())
        self.assertEqual(m.audit(raw, expected_manifest_sha256=hashlib.sha256(raw).hexdigest())["state"],
                         "PASS_BOUNDED_ENGINEERING_AUDIT__OFFICIAL_HOLD")
        self.assertEqual(m.audit(raw, expected_manifest_sha256="0"*64)["state"], "HOLD_INVALID_INPUT")

    def test_rejects_extra_or_missing_gates(self):
        f = fixture()
        del f["gates"][m.GATES[5]]
        self.assertEqual(m.audit(render(f))["state"], "HOLD_INVALID_INPUT")
        f = fixture()
        f["gates"]["SHADOW_GATE"] = {"engineeringEvidenceSha256": "c"*64, "reviewed":True}
        self.assertEqual(m.audit(render(f))["state"], "HOLD_INVALID_INPUT")

    def test_exact_dependency_dag(self):
        r = m.audit(render(fixture()))
        self.assertEqual(r["gates"][3]["dependsOn"],
                         list(m.GATES[:3]))
        self.assertEqual(r["gates"][5]["dependsOn"], [m.GATES[4]])

if __name__ == "__main__":
    unittest.main()
