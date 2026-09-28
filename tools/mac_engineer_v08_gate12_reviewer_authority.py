#!/usr/bin/env python3
"""Fail-closed Gate12 reviewer-authority and Human Threshold validation.

This module verifies public authority metadata and signed decision envelopes. It
does not create reviewer identities, keys, signatures, decisions, Gate12 PASS,
Verified Finish authority, or canonical locks.
"""

from __future__ import annotations

import base64
import binascii
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Protocol

try:
    from tools import mac_engineer_donecheck_v12_bridge as donecheck_bridge
except ImportError:  # pragma: no cover - direct script import fallback
    import mac_engineer_donecheck_v12_bridge as donecheck_bridge


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_SCHEMA = (
    ROOT
    / "governance/mac-engineer/V08_GATE12_REVIEWER_AUTHORITY_V1.schema.json"
)
EXPECTED_AUTHORITY_ARTIFACT = (
    ROOT
    / "governance/mac-engineer/V08_GATE12_REVIEWER_AUTHORITY_V1.json"
)
DONECHECK_RUNTIME = donecheck_bridge.DONECHECK_RUNTIME
DONECHECK_CANONICAL_JSON = (
    DONECHECK_RUNTIME / "dist/runtime/node/canonical-json.js"
)
DONECHECK_CANONICAL_JSON_SOURCE = (
    DONECHECK_RUNTIME / "src/runtime/node/canonical-json.ts"
)

AUTHORITY_SCHEMA_ID = (
    "enguru.mac-engineer.v08-gate12-reviewer-authority/v1"
)
THRESHOLD_SCHEMA_ID = (
    "enguru.mac-engineer.v08-gate12-human-threshold-decision/v1"
)
THRESHOLD_ATTESTATION_SCHEMA_ID = (
    "enguru.mac-engineer.v08-gate12-human-threshold-attestation/v1"
)
OBJECTIVE = "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
EXIT = "PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"
DONECHECK_VERSION = donecheck_bridge.DONECHECK_VERSION
DONECHECK_SHA = donecheck_bridge.DONECHECK_SHA
DONECHECK_CANONICAL_SOURCE_SHA256 = (
    "58cddbe0796e1ddc1db7b27b19e52aeb8eace5523f1113cbe1996d66b9ce96ea"
)
DONECHECK_CANONICAL_DIST_SHA256 = (
    "41ea1a41dce68dc7deb8bf6453c40fcbc553a01d07569eba3598ecf53b8ab3ad"
)

# Publication visibility is proven by same-parent atomic rename. Crash-durable
# publication additionally requires directory fsync in the later PRE-005
# publisher and is deliberately not claimed by this framework.
ATOMIC_VISIBILITY_PROVEN = True
CRASH_DURABILITY_PROVEN = False

SHA256 = re.compile(r"^sha256:[a-f0-9]{64}$")
DECISION_ID = re.compile(r"^g12-ht-sha256:[a-f0-9]{64}$")
TERMINAL_CANDIDATE_ID = re.compile(
    r"^g12-candidate-sha256:[a-f0-9]{64}$"
)
RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
PRIVATE_KEY_NAME = re.compile(
    r"(?:private[_-]?key|secret|seed|passphrase|password)",
    re.IGNORECASE,
)
PRIVATE_KEY_MATERIAL = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)

AUTHORITY_KEYS = {
    "schema",
    "authorityVersion",
    "status",
    "validFrom",
    "expiresAt",
    "revokedAt",
    "revocationReason",
    "humanThresholdOwner",
    "reviewer",
    "scope",
    "doneCheckAuthority",
    "humanThresholdAuthority",
    "payloadDigest",
}
REVIEWER_KEYS = {
    "reviewerId",
    "keyId",
    "algorithm",
    "publicKeyPem",
    "publicKeyFingerprint",
}
SCOPE_KEYS = {
    "objective",
    "gate",
    "version",
    "exit",
    "doneCheckHumanReview",
    "gate12HumanThreshold",
}
AUTHORITY_DECISION_KEYS = {"allowedDecisions"}
ENVELOPE_KEYS = {"payload", "payloadDigest", "attestation"}
PAYLOAD_KEYS = {
    "schema",
    "decisionId",
    "authorityDigest",
    "reviewerId",
    "keyId",
    "controlHead",
    "productHead",
    "doneCheckVersion",
    "doneCheckSha",
    "machineResultDigest",
    "evidenceManifestDigest",
    "unresolvedDeferredLedgerDigest",
    "canonicalSnapshotDigest",
    "acceptanceContractDigest",
    "verifiedFinishReceiptDigest",
    "auditHead",
    "targetVersion",
    "intendedExit",
    "decision",
    "decidedAt",
}
ATTESTATION_KEYS = {
    "scheme",
    "reviewerId",
    "keyId",
    "signedAt",
    "signatureBase64",
}
DIGEST_BINDINGS = {
    "machineResultDigest",
    "evidenceManifestDigest",
    "unresolvedDeferredLedgerDigest",
    "canonicalSnapshotDigest",
    "acceptanceContractDigest",
    "verifiedFinishReceiptDigest",
    "auditHead",
}
TERMINAL_CANDIDATE_BINDINGS = (
    "controlHead",
    "productHead",
    "doneCheckVersion",
    "doneCheckSha",
    "machineResultDigest",
    "evidenceManifestDigest",
    "unresolvedDeferredLedgerDigest",
    "canonicalSnapshotDigest",
    "acceptanceContractDigest",
    "verifiedFinishReceiptDigest",
    "auditHead",
    "targetVersion",
    "intendedExit",
)
REPLAY_RECORD_KEYS = {
    "decisionId",
    "terminalCandidateId",
    "payloadDigest",
    "envelopeDigest",
    "decision",
}
_STRICT_INGESTION_TOKEN = object()
SUPPORTED_SCHEMA_KEYWORDS = {
    "$schema",
    "$id",
    "title",
    "description",
    "type",
    "additionalProperties",
    "required",
    "properties",
    "const",
    "enum",
    "format",
    "pattern",
    "minLength",
    "items",
    "minItems",
    "uniqueItems",
    "allOf",
    "if",
    "then",
}


