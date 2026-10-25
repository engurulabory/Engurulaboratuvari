import copy
import importlib.util
import json
import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "capability_agent_authority_gate.py"
spec = importlib.util.spec_from_file_location("capability_agent_authority_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


BASE = {
    "schemaVersion": "0.1",
    "actor": {"id": "astra", "type": "agent", "parentId": None, "authorityLevel": "L3"},
    "task": {"id": "T-1", "scope": ["repository"], "successCriteria": ["tests pass"]},
    "capabilities": {"detected": ["repo_write"], "approved": ["repo_write"]},
    "authority": {
        "requestedLevel": "L3",
        "explicitGrant": True,
        "allowedActions": ["repo_write"],
        "forbiddenActions": ["payment"],
        "policyCeiling": "L4"
    },
    "delegation": {"allowed": False, "depth": 0, "maxDepth": 0, "transferableAuthority": False},
    "credentials": {"inheritance": False, "approvedCredentials": []},
    "risk": {"blastRadius": "repository", "reversible": True, "externalEffect": False, "financial": False, "legal": False},
    "verification": {
        "evidenceRequired": True,
        "evidenceRefs": ["test://unit"],
        "independentVerifierRequired": False,
        "actorIsFinalVerifier": False
    },
    "humanThreshold": {"required": False, "approved": False, "reason": None},
    "autonomyWindow": {"active": True, "remainingActions": 10},
    "selfModification": {"requested": False, "touchesGovernance": False},
    "finalState": {"state": "UNEVALUATED", "reason": None, "nextAction": None}
}


class AuthorityGateTests(unittest.TestCase):
    def case(self):
        return copy.deepcopy(BASE)

    def test_baseline_passes(self):
        self.assertEqual(gate.evaluate(self.case())["state"], "PASS")

    def test_new_tool_without_approval_holds(self):
        c = self.case()
        c["capabilities"]["detected"].append("shell")
        result = gate.evaluate(c)
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["reason"], "CAPABILITY_ESCALATION_UNAPPROVED")

    def test_authority_above_policy_ceiling_blocks(self):
        c = self.case()
        c["authority"]["requestedLevel"] = "L5"
        result = gate.evaluate(c)
        self.assertEqual(result["state"], "BLOCKED")
        self.assertEqual(result["reason"], "AUTHORITY_SCOPE_VIOLATION")

    def test_authority_escalation_without_explicit_grant_holds(self):
        c = self.case()
        c["authority"]["requestedLevel"] = "L4"
        c["authority"]["explicitGrant"] = False
        result = gate.evaluate(c)
        self.assertEqual(result["state"], "HOLD")

    def test_transitive_authority_blocks(self):
        c = self.case()
        c["delegation"]["allowed"] = True
        c["delegation"]["depth"] = 1
        c["delegation"]["maxDepth"] = 1
        c["delegation"]["transferableAuthority"] = True
        result = gate.evaluate(c)
        self.assertEqual(result["reason"], "TRANSITIVE_AUTHORITY_ATTEMPT")
        self.assertEqual(result["state"], "BLOCKED")

    def test_unapproved_delegation_blocks(self):
        c = self.case()
        c["delegation"]["depth"] = 1
        c["delegation"]["maxDepth"] = 1
        result = gate.evaluate(c)
        self.assertEqual(result["reason"], "UNAPPROVED_DELEGATION")

    def test_delegation_depth_exceeded_blocks(self):
        c = self.case()
        c["delegation"]["allowed"] = True
        c["delegation"]["depth"] = 2
        c["delegation"]["maxDepth"] = 1
        result = gate.evaluate(c)
        self.assertEqual(result["reason"], "DELEGATION_DEPTH_EXCEEDED")

    def test_credential_inheritance_blocks(self):
        c = self.case()
        c["credentials"]["inheritance"] = True
        result = gate.evaluate(c)
        self.assertEqual(result["reason"], "CREDENTIAL_INHERITANCE_ATTEMPT")
        self.assertEqual(result["state"], "BLOCKED")

    def test_governance_self_modification_blocks(self):
        c = self.case()
        c["selfModification"] = {"requested": True, "touchesGovernance": True}
        result = gate.evaluate(c)
        self.assertEqual(result["reason"], "GOVERNANCE_BYPASS_ATTEMPT")

    def test_expired_autonomy_window_blocks(self):
        c = self.case()
        c["autonomyWindow"]["remainingActions"] = 0
        result = gate.evaluate(c)
        self.assertEqual(result["reason"], "AUTONOMY_WINDOW_EXPIRED")

    def test_critical_action_requires_human_threshold(self):
        c = self.case()
        c["risk"]["blastRadius"] = "production"
        c["risk"]["reversible"] = False
        result = gate.evaluate(c)
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["reason"], "HUMAN_THRESHOLD_REQUIRED")

    def test_declared_human_threshold_must_be_approved(self):
        c = self.case()
        c["risk"]["financial"] = True
        c["humanThreshold"] = {"required": True, "approved": False, "reason": "payment"}
        result = gate.evaluate(c)
        self.assertEqual(result["reason"], "IRREVERSIBLE_ACTION_UNAPPROVED")

    def test_actor_cannot_self_verify_when_independent_verifier_required(self):
        c = self.case()
        c["verification"]["independentVerifierRequired"] = True
        c["verification"]["actorIsFinalVerifier"] = True
        result = gate.evaluate(c)
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["reason"], "EVIDENCE_BYPASS_ATTEMPT")

    def test_missing_evidence_holds(self):
        c = self.case()
        c["verification"]["evidenceRefs"] = []
        result = gate.evaluate(c)
        self.assertEqual(result["reason"], "EVIDENCE_REQUIRED")

    def test_schema_is_closed_and_machine_readable(self):
        path = ROOT / "governance" / "ip-model-trust" / "CAPABILITY_AGENT_AUTHORITY.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["delegation"]["properties"]["transferableAuthority"]["const"], False)
        self.assertEqual(schema["properties"]["credentials"]["properties"]["inheritance"]["const"], False)

    def test_explicit_forbidden_action_blocks_even_with_capability_approval(self):
        for approved in (["payment"], []):
            c = self.case()
            c["capabilities"] = {"detected": ["payment"], "approved": approved}
            result = gate.evaluate(c)
            self.assertEqual(result["state"], "BLOCKED")
            self.assertEqual(result["reason"], "AUTHORITY_SCOPE_VIOLATION")

    def test_approved_capability_still_requires_allowed_action_scope(self):
        c = self.case()
        c["authority"]["allowedActions"] = []
        self.assertEqual(gate.evaluate(c)["state"], "BLOCKED")

    def test_string_approval_cannot_authorize_escalation_or_human_threshold(self):
        c = self.case()
        c["authority"].update(requestedLevel="L4", explicitGrant="false")
        self.assertEqual(gate.evaluate(c)["state"], "BLOCKED")
        c = self.case()
        c["risk"]["financial"] = True
        c["humanThreshold"] = {"required": True, "approved": "false", "reason": "payment"}
        self.assertEqual(gate.evaluate(c)["state"], "BLOCKED")

    def test_non_objects_and_malformed_nested_sections_block_without_exceptions(self):
        for value in (None, [], True, 7, "contract"):
            self.assertEqual(gate.evaluate(value)["state"], "BLOCKED")
        for section in ("actor", "task", "capabilities", "authority", "delegation", "credentials",
                        "risk", "verification", "humanThreshold", "finalState", "selfModification"):
            for value in (None, [], True, "false"):
                c = self.case()
                c[section] = value
                with self.subTest(section=section, value=value):
                    self.assertEqual(gate.evaluate(c)["state"], "BLOCKED")

    def test_missing_required_nested_fields_and_unknown_fields_block(self):
        schema = json.loads(gate.SCHEMA.read_text())
        for section, rule in schema["properties"].items():
            if type(BASE.get(section)) is dict:
                for field in rule.get("required", []):
                    c = self.case()
                    del c[section][field]
                    with self.subTest(section=section, missing=field):
                        self.assertEqual(gate.evaluate(c)["state"], "BLOCKED")
        c = self.case()
        c["grantOverride"] = True
        self.assertEqual(gate.evaluate(c)["state"], "BLOCKED")

    def test_numbers_strings_and_arrays_preserve_canonical_types(self):
        cases = [("delegation", "depth", True), ("delegation", "depth", -1),
                 ("delegation", "maxDepth", "2"), ("risk", "financial", 0),
                 ("risk", "reversible", "false"), ("capabilities", "detected", "repo_write"),
                 ("capabilities", "approved", [["repo_write"]]),
                 ("capabilities", "approved", ["repo_write", "repo_write"]),
                 ("verification", "evidenceRefs", "test://unit"),
                 ("verification", "evidenceRefs", [{}]),
                 ("verification", "evidenceRequired", False),
                 ("verification", "evidenceRequired", 1),
                 ("autonomyWindow", "remainingActions", True)]
        for section, field, value in cases:
            c = self.case()
            c[section][field] = value
            with self.subTest(section=section, field=field, value=value):
                self.assertEqual(gate.evaluate(c)["state"], "BLOCKED")

    def test_empty_or_whitespace_evidence_holds(self):
        for refs in ([], [""], [" "], ["test://unit", " "]):
            c = self.case()
            c["verification"]["evidenceRefs"] = refs
            self.assertEqual(gate.evaluate(c)["state"], "HOLD")

    def test_declared_pass_keeps_canonical_finish_in_its_own_gate(self):
        c = self.case()
        c["finalState"]["state"] = "PASS"
        result = gate.evaluate(c)
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["decisionScope"], "DECLARED_CONTRACT_POLICY")
        self.assertEqual(result["officialVerifiedFinish"], "HOLD_CANONICAL_DONECHECK_HUMAN_THRESHOLD")

    def test_real_cli_pass_hold_blocked_and_malformed_input_exit_codes(self):
        missing = self.case()
        missing["verification"]["evidenceRefs"] = []
        forbidden = self.case()
        forbidden["capabilities"] = {"detected": ["payment"], "approved": ["payment"]}
        samples = [(json.dumps(BASE).encode(), "PASS", 0),
                   (json.dumps(missing).encode(), "HOLD", 2),
                   (json.dumps(forbidden).encode(), "BLOCKED", 3),
                   (b"null", "BLOCKED", 3), (b"[]", "BLOCKED", 3),
                   (b"{bad-json", "BLOCKED", 3), (b"\xff", "BLOCKED", 3),
                   (b"[" * 2000 + b"]" * 2000, "BLOCKED", 3),
                   (json.dumps(BASE).replace('"explicitGrant": true',
                      '"explicitGrant": false, "explicitGrant": true').encode(), "BLOCKED", 3)]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contract.json"
            for raw, state, code in samples:
                path.write_bytes(raw)
                run = subprocess.run([sys.executable, "-B", str(MODULE_PATH), "--contract", str(path)],
                                     capture_output=True, text=True, timeout=10)
                self.assertEqual(run.returncode, code, run.stderr)
                self.assertEqual(json.loads(run.stdout)["state"], state)
                self.assertNotIn("Traceback", run.stderr)
            absent = subprocess.run([sys.executable, "-B", str(MODULE_PATH), "--contract", str(Path(tmp)/"absent.json")],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(absent.returncode, 3)
            self.assertEqual(json.loads(absent.stdout)["state"], "BLOCKED")
            path.write_text(json.dumps(BASE))
            occupied = Path(tmp) / "occupied"
            occupied.write_text("existing file")
            failed_output = subprocess.run([sys.executable, "-B", str(MODULE_PATH), "--contract", str(path),
                                            "--output", str(occupied / "receipt.json")],
                                           capture_output=True, text=True, timeout=10)
            self.assertEqual(failed_output.returncode, 3)
            self.assertEqual(json.loads(failed_output.stdout)["reason"], "EVIDENCE_OUTPUT_UNWRITABLE")
        print("AGENT_REAL_CLI=PASS:0,HOLD:2,BLOCKED:3; MALFORMED_INPUT=BLOCKED; FORBIDDEN_ACTION=BLOCKED")


if __name__ == "__main__":
    unittest.main()
