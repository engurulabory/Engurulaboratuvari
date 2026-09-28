from __future__ import annotations

import base64
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest
from unittest import mock
import uuid

import tools.mac_engineer_v08_gate12_reviewer_authority as authority


ROOT = Path(__file__).resolve().parents[1]
CONTROL_HEAD = "3345b911dfbb92db0b2636b45085365de8276a9e"
PRODUCT_HEAD = "0ca33cc7b70fee915d02de72946bbd4bb0e40065"
OBSERVED_AT = "2026-09-28T09:00:00Z"
SIGNED_AT = "2026-09-28T08:00:00Z"


class TestOnlyReplayBackend:
    def __init__(self, *, durable: bool = True) -> None:
        self.durable = durable
        self.by_decision: dict[str, dict[str, str]] = {}
        self.by_candidate: dict[str, dict[str, str]] = {}

    def get_decision(self, decision_id: str) -> dict[str, str] | None:
        return self.by_decision.get(decision_id)

    def get_terminal_candidate(
        self, terminal_candidate_id: str
    ) -> dict[str, str] | None:
        return self.by_candidate.get(terminal_candidate_id)

    def remember(self, envelope: dict) -> None:
        payload = envelope["payload"]
        record = {
            "decisionId": payload["decisionId"],
            "terminalCandidateId": authority.terminal_candidate_id(payload),
            "payloadDigest": envelope["payloadDigest"],
            "envelopeDigest": authority.digest(envelope),
            "decision": payload["decision"],
        }
        self.by_decision[record["decisionId"]] = record
        self.by_candidate[record["terminalCandidateId"]] = record


KEY_HELPER = r"""
import { createHash, createPrivateKey, generateKeyPairSync, sign } from "node:crypto";
import { pathToFileURL } from "node:url";

const runtime = await import(pathToFileURL(process.env.ENGURU_CANONICAL_JSON).href);
const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);
const input = JSON.parse(Buffer.concat(chunks).toString("utf8"));
if (input.operation === "generate") {
  const pair = generateKeyPairSync("ed25519");
  const publicDer = pair.publicKey.export({ type: "spki", format: "der" });
  process.stdout.write(JSON.stringify({
    publicKeyPem: pair.publicKey.export({ type: "spki", format: "pem" }).toString(),
    privateKeyPem: pair.privateKey.export({ type: "pkcs8", format: "pem" }).toString(),
    fingerprint: "sha256:" + createHash("sha256").update(publicDer).digest("hex"),
  }));
} else if (input.operation === "sign") {
  const material = runtime.canonicalJson({
    schema: input.attestationSchema,
    signedAt: input.signedAt,
    payload: input.payload,
  });
  const signature = sign(
    null,
    Buffer.from(material, "utf8"),
    createPrivateKey(input.privateKeyPem),
  );
  process.stdout.write(JSON.stringify({ signatureBase64: signature.toString("base64") }));
} else {
  throw new Error("unsupported operation");
}
"""