class DurableReplayAuthority(Protocol):
    """Read-only replay authority; persistence belongs to PRE-005 publisher."""

    durable: bool

    def get_decision(self, decision_id: str) -> dict[str, str] | None: ...

    def get_terminal_candidate(
        self, terminal_candidate_id: str
    ) -> dict[str, str] | None: ...


class DuplicateJsonKeyError(ValueError):
    pass


def _strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateJsonKeyError(f"DUPLICATE_JSON_KEY:{key}")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"NON_JSON_NUMBER:{value}")


def strict_json_loads(text: str) -> tuple[Any | None, list[str]]:
    """Parse security JSON while rejecting duplicate keys at every depth."""

    try:
        return json.loads(
            text,
            object_pairs_hook=_strict_object_pairs,
            parse_constant=_reject_json_constant,
        ), []
    except DuplicateJsonKeyError as exc:
        return None, [str(exc)]
    except (TypeError, ValueError, json.JSONDecodeError):
        return None, ["MALFORMED_JSON"]


def _parse_timestamp(
    value: Any,
    label: str,
    errors: list[str],
) -> datetime | None:
    if not isinstance(value, str) or not RFC3339_DATE_TIME.fullmatch(value):
        errors.append(f"{label}_RFC3339_DATE_TIME_REQUIRED")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label}_RFC3339_DATE_TIME_REQUIRED")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{label}_TIMEZONE_REQUIRED")
        return None
    return parsed.astimezone(timezone.utc)


def _json_schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return False


def _json_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    return left == right


