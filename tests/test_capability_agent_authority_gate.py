import copy
import importlib.util
import json
import unittest
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


if __name__ == "__main__":
    unittest.main()