def run_key_helper(payload: dict) -> dict:
    result = subprocess.run(
        ["node", "--input-type=module", "-e", KEY_HELPER],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
        env={
            "PATH": __import__("os").environ["PATH"],
            "ENGURU_CANONICAL_JSON": str(authority.DONECHECK_CANONICAL_JSON),
        },
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class Gate12ReviewerAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        keys = run_key_helper({"operation": "generate"})
        cls.private_key = keys["privateKeyPem"]
        cls.public_key = keys["publicKeyPem"]
        cls.fingerprint = keys["fingerprint"]
        keys_b = run_key_helper({"operation": "generate"})
        cls.private_key_b = keys_b["privateKeyPem"]
        cls.public_key_b = keys_b["publicKeyPem"]
        cls.fingerprint_b = keys_b["fingerprint"]

    def make_authority(self) -> dict:
        value = {
            "schema": authority.AUTHORITY_SCHEMA_ID,
            "authorityVersion": 1,
            "status": "ACTIVE",
            "validFrom": "2026-09-28T00:00:00Z",
            "expiresAt": "2026-10-28T00:00:00Z",
            "revokedAt": None,
            "revocationReason": None,
            "humanThresholdOwner": "TEST_ONLY_OWNER",
            "reviewer": {
                "reviewerId": "TEST_ONLY_REVIEWER",
                "keyId": "TEST_ONLY_KEY",
                "algorithm": "ed25519",
                "publicKeyPem": self.public_key,
                "publicKeyFingerprint": self.fingerprint,
            },
            "scope": {
                "objective": authority.OBJECTIVE,
                "gate": 12,
                "version": "v0.8",
                "exit": authority.EXIT,
                "doneCheckHumanReview": True,
                "gate12HumanThreshold": True,
            },
            "doneCheckAuthority": {
                "allowedDecisions": ["accepted", "revise", "rejected"]
            },
            "humanThresholdAuthority": {
                "allowedDecisions": ["ACCEPT", "HOLD"]
            },
            "payloadDigest": "",
        }
        value["payloadDigest"] = authority.authority_digest(value)
        return value

    def expected(self) -> dict:
        return {
            "controlHead": CONTROL_HEAD,
            "productHead": PRODUCT_HEAD,
            "machineResultDigest": "sha256:" + "1" * 64,
            "evidenceManifestDigest": "sha256:" + "2" * 64,
            "unresolvedDeferredLedgerDigest": "sha256:" + "3" * 64,
            "canonicalSnapshotDigest": "sha256:" + "4" * 64,
            "acceptanceContractDigest": "sha256:" + "5" * 64,
            "verifiedFinishReceiptDigest": "sha256:" + "6" * 64,
            "auditHead": "sha256:" + "7" * 64,
        }

    def make_envelope(
        self,
        auth: dict,
        expected: dict | None = None,
        *,
        signed_at: str = SIGNED_AT,
        private_key: str | None = None,
    ) -> dict:
        expected = deepcopy(expected or self.expected())
        payload = {
            "schema": authority.THRESHOLD_SCHEMA_ID,
            "decisionId": "",
            "authorityDigest": authority.authority_digest(auth),
            "reviewerId": auth["reviewer"]["reviewerId"],
            "keyId": auth["reviewer"]["keyId"],
            "controlHead": expected["controlHead"],
            "productHead": expected["productHead"],
            "doneCheckVersion": authority.DONECHECK_VERSION,
            "doneCheckSha": authority.DONECHECK_SHA,
            "machineResultDigest": expected["machineResultDigest"],
            "evidenceManifestDigest": expected["evidenceManifestDigest"],
            "unresolvedDeferredLedgerDigest": expected[
                "unresolvedDeferredLedgerDigest"
            ],
            "canonicalSnapshotDigest": expected["canonicalSnapshotDigest"],
            "acceptanceContractDigest": expected["acceptanceContractDigest"],
            "verifiedFinishReceiptDigest": expected[
                "verifiedFinishReceiptDigest"
            ],
            "auditHead": expected["auditHead"],
            "targetVersion": "v0.8",
            "intendedExit": authority.EXIT,
            "decision": "ACCEPT",
            "decidedAt": signed_at,
        }
        payload["decisionId"] = authority.decision_id(payload)
        envelope = {
            "payload": payload,
            "payloadDigest": authority.digest(payload),
            "attestation": {
                "scheme": "ed25519",
                "reviewerId": payload["reviewerId"],
                "keyId": payload["keyId"],
                "signedAt": signed_at,
                "signatureBase64": "",
            },
        }
        self.resign(envelope, private_key=private_key)
        return envelope

    def resign(self, envelope: dict, *, private_key: str | None = None) -> None:
        signed = run_key_helper(
            {
                "operation": "sign",
                "attestationSchema": authority.THRESHOLD_ATTESTATION_SCHEMA_ID,
                "signedAt": envelope["attestation"]["signedAt"],
                "payload": envelope["payload"],
                "privateKeyPem": private_key or self.private_key,
            }
        )
        envelope["attestation"]["signatureBase64"] = signed[
            "signatureBase64"
        ]

    def redigest_authority(self, value: dict) -> None:
        value["payloadDigest"] = authority.authority_digest(value)

    def finalize_payload(
        self,
        envelope: dict,
        *,
        resign: bool = True,
        private_key: str | None = None,
    ) -> None:
        envelope["payload"]["decisionId"] = authority.decision_id(
            envelope["payload"]
        )
        envelope["payloadDigest"] = authority.digest(envelope["payload"])
        if resign:
            self.resign(envelope, private_key=private_key)

    def verify(self, auth: dict, envelope: dict, **kwargs) -> dict:
        return authority.verify_threshold_envelope(
            auth,
            envelope,
            expected=self.expected(),
            observed_at=OBSERVED_AT,
            production_use=False,
            **kwargs,
        )

    def assert_hold(self, result: dict, error: str) -> None:
        self.assertEqual(result["state"], "HOLD", result)
        self.assertIn(error, result["errors"], result)
        self.assertFalse(result["createsDecision"])

    def test_positive_ephemeral_fixture_passes_without_creating_decision(self):
        auth = self.make_authority()
        result = self.verify(auth, self.make_envelope(auth))
        self.assertEqual(result["state"], "PASS", result)
        self.assertFalse(result["createsDecision"])

    def test_authority_schema_is_closed_and_no_production_artifact_exists(self):
        schema = json.loads(authority.AUTHORITY_SCHEMA.read_text())
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["properties"]["reviewer"]["additionalProperties"])
        self.assertNotIn("privateKey", json.dumps(schema))
        self.assertFalse(authority.EXPECTED_AUTHORITY_ARTIFACT.exists())

    def test_private_key_field_is_rejected(self):
        auth = self.make_authority()
        auth["reviewer"]["privateKeyPem"] = self.private_key
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertTrue(
            any(item.startswith("PRIVATE_KEY_MATERIAL_FORBIDDEN") for item in result["errors"])
        )

    def test_unknown_reviewer_is_rejected(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        envelope["payload"]["reviewerId"] = "TEST_ONLY_UNKNOWN"
        envelope["attestation"]["reviewerId"] = "TEST_ONLY_UNKNOWN"
        self.finalize_payload(envelope)
        self.assert_hold(self.verify(auth, envelope), "UNKNOWN_REVIEWER")

    def test_wrong_key_id_is_rejected(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        envelope["payload"]["keyId"] = "TEST_ONLY_WRONG_KEY"
        envelope["attestation"]["keyId"] = "TEST_ONLY_WRONG_KEY"
        self.finalize_payload(envelope)
        self.assert_hold(self.verify(auth, envelope), "WRONG_KEY_ID")

    def test_invalid_public_key_is_rejected(self):
        auth = self.make_authority()
        auth["reviewer"]["publicKeyPem"] = "not-a-public-key"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("ED25519_PUBLIC_KEY_INVALID", result["errors"])

    def test_fingerprint_mismatch_is_rejected(self):
        auth = self.make_authority()
        auth["reviewer"]["publicKeyFingerprint"] = "sha256:" + "0" * 64
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("PUBLIC_KEY_FINGERPRINT_MISMATCH", result["errors"])

    def test_algorithm_mismatch_is_rejected(self):
        auth = self.make_authority()
        auth["reviewer"]["algorithm"] = "rsa"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("ED25519_ALGORITHM_REQUIRED", result["errors"])

    def test_objective_scope_mismatch_is_rejected(self):
        auth = self.make_authority()
        auth["scope"]["objective"] = "WRONG"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("SCOPE_OBJECTIVE_MISMATCH", result["errors"])

    def test_gate_scope_mismatch_is_rejected(self):
        auth = self.make_authority()
        auth["scope"]["gate"] = 11
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("SCOPE_GATE_MISMATCH", result["errors"])

    def test_version_scope_mismatch_is_rejected(self):
        auth = self.make_authority()
        auth["scope"]["version"] = "v1.3"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("SCOPE_VERSION_MISMATCH", result["errors"])

    def test_exit_scope_mismatch_is_rejected(self):
        auth = self.make_authority()
        auth["scope"]["exit"] = "WRONG"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("SCOPE_EXIT_MISMATCH", result["errors"])

    def test_unauthorized_donecheck_accept_decision_is_rejected(self):
        auth = self.make_authority()
        auth["doneCheckAuthority"]["allowedDecisions"] = ["approve"]
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("DONECHECK_ALLOWED_DECISIONS_INVALID", result["errors"])

    def test_unauthorized_human_threshold_accept_is_rejected(self):
        auth = self.make_authority()
        auth["humanThresholdAuthority"]["allowedDecisions"] = ["HOLD"]
        self.redigest_authority(auth)
        envelope = self.make_envelope(auth)
        self.assert_hold(
            self.verify(auth, envelope),
            "UNAUTHORIZED_HUMAN_THRESHOLD_DECISION",
        )

    def test_future_valid_from_is_rejected(self):
        auth = self.make_authority()
        auth["validFrom"] = "2026-09-29T00:00:00Z"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("AUTHORITY_NOT_YET_VALID", result["errors"])

    def test_expired_authority_is_rejected(self):
        auth = self.make_authority()
        auth["expiresAt"] = "2026-09-27T00:00:00Z"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("AUTHORITY_EXPIRED", result["errors"])

    def test_revoked_authority_is_rejected(self):
        auth = self.make_authority()
        auth["status"] = "REVOKED"
        auth["revokedAt"] = "2026-09-28T01:00:00Z"
        auth["revocationReason"] = "TEST_ONLY_REVOCATION"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("AUTHORITY_REVOKED", result["errors"])

    def test_authority_payload_digest_mismatch_is_rejected(self):
        auth = self.make_authority()
        auth["payloadDigest"] = "sha256:" + "0" * 64
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertIn("AUTHORITY_PAYLOAD_DIGEST_MISMATCH", result["errors"])

    def test_signature_mismatch_is_rejected(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        raw = bytearray(base64.b64decode(envelope["attestation"]["signatureBase64"]))
        raw[0] ^= 1
        envelope["attestation"]["signatureBase64"] = base64.b64encode(raw).decode()
        self.assert_hold(
            self.verify(auth, envelope), "THRESHOLD_SIGNATURE_INVALID"
        )

    def assert_bound_value_rejected(self, key: str, error: str) -> None:
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        envelope["payload"][key] = "sha256:" + "a" * 64
        if key in {"controlHead", "productHead", "doneCheckSha"}:
            envelope["payload"][key] = "wrong"
        self.finalize_payload(envelope)
        self.assert_hold(self.verify(auth, envelope), error)

    def test_wrong_control_head_is_rejected(self):
        self.assert_bound_value_rejected("controlHead", "CONTROLHEAD_MISMATCH")

    def test_wrong_product_head_is_rejected(self):
        self.assert_bound_value_rejected("productHead", "PRODUCTHEAD_MISMATCH")

    def test_wrong_donecheck_sha_is_rejected(self):
        self.assert_bound_value_rejected("doneCheckSha", "DONECHECKSHA_MISMATCH")

    def test_altered_evidence_digest_is_rejected(self):
        self.assert_bound_value_rejected(
            "evidenceManifestDigest", "EVIDENCEMANIFESTDIGEST_MISMATCH"
        )

    def test_altered_acceptance_contract_digest_is_rejected(self):
        self.assert_bound_value_rejected(
            "acceptanceContractDigest", "ACCEPTANCECONTRACTDIGEST_MISMATCH"
        )

    def test_altered_verified_finish_digest_is_rejected(self):
        self.assert_bound_value_rejected(
            "verifiedFinishReceiptDigest", "VERIFIEDFINISHRECEIPTDIGEST_MISMATCH"
        )

    def test_duplicate_decision_id_with_different_payload_is_rejected(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        replay = TestOnlyReplayBackend()
        replay.remember(envelope)
        envelope["payload"]["decidedAt"] = "2026-09-28T08:00:01Z"
        envelope["attestation"]["signedAt"] = "2026-09-28T08:00:01Z"
        self.finalize_payload(envelope)
        self.assert_hold(
            self.verify(auth, envelope, replay_backend=replay),
            "REPLAY_ID_CONTENT_CONFLICT",
        )

    def test_exact_replay_is_idempotent_for_validation(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        replay = TestOnlyReplayBackend()
        replay.remember(envelope)
        result = self.verify(auth, envelope, replay_backend=replay)
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["replayDisposition"], "IDEMPOTENT")

    def test_stale_authority_digest_is_rejected(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        envelope["payload"]["authorityDigest"] = "sha256:" + "e" * 64
        self.finalize_payload(envelope)
        self.assert_hold(self.verify(auth, envelope), "STALE_AUTHORITY_DIGEST")

    def test_strict_json_rejects_duplicate_security_keys_at_any_depth(self):
        fields = (
            "reviewerId",
            "keyId",
            "status",
            "publicKeyPem",
            "objective",
            "gate",
            "decision",
            "controlHead",
            "authorityDigest",
            "payloadDigest",
        )
        for field in fields:
            with self.subTest(field=field):
                value, errors = authority.strict_json_loads(
                    '{"outer":{"%s":1,"%s":2}}' % (field, field)
                )
                self.assertIsNone(value)
                self.assertIn(f"DUPLICATE_JSON_KEY:{field}", errors)

    def test_authority_json_ingestion_rejects_duplicate_status(self):
        auth = self.make_authority()
        text = json.dumps(auth).replace(
            '"status": "ACTIVE"',
            '"status": "ACTIVE", "status": "REVOKED"',
            1,
        )
        result = authority.verify_authority_json(
            text, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("DUPLICATE_JSON_KEY:status", result["errors"])

    def test_envelope_json_ingestion_rejects_duplicate_decision(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        text = json.dumps(envelope).replace(
            '"decision": "ACCEPT"',
            '"decision": "ACCEPT", "decision": "HOLD"',
            1,
        )
        result = authority.verify_threshold_envelope_json(
            json.dumps(auth),
            text,
            expected=self.expected(),
            observed_at=OBSERVED_AT,
            production_use=False,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("ENVELOPE_DUPLICATE_JSON_KEY:decision", result["errors"])

    def test_malformed_non_object_authority_roots_return_structured_hold(self):
        for value in (None, [], "string", 42):
            with self.subTest(value=value):
                result = authority.verify_authority(
                    value, observed_at=OBSERVED_AT, production_use=False
                )
                self.assertEqual(result["state"], "HOLD")
                self.assertEqual(result["errors"], ["AUTHORITY_OBJECT_REQUIRED"])

    def test_declared_schema_participates_in_validation(self):
        auth = self.make_authority()
        auth["unexpectedSecurityField"] = True
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertTrue(
            any(item.startswith("SCHEMA_ADDITIONAL_PROPERTY") for item in result["errors"])
        )

    def test_old_space_separated_timestamp_false_pass_is_closed(self):
        auth = self.make_authority()
        auth["validFrom"] = "2026-09-28 00:00:00Z"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("VALID_FROM_RFC3339_DATE_TIME_REQUIRED", result["errors"])

    def test_old_offset_seconds_timestamp_false_pass_is_closed(self):
        auth = self.make_authority()
        auth["validFrom"] = "2026-09-28T00:00:00+00:00:30"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth, observed_at=OBSERVED_AT, production_use=False
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("VALID_FROM_RFC3339_DATE_TIME_REQUIRED", result["errors"])

    def authority_window(self) -> dict:
        auth = self.make_authority()
        auth["validFrom"] = "2026-09-28T08:00:00Z"
        auth["expiresAt"] = "2026-09-28T09:00:00Z"
        self.redigest_authority(auth)
        return auth

    def test_authority_interval_reversed_is_rejected(self):
        auth = self.authority_window()
        auth["expiresAt"] = "2026-09-28T07:59:59Z"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth,
            observed_at="2026-09-28T08:30:00Z",
            production_use=False,
        )
        self.assertIn(
            "AUTHORITY_VALIDITY_INTERVAL_EMPTY_OR_REVERSED", result["errors"]
        )

    def test_revocation_before_validity_is_rejected(self):
        auth = self.authority_window()
        auth["status"] = "REVOKED"
        auth["revokedAt"] = "2026-09-28T07:59:59Z"
        auth["revocationReason"] = "TEST_ONLY_REVOKED"
        self.redigest_authority(auth)
        result = authority.verify_authority(
            auth,
            observed_at="2026-09-28T08:30:00Z",
            production_use=False,
        )
        self.assertIn("AUTHORITY_REVOCATION_BEFORE_VALIDITY", result["errors"])

    def test_signed_time_authority_boundaries(self):
        cases = (
            ("2026-09-28T07:59:59.999999Z", "HOLD"),
            ("2026-09-28T08:00:00Z", "PASS"),
            ("2026-09-28T08:59:59.999999Z", "PASS"),
            ("2026-09-28T09:00:00Z", "HOLD"),
            ("2026-09-28T09:00:00.000001Z", "HOLD"),
        )
        for signed_at, expected_state in cases:
            with self.subTest(signed_at=signed_at):
                auth = self.authority_window()
                envelope = self.make_envelope(auth, signed_at=signed_at)
                result = authority.verify_threshold_envelope(
                    auth,
                    envelope,
                    expected=self.expected(),
                    observed_at="2026-09-28T08:30:00Z",
                    production_use=False,
                )
                self.assertEqual(result["state"], expected_state, result)

    def test_signed_at_after_revocation_is_rejected(self):
        auth = self.authority_window()
        auth["status"] = "REVOKED"
        auth["revokedAt"] = "2026-09-28T08:30:00Z"
        auth["revocationReason"] = "TEST_ONLY_REVOKED"
        self.redigest_authority(auth)
        envelope = self.make_envelope(
            auth, signed_at="2026-09-28T08:30:00Z"
        )
        result = authority.verify_threshold_envelope(
            auth,
            envelope,
            expected=self.expected(),
            observed_at="2026-09-28T08:20:00Z",
            production_use=False,
        )
        self.assertIn(
            "SIGNED_AT_AT_OR_AFTER_AUTHORITY_REVOCATION", result["errors"]
        )

    def test_production_without_durable_replay_backend_holds(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        result = authority.verify_threshold_envelope_json(
            json.dumps(auth),
            json.dumps(envelope),
            expected=self.expected(),
            observed_at=OBSERVED_AT,
            production_use=True,
            artifact_path=authority.EXPECTED_AUTHORITY_ARTIFACT,
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertIn(
            "PRODUCTION_DURABLE_REPLAY_AUTHORITY_REQUIRED", result["errors"]
        )

    def test_changed_timestamp_fresh_signature_is_blocked_by_durable_replay(self):
        auth = self.make_authority()
        original = self.make_envelope(auth)
        replay = TestOnlyReplayBackend()
        replay.remember(original)
        changed = deepcopy(original)
        changed["payload"]["decidedAt"] = "2026-09-28T08:00:01Z"
        changed["attestation"]["signedAt"] = "2026-09-28T08:00:01Z"
        self.finalize_payload(changed)
        self.assertEqual(
            original["payload"]["decisionId"],
            changed["payload"]["decisionId"],
        )
        result = self.verify(auth, changed, replay_backend=replay)
        self.assert_hold(result, "REPLAY_ID_CONTENT_CONFLICT")

    def test_new_decision_for_terminal_accepted_candidate_is_rejected(self):
        auth = self.make_authority()
        accepted = self.make_envelope(auth)
        replay = TestOnlyReplayBackend()
        replay.remember(accepted)
        second = self.make_envelope(auth)
        second["payload"]["decision"] = "HOLD"
        self.finalize_payload(second)
        self.assertNotEqual(
            accepted["payload"]["decisionId"], second["payload"]["decisionId"]
        )
        result = self.verify(auth, second, replay_backend=replay)
        self.assert_hold(result, "TERMINAL_CANDIDATE_ALREADY_ACCEPTED")

    def test_real_cryptographic_wrong_key_is_rejected(self):
        auth = self.make_authority()
        auth["reviewer"]["publicKeyPem"] = self.public_key_b
        auth["reviewer"]["publicKeyFingerprint"] = self.fingerprint_b
        self.redigest_authority(auth)
        envelope = self.make_envelope(auth, private_key=self.private_key)
        self.assert_hold(
            self.verify(auth, envelope), "THRESHOLD_SIGNATURE_INVALID"
        )

    def test_payload_mutated_after_signing_is_rejected_cryptographically(self):
        auth = self.make_authority()
        envelope = self.make_envelope(auth)
        envelope["payload"]["decidedAt"] = "2026-09-28T08:00:01Z"
        envelope["attestation"]["signedAt"] = "2026-09-28T08:00:01Z"
        self.finalize_payload(envelope, resign=False)
        self.assert_hold(
            self.verify(auth, envelope), "THRESHOLD_SIGNATURE_INVALID"
        )

    def test_donecheck_runtime_authority_is_exact(self):
        result = authority.verify_donecheck_runtime_authority()
        self.assertEqual(result["state"], "PASS", result)
        self.assertEqual(result["version"], "1.2.0")
        self.assertEqual(result["exactSha"], authority.DONECHECK_SHA)

    def test_donecheck_runtime_authority_mismatch_holds(self):
        with mock.patch.object(
            authority.donecheck_bridge, "DONECHECK_SHA", "wrong-sha"
        ):
            result = authority.verify_donecheck_runtime_authority()
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("DONECHECK_BRIDGE_SHA_MISMATCH", result["errors"])

    def test_atomic_visibility_is_not_crash_durability(self):
        self.assertTrue(authority.ATOMIC_VISIBILITY_PROVEN)
        self.assertFalse(authority.CRASH_DURABILITY_PROVEN)

    def test_production_use_rejects_test_identity_and_wrong_artifact_path(self):
        auth = self.make_authority()
        result = authority.verify_authority(
            auth,
            observed_at=OBSERVED_AT,
            production_use=True,
            artifact_path=ROOT / "not-canonical.json",
        )
        self.assertIn("AUTHORITY_ARTIFACT_IDENTITY_MISMATCH", result["errors"])
        self.assertIn("TEST_ONLY_AUTHORITY_FORBIDDEN_IN_PRODUCTION", result["errors"])

    def test_production_use_requires_canonical_artifact_to_exist(self):
        auth = self.make_authority()
        result = authority.verify_authority(
            auth,
            observed_at=OBSERVED_AT,
            production_use=True,
            artifact_path=authority.EXPECTED_AUTHORITY_ARTIFACT,
        )
        self.assertIn("AUTHORITY_ARTIFACT_MISSING", result["errors"])

    def test_donecheck_verified_finish_unpublished_staging_protocol(self):
        runtime = authority.DONECHECK_RUNTIME
        transient = (
            Path(tempfile.gettempdir())
            / f"enguru-pre005a-{uuid.uuid4().hex}.test.ts"
        ).resolve()
        runtime_entry = (runtime / "src/donecheck-runtime-node.ts").as_posix()
        source = textwrap.dedent(
            """
            import { generateKeyPairSync } from "node:crypto";
            import { access, mkdir, mkdtemp, open, rename, rm } from "node:fs/promises";
            import { tmpdir } from "node:os";
            import { join } from "node:path";
            import { afterEach, describe, expect, it } from "vitest";
            import {
              JsonlAuditLedger,
              recordVerifiedFinish,
              signHumanReviewAttestation,
            } from "__RUNTIME_ENTRY__";

            const roots: string[] = [];
            afterEach(async () => {
              await Promise.all(roots.splice(0).map((path) => rm(path, { recursive: true, force: true })));
            });

            function fixture() {
              const pair = generateKeyPairSync("ed25519");
              const result = {
                id: "verification-staging-1", taskId: "task-staging-1", outcome: "pass" as const,
                reason: "Machine PASS.", criteria: [{ criterionId: "c1", outcome: "pass" as const,
                reason: "Evidence passed.", evidenceIds: ["e1"] }], verifiedAt: "2026-09-28T08:00:00Z",
              };
              const review = {
                id: "review-staging-1", taskId: result.taskId, verificationResultId: result.id,
                decision: "accepted" as const, reason: "TEST_ONLY acceptance.",
                reviewerId: "TEST_ONLY_REVIEWER", reviewedAt: "2026-09-28T08:01:00Z",
              };
              const privateKeyPem = pair.privateKey.export({ type: "pkcs8", format: "pem" }).toString();
              const publicKeyPem = pair.publicKey.export({ type: "spki", format: "pem" }).toString();
              const attestation = signHumanReviewAttestation(review, {
                reviewerId: review.reviewerId, keyId: "TEST_ONLY_KEY", privateKeyPem,
                signedAt: "2026-09-28T08:01:01Z",
              });
              return { result, review, attestation, authority: {
                reviewerId: review.reviewerId, keyId: "TEST_ONLY_KEY", publicKeyPem,
                allowedDecisions: ["accepted" as const],
              }};
            }

            async function exists(path: string) {
              try { await access(path); return true; } catch { return false; }
            }

            describe("ENGURU unpublished Verified Finish staging proof", () => {
              it("fsyncs receipt, reopens ledger, then atomically publishes the directory", async () => {
                const root = await mkdtemp(join(tmpdir(), "enguru-pre005a-ok-")); roots.push(root);
                const staging = join(root, ".candidate.staging");
                const published = join(root, "candidate");
                await mkdir(staging);
                const ledgerPath = join(staging, "audit.jsonl");
                const ledger = new JsonlAuditLedger(ledgerPath);
                const value = fixture();
                const receipt = await recordVerifiedFinish({
                  verificationResult: value.result, review: value.review,
                  attestation: value.attestation, authority: value.authority,
                  ledger, finishId: "finish-staging-ok",
                });
                const receiptPath = join(staging, "verified-finish-receipt.json");
                const handle = await open(receiptPath, "wx");
                try { await handle.writeFile(JSON.stringify(receipt) + "\\n", "utf8"); await handle.sync(); }
                finally { await handle.close(); }
                const reopened = await new JsonlAuditLedger(ledgerPath).verify();
                expect(reopened.valid).toBe(true);
                if (reopened.valid) expect(reopened.records).toHaveLength(2);
                await rename(staging, published);
                expect(await exists(join(published, "audit.jsonl"))).toBe(true);
                expect(await exists(join(published, "verified-finish-receipt.json"))).toBe(true);
              });

              it("leaves a partial two-append failure unpublished and without a receipt", async () => {
                const root = await mkdtemp(join(tmpdir(), "enguru-pre005a-fail-")); roots.push(root);
                const staging = join(root, ".candidate.staging");
                const published = join(root, "candidate");
                await mkdir(staging);
                const ledgerPath = join(staging, "audit.jsonl");
                const ledger = new JsonlAuditLedger(ledgerPath);
                const realAppend = ledger.append.bind(ledger);
                let count = 0;
                (ledger as any).append = async (event: any) => {
                  count += 1;
                  if (count === 2) throw new Error("TEST_ONLY_SECOND_APPEND_FAILURE");
                  return realAppend(event);
                };
                const value = fixture();
                await expect(recordVerifiedFinish({
                  verificationResult: value.result, review: value.review,
                  attestation: value.attestation, authority: value.authority,
                  ledger, finishId: "finish-staging-fail",
                })).rejects.toThrow("TEST_ONLY_SECOND_APPEND_FAILURE");
                const reopened = await new JsonlAuditLedger(ledgerPath).verify();
                expect(reopened.valid).toBe(true);
                if (reopened.valid) expect(reopened.records).toHaveLength(1);
                expect(await exists(join(staging, "verified-finish-receipt.json"))).toBe(false);
                expect(await exists(published)).toBe(false);
              });

              it("delegates unauthorized DoneCheck decisions to the canonical runtime verifier", async () => {
                const root = await mkdtemp(join(tmpdir(), "enguru-pre005a-auth-")); roots.push(root);
                const value = fixture();
                await expect(recordVerifiedFinish({
                  verificationResult: value.result, review: value.review,
                  attestation: value.attestation,
                  authority: { ...value.authority, allowedDecisions: ["rejected"] },
                  ledger: new JsonlAuditLedger(join(root, "audit.jsonl")),
                  finishId: "finish-staging-unauthorized",
                })).rejects.toThrow("Reviewer is not authorized for this decision");
                expect(await exists(join(root, "audit.jsonl"))).toBe(false);
              });
            });
            """
        ).replace("__RUNTIME_ENTRY__", runtime_entry)
        transient.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(
                [
                    str(runtime / "node_modules/.bin/vitest"),
                    "run",
                    "--root",
                    str(transient.parent),
                    str(transient),
                    "--reporter=dot",
                ],
                cwd=runtime,
                text=True,
                capture_output=True,
                check=False,
                timeout=120,
            )
        finally:
            transient.unlink(missing_ok=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("3 passed", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