def _schema_errors(
    instance: Any,
    schema: dict[str, Any],
    path: str = "$",
) -> list[str]:
    """Evaluate every assertion keyword used by the bounded 2020-12 schema."""

    errors: list[str] = []
    for keyword in sorted(set(schema) - SUPPORTED_SCHEMA_KEYWORDS):
        errors.append(f"SCHEMA_UNSUPPORTED_KEYWORD:{path}:{keyword}")
    expected_type = schema.get("type")
    if expected_type is not None:
        accepted = (
            expected_type if isinstance(expected_type, list) else [expected_type]
        )
        if not any(_json_schema_type_matches(instance, item) for item in accepted):
            return [f"SCHEMA_TYPE:{path}"]

    if "const" in schema and not _json_equal(instance, schema["const"]):
        errors.append(f"SCHEMA_CONST:{path}")
    if "enum" in schema and not any(
        _json_equal(instance, item) for item in schema["enum"]
    ):
        errors.append(f"SCHEMA_ENUM:{path}")

    if isinstance(instance, dict):
        properties = schema.get("properties") or {}
        required = schema.get("required") or []
        for key in required:
            if key not in instance:
                errors.append(f"SCHEMA_REQUIRED:{path}.{key}")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"SCHEMA_ADDITIONAL_PROPERTY:{path}.{key}")
        for key, child_schema in properties.items():
            if key in instance:
                errors.extend(
                    _schema_errors(instance[key], child_schema, f"{path}.{key}")
                )

    if isinstance(instance, list):
        if len(instance) < int(schema.get("minItems", 0)):
            errors.append(f"SCHEMA_MIN_ITEMS:{path}")
        if schema.get("uniqueItems") is True:
            seen: set[str] = set()
            for item in instance:
                identity = json.dumps(
                    item, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                )
                if identity in seen:
                    errors.append(f"SCHEMA_UNIQUE_ITEMS:{path}")
                    break
                seen.add(identity)
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(
                    _schema_errors(item, item_schema, f"{path}[{index}]")
                )

    if isinstance(instance, str):
        if len(instance) < int(schema.get("minLength", 0)):
            errors.append(f"SCHEMA_MIN_LENGTH:{path}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, instance) is None:
            errors.append(f"SCHEMA_PATTERN:{path}")
        if schema.get("format") == "date-time":
            timestamp_errors: list[str] = []
            _parse_timestamp(instance, "SCHEMA_DATE_TIME", timestamp_errors)
            if timestamp_errors:
                errors.append(f"SCHEMA_FORMAT_DATE_TIME:{path}")

    for child in schema.get("allOf") or []:
        errors.extend(_schema_errors(instance, child, path))
    condition = schema.get("if")
    if isinstance(condition, dict) and not _schema_errors(instance, condition, path):
        then_schema = schema.get("then")
        if isinstance(then_schema, dict):
            errors.extend(_schema_errors(instance, then_schema, path))
    return errors


def validate_authority_schema(authority: Any) -> list[str]:
    try:
        text = AUTHORITY_SCHEMA.read_text(encoding="utf-8")
    except OSError:
        return ["AUTHORITY_SCHEMA_REQUIRED"]
    schema, parse_errors = strict_json_loads(text)
    if parse_errors or not isinstance(schema, dict):
        return ["AUTHORITY_SCHEMA_INVALID", *parse_errors]
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        return ["AUTHORITY_SCHEMA_DRAFT_2020_12_REQUIRED"]
    return _schema_errors(authority, schema)


NODE_HELPER = r"""
import { createHash, createPublicKey, verify } from "node:crypto";
import { pathToFileURL } from "node:url";

const runtime = await import(pathToFileURL(process.env.ENGURU_CANONICAL_JSON).href);
const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);
const input = JSON.parse(Buffer.concat(chunks).toString("utf8"));

if (input.operation === "canonical") {
  process.stdout.write(JSON.stringify({ canonical: runtime.canonicalJson(input.value) }));
} else if (input.operation === "inspect-public-key") {
  try {
    const key = createPublicKey(input.publicKeyPem);
    const der = key.export({ type: "spki", format: "der" });
    process.stdout.write(JSON.stringify({
      valid: key.asymmetricKeyType === "ed25519",
      asymmetricKeyType: key.asymmetricKeyType,
      fingerprint: "sha256:" + createHash("sha256").update(der).digest("hex"),
    }));
  } catch (error) {
    process.stdout.write(JSON.stringify({ valid: false, reason: String(error) }));
  }
} else if (input.operation === "verify-threshold") {
  try {
    const key = createPublicKey(input.publicKeyPem);
    const material = runtime.canonicalJson({
      schema: input.attestationSchema,
      signedAt: input.attestation.signedAt,
      payload: input.payload,
    });
    const signature = Buffer.from(input.attestation.signatureBase64, "base64");
    const valid = signature.length > 0 && verify(
      null,
      Buffer.from(material, "utf8"),
      key,
      signature,
    );
    process.stdout.write(JSON.stringify({ valid }));
  } catch (error) {
    process.stdout.write(JSON.stringify({ valid: false, reason: String(error) }));
  }
} else {
  throw new Error("unsupported operation");
}
"""


def _node(payload: dict[str, Any]) -> dict[str, Any]:
    if not DONECHECK_CANONICAL_JSON.is_file():
        raise RuntimeError("DONECHECK_CANONICAL_JSON_RUNTIME_REQUIRED")
    result = subprocess.run(
        ["node", "--input-type=module", "-e", NODE_HELPER],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
        env={
            **os.environ,
            "ENGURU_CANONICAL_JSON": str(DONECHECK_CANONICAL_JSON),
        },
    )
    if result.returncode != 0:
        raise RuntimeError(
            "DONECHECK_NODE_ADAPTER_FAILED:" + result.stderr[-1000:]
        )
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise RuntimeError("DONECHECK_NODE_ADAPTER_OBJECT_REQUIRED")
    return value


def canonical_json(value: Any) -> str:
    """Use DoneCheck's exported canonicalJson implementation."""

    return str(_node({"operation": "canonical", "value": value})["canonical"])


def digest(value: Any) -> str:
    material = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(material).hexdigest()


def _file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verify_donecheck_runtime_authority() -> dict[str, Any]:
    """Read-only reuse of the canonical bridge's fabric/runtime authority."""

    errors: list[str] = []
    if donecheck_bridge.DONECHECK_VERSION != "1.2.0":
        errors.append("DONECHECK_BRIDGE_VERSION_MISMATCH")
    if donecheck_bridge.DONECHECK_SHA != (
        "8b90a8fc93453dd8a84994195d28d14b15e261cb"
    ):
        errors.append("DONECHECK_BRIDGE_SHA_MISMATCH")
    try:
        donecheck_bridge.require_current_fabric()
    except Exception:
        errors.append("DONECHECK_FABRIC_AUTHORITY_REQUIRED")

    mirror = donecheck_bridge.run(
        [
            "git",
            "--git-dir",
            str(donecheck_bridge.DONECHECK_MIRROR),
            "rev-parse",
            "refs/heads/main",
        ],
        timeout=30,
    )
    if mirror.get("code") != 0 or mirror.get("stdout") != DONECHECK_SHA:
        errors.append("DONECHECK_MIRROR_EXACT_SHA_REQUIRED")

    head = donecheck_bridge.run(
        ["git", "rev-parse", "HEAD"], cwd=DONECHECK_RUNTIME, timeout=30
    )
    if head.get("code") != 0 or head.get("stdout") != DONECHECK_SHA:
        errors.append("DONECHECK_RUNTIME_EXACT_SHA_REQUIRED")
    status = donecheck_bridge.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=DONECHECK_RUNTIME,
        timeout=30,
    )
    if status.get("code") != 0 or status.get("stdout"):
        errors.append("DONECHECK_RUNTIME_CLEAN_REQUIRED")

    try:
        package_text = (DONECHECK_RUNTIME / "package.json").read_text(
            encoding="utf-8"
        )
        package, package_errors = strict_json_loads(package_text)
    except OSError:
        package, package_errors = None, ["DONECHECK_PACKAGE_REQUIRED"]
    if package_errors or not isinstance(package, dict):
        errors.extend(package_errors or ["DONECHECK_PACKAGE_OBJECT_REQUIRED"])
    elif package.get("version") != DONECHECK_VERSION:
        errors.append("DONECHECK_RUNTIME_VERSION_REQUIRED")

    expected_files = (
        (DONECHECK_CANONICAL_JSON_SOURCE, DONECHECK_CANONICAL_SOURCE_SHA256),
        (DONECHECK_CANONICAL_JSON, DONECHECK_CANONICAL_DIST_SHA256),
    )
    for path, expected_sha in expected_files:
        try:
            observed_sha = _file_sha256(path)
        except OSError:
            errors.append(f"DONECHECK_RUNTIME_FILE_REQUIRED:{path.name}")
            continue
        if observed_sha != expected_sha:
            errors.append(f"DONECHECK_RUNTIME_FILE_DIGEST_MISMATCH:{path.name}")

    return {
        "state": "PASS" if not errors else "HOLD",
        "errors": errors,
        "version": DONECHECK_VERSION,
        "exactSha": DONECHECK_SHA,
    }


