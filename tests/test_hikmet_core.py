import copy
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "hikmet_core.py"
SPEC = importlib.util.spec_from_file_location("hikmet_core", MODULE_PATH)
hikmet_core = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(hikmet_core)


def gate(verdict="PASS", evidence=None):
    return {
        "state": "observed state",
        "claim": "bounded claim",
        "evidence": ["verified evidence"] if evidence is None else evidence,
        "next_action": "none",
        "verdict": verdict,
    }


def record(verdict="PASS", human_threshold_required=False):
    payload = {name: gate() for name in hikmet_core.GATES}
    payload["human_threshold_required"] = human_threshold_required
    payload["overall_verdict"] = verdict
    return payload


class HikmetCoreTests(unittest.TestCase):
    def test_all_pass_derives_pass(self):
        payload = record("PASS")
        self.assertEqual(hikmet_core.derive_overall_verdict(payload), "PASS")
        self.assertEqual(hikmet_core.donecheck(payload)["verdict"], "PASS")

    def test_hold_prevents_pass(self):
        payload = record("HOLD")
        payload["reality"] = gate("HOLD", evidence=[])
        self.assertEqual(hikmet_core.derive_overall_verdict(payload), "HOLD")

    def test_blocked_dominates(self):
        payload = record("BLOCKED")
        payload["mizan"] = gate("BLOCKED")
        payload["consequence"] = gate("HOLD", evidence=[])
        self.assertEqual(hikmet_core.derive_overall_verdict(payload), "BLOCKED")

    def test_human_threshold_forces_hold(self):
        payload = record("HOLD", human_threshold_required=True)
        self.assertEqual(hikmet_core.derive_overall_verdict(payload), "HOLD")

    def test_false_pass_is_caught_by_donecheck(self):
        payload = record("PASS")
        payload["responsibility"] = gate("HOLD", evidence=[])
        result = hikmet_core.donecheck(payload)
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["evidence"]["derived_overall_verdict"], "HOLD")

    def test_invalid_verdict_fails_contract(self):
        payload = record("PASS")
        payload["intent"]["verdict"] = "UNKNOWN"
        with self.assertRaises(hikmet_core.HikmetContractError):
            hikmet_core.validate_record(payload)

    def test_missing_claim_fails_contract(self):
        payload = record("PASS")
        del payload["intent"]["claim"]
        with self.assertRaises(hikmet_core.HikmetContractError):
            hikmet_core.validate_record(payload)

    def test_schema_is_valid_json_and_has_seven_gates(self):
        schema_path = ROOT / "governance" / "ENGURU_HIKMET_CORE_V0_1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for name in hikmet_core.GATES:
            self.assertIn(name, schema["required"])
            self.assertIn(name, schema["properties"])
        self.assertEqual(
            schema["$defs"]["verdict"]["enum"], ["PASS", "HOLD", "BLOCKED"]
        )


if __name__ == "__main__":
    unittest.main()