def authority_payload(authority: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(authority)
    payload.pop("payloadDigest", None)
    return payload


def authority_digest(authority: dict[str, Any]) -> str:
    return digest(authority_payload(authority))


def decision_id(payload: dict[str, Any]) -> str:
    material = {
        key: deepcopy(value)
        for key, value in payload.items()
        if key not in {"decisionId", "decidedAt"}
    }
    return "g12-ht-sha256:" + digest(material).removeprefix("sha256:")


def terminal_candidate_id(payload: dict[str, Any]) -> str:
    material = {
        key: deepcopy(payload.get(key)) for key in TERMINAL_CANDIDATE_BINDINGS
    }
    return "g12-candidate-sha256:" + digest(material).removeprefix("sha256:")


def _date(value: Any, label: str, errors: list[str]) -> datetime | None:
    return _parse_timestamp(value, label, errors)


def _closed_object(
    value: Any,
    expected: set[str],
    label: str,
    errors: list[str],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}_OBJECT_REQUIRED")
        return {}
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        errors.append(f"{label}_MISSING_FIELDS:" + ",".join(missing))
    if unknown:
        errors.append(f"{label}_UNKNOWN_FIELDS:" + ",".join(unknown))
    return value


def _private_material_findings(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if PRIVATE_KEY_NAME.search(str(key)):
                findings.append(f"{path}.{key}")
            findings.extend(_private_material_findings(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_private_material_findings(item, f"{path}[{index}]"))
    elif isinstance(value, str) and PRIVATE_KEY_MATERIAL.search(value):
        findings.append(path)
    return findings


def inspect_public_key(public_key_pem: str) -> dict[str, Any]:
    return _node(
        {
            "operation": "inspect-public-key",
            "publicKeyPem": public_key_pem,
        }
    )


def verify_authority(
    authority: Any,
    *,
    observed_at: str,
    production_use: bool,
    artifact_path: Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(authority, dict):
        return {
            "state": "HOLD",
            "errors": ["AUTHORITY_OBJECT_REQUIRED"],
            "authorityDigest": None,
            "reviewerId": None,
            "keyId": None,
            "productionUse": production_use,
        }
    errors.extend(validate_authority_schema(authority))
    root = _closed_object(authority, AUTHORITY_KEYS, "AUTHORITY", errors)
    reviewer = _closed_object(
        root.get("reviewer"), REVIEWER_KEYS, "REVIEWER", errors
    )
    scope = _closed_object(root.get("scope"), SCOPE_KEYS, "SCOPE", errors)
    donecheck = _closed_object(
        root.get("doneCheckAuthority"),
        AUTHORITY_DECISION_KEYS,
        "DONECHECK_AUTHORITY",
        errors,
    )
    threshold = _closed_object(
        root.get("humanThresholdAuthority"),
        AUTHORITY_DECISION_KEYS,
        "HUMAN_THRESHOLD_AUTHORITY",
        errors,
    )

    findings = _private_material_findings(authority)
    if findings:
        errors.append("PRIVATE_KEY_MATERIAL_FORBIDDEN:" + ",".join(findings))

    if root.get("schema") != AUTHORITY_SCHEMA_ID:
        errors.append("AUTHORITY_SCHEMA_MISMATCH")
    if root.get("authorityVersion") != 1:
        errors.append("AUTHORITY_VERSION_MISMATCH")
    if root.get("status") not in {"PENDING_BINDING", "ACTIVE", "REVOKED"}:
        errors.append("AUTHORITY_STATUS_INVALID")
    if production_use and root.get("status") != "ACTIVE":
        errors.append("ACTIVE_AUTHORITY_REQUIRED")
    if production_use:
        runtime_authority = verify_donecheck_runtime_authority()
        if runtime_authority["state"] != "PASS":
            errors.extend(runtime_authority["errors"])
        if artifact_path is None:
            errors.append("AUTHORITY_ARTIFACT_PATH_REQUIRED")
        elif artifact_path.resolve() != EXPECTED_AUTHORITY_ARTIFACT.resolve():
            errors.append("AUTHORITY_ARTIFACT_IDENTITY_MISMATCH")
        elif not artifact_path.is_file():
            errors.append("AUTHORITY_ARTIFACT_MISSING")
        else:
            try:
                persisted_text = artifact_path.read_text(encoding="utf-8")
            except OSError:
                errors.append("AUTHORITY_ARTIFACT_UNREADABLE")
            else:
                persisted, persisted_errors = strict_json_loads(persisted_text)
                if persisted_errors:
                    errors.extend(
                        f"AUTHORITY_ARTIFACT_{item}"
                        for item in persisted_errors
                    )
                elif persisted != authority:
                    errors.append("AUTHORITY_ARTIFACT_CONTENT_MISMATCH")
        if any(
            "TEST_ONLY" in str(value)
            for value in (
                reviewer.get("reviewerId"),
                reviewer.get("keyId"),
                root.get("humanThresholdOwner"),
            )
        ):
            errors.append("TEST_ONLY_AUTHORITY_FORBIDDEN_IN_PRODUCTION")

    if not isinstance(root.get("humanThresholdOwner"), str) or not str(
        root.get("humanThresholdOwner") or ""
    ).strip():
        errors.append("HUMAN_THRESHOLD_OWNER_REQUIRED")
    for key in ("reviewerId", "keyId", "publicKeyPem"):
        if not isinstance(reviewer.get(key), str) or not reviewer.get(key):
            errors.append(f"REVIEWER_{key.upper()}_REQUIRED")
    if reviewer.get("algorithm") != "ed25519":
        errors.append("ED25519_ALGORITHM_REQUIRED")
    if scope != {}:
        expected_scope = {
            "objective": OBJECTIVE,
            "gate": 12,
            "version": "v0.8",
            "exit": EXIT,
        }
        for key, expected in expected_scope.items():
            if scope.get(key) != expected:
                errors.append(f"SCOPE_{key.upper()}_MISMATCH")
        if scope.get("doneCheckHumanReview") is not True:
            errors.append("DONECHECK_HUMAN_REVIEW_SCOPE_REQUIRED")
        if scope.get("gate12HumanThreshold") is not True:
            errors.append("GATE12_HUMAN_THRESHOLD_SCOPE_REQUIRED")

    donecheck_allowed = donecheck.get("allowedDecisions")
    if (
        not isinstance(donecheck_allowed, list)
        or not donecheck_allowed
        or any(not isinstance(item, str) for item in donecheck_allowed)
        or len(donecheck_allowed) != len(set(donecheck_allowed))
        or any(
            item not in {"accepted", "revise", "rejected"}
            for item in donecheck_allowed
        )
    ):
        errors.append("DONECHECK_ALLOWED_DECISIONS_INVALID")
    threshold_allowed = threshold.get("allowedDecisions")
    if (
        not isinstance(threshold_allowed, list)
        or not threshold_allowed
        or any(not isinstance(item, str) for item in threshold_allowed)
        or len(threshold_allowed) != len(set(threshold_allowed))
        or any(item not in {"ACCEPT", "HOLD"} for item in threshold_allowed)
    ):
        errors.append("HUMAN_THRESHOLD_ALLOWED_DECISIONS_INVALID")

    observed = _date(observed_at, "OBSERVED_AT", errors)
    valid_from = _date(root.get("validFrom"), "VALID_FROM", errors)
    expires = None
    if root.get("expiresAt") is not None:
        expires = _date(root.get("expiresAt"), "EXPIRES_AT", errors)
    revoked = None
    if root.get("revokedAt") is not None:
        revoked = _date(root.get("revokedAt"), "REVOKED_AT", errors)
    if root.get("status") == "REVOKED" or revoked is not None:
        errors.append("AUTHORITY_REVOKED")
    if root.get("status") in {"PENDING_BINDING", "ACTIVE"} and root.get(
        "revocationReason"
    ) is not None:
        errors.append("NON_REVOKED_AUTHORITY_REASON_MUST_BE_NULL")
    if root.get("status") == "REVOKED" and not root.get("revocationReason"):
        errors.append("REVOKED_AUTHORITY_REASON_REQUIRED")
    if valid_from and expires and expires <= valid_from:
        errors.append("AUTHORITY_VALIDITY_INTERVAL_EMPTY_OR_REVERSED")
    if valid_from and revoked and revoked < valid_from:
        errors.append("AUTHORITY_REVOCATION_BEFORE_VALIDITY")
    if observed and valid_from and observed < valid_from:
        errors.append("AUTHORITY_NOT_YET_VALID")
    if observed and expires and observed >= expires:
        errors.append("AUTHORITY_EXPIRED")

    public_key = str(reviewer.get("publicKeyPem") or "")
    if public_key:
        key_result = inspect_public_key(public_key)
        if key_result.get("valid") is not True:
            errors.append("ED25519_PUBLIC_KEY_INVALID")
        elif reviewer.get("publicKeyFingerprint") != key_result.get(
            "fingerprint"
        ):
            errors.append("PUBLIC_KEY_FINGERPRINT_MISMATCH")
    fingerprint = reviewer.get("publicKeyFingerprint")
    if not isinstance(fingerprint, str) or not SHA256.fullmatch(fingerprint):
        errors.append("PUBLIC_KEY_FINGERPRINT_FORMAT_INVALID")

    computed_digest = authority_digest(authority)
    if root.get("payloadDigest") != computed_digest:
        errors.append("AUTHORITY_PAYLOAD_DIGEST_MISMATCH")

    return {
        "state": "PASS" if not errors else "HOLD",
        "errors": errors,
        "authorityDigest": computed_digest,
        "reviewerId": reviewer.get("reviewerId"),
        "keyId": reviewer.get("keyId"),
        "productionUse": production_use,
    }


def _verify_threshold_signature(
    payload: dict[str, Any],
    attestation: dict[str, Any],
    public_key_pem: str,
) -> bool:
    result = _node(
        {
            "operation": "verify-threshold",
            "attestationSchema": THRESHOLD_ATTESTATION_SCHEMA_ID,
            "payload": payload,
            "attestation": attestation,
            "publicKeyPem": public_key_pem,
        }
    )
    return result.get("valid") is True


def _replay_record(
    value: Any,
    label: str,
    errors: list[str],
) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != REPLAY_RECORD_KEYS:
        errors.append(f"{label}_RECORD_INVALID")
        return None
    if not all(isinstance(item, str) and item for item in value.values()):
        errors.append(f"{label}_RECORD_INVALID")
        return None
    if not DECISION_ID.fullmatch(value["decisionId"]):
        errors.append(f"{label}_DECISION_ID_INVALID")
    if not TERMINAL_CANDIDATE_ID.fullmatch(value["terminalCandidateId"]):
        errors.append(f"{label}_CANDIDATE_ID_INVALID")
    for key in ("payloadDigest", "envelopeDigest"):
        if not SHA256.fullmatch(value[key]):
            errors.append(f"{label}_{key.upper()}_INVALID")
    if value["decision"] not in {"ACCEPT", "HOLD"}:
        errors.append(f"{label}_DECISION_INVALID")
    return value


def verify_threshold_envelope(
    authority: Any,
    envelope: Any,
    *,
    expected: dict[str, Any],
    observed_at: str,
    production_use: bool,
    artifact_path: Path | None = None,
    replay_backend: DurableReplayAuthority | None = None,
    _strict_ingestion_token: object | None = None,
) -> dict[str, Any]:
    authority_result = verify_authority(
        authority,
        observed_at=observed_at,
        production_use=production_use,
        artifact_path=artifact_path,
    )
    errors = list(authority_result["errors"])
    if production_use and _strict_ingestion_token is not _STRICT_INGESTION_TOKEN:
        errors.append("PRODUCTION_STRICT_JSON_INGESTION_REQUIRED")
    if not isinstance(envelope, dict):
        return {
            "state": "HOLD",
            "errors": [*errors, "ENVELOPE_OBJECT_REQUIRED"],
            "decisionId": None,
            "terminalCandidateId": None,
            "payloadDigest": None,
            "envelopeDigest": None,
            "authorityDigest": authority_result["authorityDigest"],
            "productionUse": production_use,
            "createsDecision": False,
            "replayDisposition": "REJECTED",
        }
    root = _closed_object(envelope, ENVELOPE_KEYS, "ENVELOPE", errors)
    payload = _closed_object(root.get("payload"), PAYLOAD_KEYS, "PAYLOAD", errors)
    attestation = _closed_object(
        root.get("attestation"), ATTESTATION_KEYS, "ATTESTATION", errors
    )

    if _private_material_findings(envelope):
        errors.append("PRIVATE_KEY_MATERIAL_FORBIDDEN_IN_ENVELOPE")
    if payload.get("schema") != THRESHOLD_SCHEMA_ID:
        errors.append("THRESHOLD_SCHEMA_MISMATCH")
    if payload.get("authorityDigest") != authority_result["authorityDigest"]:
        errors.append("STALE_AUTHORITY_DIGEST")
    reviewer_value = authority.get("reviewer") if isinstance(authority, dict) else None
    reviewer = reviewer_value if isinstance(reviewer_value, dict) else {}
    if payload.get("reviewerId") != reviewer.get("reviewerId"):
        errors.append("UNKNOWN_REVIEWER")
    if payload.get("keyId") != reviewer.get("keyId"):
        errors.append("WRONG_KEY_ID")

    fixed = {
        "controlHead": expected.get("controlHead"),
        "productHead": expected.get("productHead"),
        "doneCheckVersion": DONECHECK_VERSION,
        "doneCheckSha": DONECHECK_SHA,
        "targetVersion": "v0.8",
        "intendedExit": EXIT,
    }
    for key, value in fixed.items():
        if payload.get(key) != value:
            errors.append(f"{key.upper()}_MISMATCH")
    for key in DIGEST_BINDINGS:
        value = payload.get(key)
        if not isinstance(value, str) or not SHA256.fullmatch(value):
            errors.append(f"{key.upper()}_FORMAT_INVALID")
        if value != expected.get(key):
            errors.append(f"{key.upper()}_MISMATCH")

    decision = payload.get("decision")
    threshold_value = (
        authority.get("humanThresholdAuthority")
        if isinstance(authority, dict)
        else None
    )
    threshold_allowed = (
        threshold_value.get("allowedDecisions") or []
        if isinstance(threshold_value, dict)
        else []
    )
    if (
        not isinstance(decision, str)
        or decision not in {"ACCEPT", "HOLD"}
        or decision not in threshold_allowed
    ):
        errors.append("UNAUTHORIZED_HUMAN_THRESHOLD_DECISION")

    decided_at = _date(payload.get("decidedAt"), "DECIDED_AT", errors)
    signed_at = _date(attestation.get("signedAt"), "SIGNED_AT", errors)
    if payload.get("decidedAt") != attestation.get("signedAt"):
        errors.append("ATTESTATION_TIME_MISMATCH")
    authority_valid_from = None
    authority_expires = None
    authority_revoked = None
    if isinstance(authority, dict):
        authority_valid_from = _date(
            authority.get("validFrom"), "AUTHORITY_VALID_FROM", errors
        )
        if authority.get("expiresAt") is not None:
            authority_expires = _date(
                authority.get("expiresAt"), "AUTHORITY_EXPIRES_AT", errors
            )
        if authority.get("revokedAt") is not None:
            authority_revoked = _date(
                authority.get("revokedAt"), "AUTHORITY_REVOKED_AT", errors
            )
    if signed_at and authority_valid_from and signed_at < authority_valid_from:
        errors.append("SIGNED_AT_BEFORE_AUTHORITY_VALID_FROM")
    if signed_at and authority_expires and signed_at >= authority_expires:
        errors.append("SIGNED_AT_AT_OR_AFTER_AUTHORITY_EXPIRY")
    if signed_at and authority_revoked and signed_at >= authority_revoked:
        errors.append("SIGNED_AT_AT_OR_AFTER_AUTHORITY_REVOCATION")
    if attestation.get("scheme") != "ed25519":
        errors.append("ATTESTATION_SCHEME_MISMATCH")
    if attestation.get("reviewerId") != payload.get("reviewerId"):
        errors.append("ATTESTATION_REVIEWER_MISMATCH")
    if attestation.get("keyId") != payload.get("keyId"):
        errors.append("ATTESTATION_KEY_MISMATCH")
    signature = attestation.get("signatureBase64")
    if not isinstance(signature, str) or not signature:
        errors.append("ATTESTATION_SIGNATURE_REQUIRED")
    else:
        try:
            if not base64.b64decode(signature, validate=True):
                errors.append("ATTESTATION_SIGNATURE_INVALID")
        except (ValueError, binascii.Error):
            errors.append("ATTESTATION_SIGNATURE_INVALID")

    computed_payload_digest = digest(payload)
    if root.get("payloadDigest") != computed_payload_digest:
        errors.append("THRESHOLD_PAYLOAD_DIGEST_MISMATCH")
    computed_decision_id = decision_id(payload)
    computed_candidate_id = terminal_candidate_id(payload)
    computed_envelope_digest = digest(envelope)
    if payload.get("decisionId") != computed_decision_id:
        errors.append("DETERMINISTIC_DECISION_ID_MISMATCH")
    if not isinstance(payload.get("decisionId"), str) or not DECISION_ID.fullmatch(
        str(payload.get("decisionId") or "")
    ):
        errors.append("DECISION_ID_FORMAT_INVALID")

    replay_disposition = "NEW"
    if production_use and replay_backend is None:
        errors.append("PRODUCTION_DURABLE_REPLAY_AUTHORITY_REQUIRED")
        replay_disposition = "REJECTED"
    elif replay_backend is not None:
        if production_use and getattr(replay_backend, "durable", False) is not True:
            errors.append("PRODUCTION_DURABLE_REPLAY_AUTHORITY_REQUIRED")
            replay_disposition = "REJECTED"
        decision_lookup = getattr(replay_backend, "get_decision", None)
        candidate_lookup = getattr(
            replay_backend, "get_terminal_candidate", None
        )
        if not callable(decision_lookup) or not callable(candidate_lookup):
            errors.append("REPLAY_AUTHORITY_INTERFACE_INVALID")
            replay_disposition = "REJECTED"
        else:
            try:
                prior_decision = _replay_record(
                    decision_lookup(computed_decision_id),
                    "REPLAY_DECISION",
                    errors,
                )
                prior_candidate = _replay_record(
                    candidate_lookup(computed_candidate_id),
                    "REPLAY_CANDIDATE",
                    errors,
                )
            except Exception:
                errors.append("REPLAY_AUTHORITY_LOOKUP_FAILED")
                replay_disposition = "REJECTED"
            else:
                if prior_decision is not None:
                    exact = (
                        prior_decision["terminalCandidateId"]
                        == computed_candidate_id
                        and prior_decision["payloadDigest"]
                        == computed_payload_digest
                        and prior_decision["envelopeDigest"]
                        == computed_envelope_digest
                        and prior_decision["decision"] == decision
                    )
                    if exact:
                        replay_disposition = "IDEMPOTENT"
                    else:
                        errors.append("REPLAY_ID_CONTENT_CONFLICT")
                        replay_disposition = "REJECTED"
                if (
                    prior_candidate is not None
                    and prior_candidate["decision"] == "ACCEPT"
                ):
                    exact_candidate = (
                        prior_candidate["decisionId"] == computed_decision_id
                        and prior_candidate["payloadDigest"]
                        == computed_payload_digest
                        and prior_candidate["envelopeDigest"]
                        == computed_envelope_digest
                    )
                    if exact_candidate:
                        replay_disposition = "IDEMPOTENT"
                    else:
                        errors.append("TERMINAL_CANDIDATE_ALREADY_ACCEPTED")
                        replay_disposition = "REJECTED"

    if not errors and not _verify_threshold_signature(
        payload,
        attestation,
        str(reviewer.get("publicKeyPem") or ""),
    ):
        errors.append("THRESHOLD_SIGNATURE_INVALID")

    return {
        "state": "PASS" if not errors else "HOLD",
        "errors": errors,
        "decisionId": computed_decision_id,
        "terminalCandidateId": computed_candidate_id,
        "payloadDigest": computed_payload_digest,
        "envelopeDigest": computed_envelope_digest,
        "authorityDigest": authority_result["authorityDigest"],
        "productionUse": production_use,
        "createsDecision": False,
        "replayDisposition": replay_disposition,
    }


def verify_authority_json(
    text: str,
    *,
    observed_at: str,
    production_use: bool,
    artifact_path: Path | None = None,
) -> dict[str, Any]:
    value, parse_errors = strict_json_loads(text)
    if parse_errors:
        return {
            "state": "HOLD",
            "errors": parse_errors,
            "authorityDigest": None,
            "reviewerId": None,
            "keyId": None,
            "productionUse": production_use,
        }
    return verify_authority(
        value,
        observed_at=observed_at,
        production_use=production_use,
        artifact_path=artifact_path,
    )


def verify_threshold_envelope_json(
    authority_text: str,
    envelope_text: str,
    *,
    expected: dict[str, Any],
    observed_at: str,
    production_use: bool,
    artifact_path: Path | None = None,
    replay_backend: DurableReplayAuthority | None = None,
) -> dict[str, Any]:
    authority_value, authority_errors = strict_json_loads(authority_text)
    envelope_value, envelope_errors = strict_json_loads(envelope_text)
    parse_errors = [
        *(f"AUTHORITY_{item}" for item in authority_errors),
        *(f"ENVELOPE_{item}" for item in envelope_errors),
    ]
    if parse_errors:
        return {
            "state": "HOLD",
            "errors": parse_errors,
            "decisionId": None,
            "terminalCandidateId": None,
            "payloadDigest": None,
            "envelopeDigest": None,
            "authorityDigest": None,
            "productionUse": production_use,
            "createsDecision": False,
            "replayDisposition": "REJECTED",
        }
    return verify_threshold_envelope(
        authority_value,
        envelope_value,
        expected=expected,
        observed_at=observed_at,
        production_use=production_use,
        artifact_path=artifact_path,
        replay_backend=replay_backend,
        _strict_ingestion_token=_STRICT_INGESTION_TOKEN,
    )


def load_authority(path: Path = EXPECTED_AUTHORITY_ARTIFACT) -> dict[str, Any]:
    value, errors = strict_json_loads(path.read_text(encoding="utf-8"))
    if errors:
        raise RuntimeError(";".join(errors))
    if not isinstance(value, dict):
        raise RuntimeError("AUTHORITY_OBJECT_REQUIRED")
    return value


__all__ = [
    "AUTHORITY_SCHEMA",
    "EXPECTED_AUTHORITY_ARTIFACT",
    "DONECHECK_RUNTIME",
    "AUTHORITY_SCHEMA_ID",
    "THRESHOLD_SCHEMA_ID",
    "THRESHOLD_ATTESTATION_SCHEMA_ID",
    "OBJECTIVE",
    "EXIT",
    "DONECHECK_VERSION",
    "DONECHECK_SHA",
    "ATOMIC_VISIBILITY_PROVEN",
    "CRASH_DURABILITY_PROVEN",
    "canonical_json",
    "digest",
    "authority_digest",
    "decision_id",
    "terminal_candidate_id",
    "inspect_public_key",
    "strict_json_loads",
    "validate_authority_schema",
    "verify_donecheck_runtime_authority",
    "verify_authority",
    "verify_authority_json",
    "verify_threshold_envelope",
    "verify_threshold_envelope_json",
    "load_authority",
]
