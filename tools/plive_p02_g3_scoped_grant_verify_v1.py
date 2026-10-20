#!/usr/bin/env python3
"""P02 G3-B offline verifier candidate. No issuance, key access, or canonical writes."""
from __future__ import annotations
import base64
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timezone

POLICY_SHA256 = "48f46754c4a94e28d66e7e6a272284afae60791d631f556d6826f6775744fb9e"
PROJECT = "ENGURU_PLIVE_P02_USER_SCREEN"
ITEM = "P02.S01.01"
ACTION = "P02_ITEM_PASS"
FIELDS = frozenset({"schema", "projectId", "itemId", "action", "head",
                    "preimageSha256", "evidenceSha256", "approvalSha256",
                    "issuerId", "keyId", "nonce", "issuedAt", "expiresAt",
                    "policySha256"})
SHA = re.compile(r"[0-9a-f]{64}\Z")
HEX_NONCE = re.compile(r"[0-9a-f]{32,128}\Z")
HEAD = re.compile(r"[0-9a-f]{40}\Z")


def canonical(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def exact_json(raw: bytes) -> dict:
    def pairs(items):
        obj = {}
        for k, v in items:
            if k in obj:
                raise ValueError("DUPLICATE_KEY")
            obj[k] = v
        return obj
    def reject_constant(_):
        raise ValueError("NONFINITE_NUMBER")
    value = json.loads(raw, object_pairs_hook=pairs,
                       parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValueError("OBJECT_REQUIRED")
    if raw != canonical(value):
        raise ValueError('NONCANONICAL_GRANT_BYTES')
    return value



def load_pinned_trust_record(raw: bytes, *, approved_sha256: str) -> dict:
    """Load only a pre-pinned public trust record. Pin approval is an EXTERNAL human step.

    Does not authenticate the person/device who supplied approved_sha256,
    check live revocation, establish issuer custody, or authorize production.
    """
    if not isinstance(approved_sha256, str) or not SHA.fullmatch(approved_sha256):
        raise ValueError("APPROVED_TRUST_PIN_REQUIRED")
    if hashlib.sha256(raw).hexdigest() != approved_sha256:
        raise ValueError("TRUST_SOURCE_PIN_MISMATCH")
    trust = exact_json(raw)
    required = {"schema", "issuerId", "keyId", "policySha256",
                "publicKeyX963Hex", "publicKeySha256", "status",
                "revocationChecked"}
    if set(trust) != required:
        raise ValueError("TRUST_FIELDS")
    if trust["schema"] != "enguru.plive.p02.pinned-public-trust-candidate/v1":
        raise ValueError("TRUST_SCHEMA")
    if trust["policySha256"] != POLICY_SHA256:
        raise ValueError("TRUST_POLICY_MISMATCH")
    if trust["status"] != "ACTIVE" or trust["revocationChecked"] is not True:
        raise ValueError("TRUST_STATUS_OR_REVOCATION")
    pub = trust["publicKeyX963Hex"]
    if not isinstance(pub, str) or not re.fullmatch(r"04[0-9a-f]{128}", pub):
        raise ValueError("TRUST_PUBLIC_KEY_FORMAT")
    if hashlib.sha256(bytes.fromhex(pub)).hexdigest() != trust["publicKeySha256"]:
        raise ValueError("TRUST_KEY_FINGERPRINT")
    return trust


def inspect(grant: dict, *, trusted: dict, expected: dict, observed_at: str,
            consumed_nonces: frozenset[str]) -> list[str]:
    """Schema/policy checks; does NOT attest custody, user presence or revocation."""
    errors = []
    if set(grant) != FIELDS:
        errors.append("GRANT_FIELDS")
        return errors
    for key, value in grant.items():
        if not isinstance(value, str) or not value:
            errors.append("BAD_STRING_" + key)
    if errors:
        return errors
    fixed = {"schema": "enguru.plive.p02.scoped-grant/v1",
             "projectId": PROJECT, "itemId": ITEM, "action": ACTION,
             "policySha256": POLICY_SHA256}
    for k, v in fixed.items():
        if grant[k] != v:
            errors.append("WRONG_" + k)
    for k in ("head", "preimageSha256", "evidenceSha256", "approvalSha256"):
        val = grant[k]
        if not (HEAD.fullmatch(val) if k == "head" else SHA.fullmatch(val)):
            errors.append("FORMAT_" + k)
        if val != expected.get(k):
            errors.append("MISMATCH_" + k)
    if not HEX_NONCE.fullmatch(grant["nonce"]):
        errors.append("NONCE_FORMAT")
    if grant["nonce"] in consumed_nonces:
        errors.append("NONCE_REPLAY")
    if grant["issuerId"] != trusted.get("issuerId") or grant["keyId"] != trusted.get("keyId"):
        errors.append("UNTRUSTED_ISSUER")
    if trusted.get("policySha256") != POLICY_SHA256:
        errors.append("UNTRUSTED_POLICY")
    if trusted.get("status") != "ACTIVE" or trusted.get("revocationChecked") is not True:
        errors.append("TRUST_NOT_ACTIVE_OR_REVOCATION_UNCHECKED")
    def utc(value):
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
            raise ValueError("TIME_FORMAT")
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
            raise ValueError("TIME_NONCANONICAL")
        return parsed
    try:
        issued, expires, now = map(utc, (grant["issuedAt"], grant["expiresAt"], observed_at))
    except ValueError:
        errors.append("TIME_INVALID")
        return errors
    if not issued <= now < expires:
        errors.append("EXPIRED_OR_NOT_YET_VALID")
    return errors


def verify(grant_raw: bytes, signature_b64: str, *, trusted: dict,
           expected: dict, observed_at: str, consumed_nonces: frozenset[str]) -> dict:
    """Evidence-only cryptographic check. Never grants authority to write."""
    try:
        grant = exact_json(grant_raw)
        errors = inspect(grant, trusted=trusted, expected=expected,
                         observed_at=observed_at, consumed_nonces=consumed_nonces)
        if errors:
            return {"state": "HOLD", "errors": errors, "authorizedToWrite": False}
        pub = trusted.get("publicKeyX963Hex")
        if not isinstance(pub, str) or not re.fullmatch(r"04[0-9a-f]{128}", pub):
            raise ValueError("PUBLIC_KEY_FORMAT")
        key = bytes.fromhex(pub)
        fingerprint = hashlib.sha256(key).hexdigest()
        if fingerprint != trusted.get("publicKeySha256"):
            raise ValueError("TRUST_KEY_FINGERPRINT")
        signature = base64.b64decode(signature_b64, validate=True)
        if not signature or len(signature) > 144:
            raise ValueError("SIGNATURE_FORMAT")
        spki = bytes.fromhex("3059301306072a8648ce3d020106082a8648ce3d030107034200") + key
        with tempfile.TemporaryDirectory(prefix="p02-g3-verify-") as d:
            root = Path(d)
            (root/"pub.der").write_bytes(spki)
            (root/"sig.der").write_bytes(signature)
            (root/"payload.bin").write_bytes(canonical(grant))
            proc = subprocess.run(
                ["openssl", "dgst", "-sha256", "-verify", str(root/"pub.der"),
                 "-keyform", "DER", "-signature", str(root/"sig.der"), str(root/"payload.bin")],
                capture_output=True, timeout=12, check=False)
        if proc.returncode != 0 or proc.stdout.strip() != b"Verified OK":
            raise ValueError("SIGNATURE_INVALID")
        return {"state": "CRYPTO_AND_SCOPE_VALID_ONLY",
                "errors": [], "authorizedToWrite": False,
                "grantSha256": hashlib.sha256(canonical(grant)).hexdigest()}
    except (ValueError, TypeError, json.JSONDecodeError, subprocess.TimeoutExpired,
            OSError) as exc:
        return {"state": "HOLD", "errors": [str(exc)[:120]], "authorizedToWrite": False}


def verify_with_pinned_trust(grant_raw: bytes, signature_b64: str, *,
                             trust_record_raw: bytes, approved_trust_sha256: str,
                             expected: dict, observed_at: str,
                             consumed_nonces: frozenset[str]) -> dict:
    """Evidence-only entry point; trust pin MUST originate outside caller control.

    This function validates a preapproved byte pin but cannot authenticate its
    approval origin, prove signer custody, or reserve a nonce across crashes.
    A valid result is never permission to update P02 canonical state.
    """
    try:
        trust = load_pinned_trust_record(
            trust_record_raw, approved_sha256=approved_trust_sha256
        )
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"state": "HOLD",
                "errors": ["PINNED_TRUST_REJECTED:" + str(exc)[:100]],
                "authorizedToWrite": False}
    return verify(grant_raw, signature_b64, trusted=trust,
                  expected=expected, observed_at=observed_at,
                  consumed_nonces=consumed_nonces)

# Canonical source binding is a guard on evidence input, not native writer authority.
P02_STATE_PATH = "governance/plive-p02-user-screen/STATE_V1.json"
P02_WORKLIST_PATH = "governance/plive-p02-user-screen/WORKLIST_V1.json"

def inspect_p02_canonical_source_binding(*, contract_raw: bytes, state_raw: bytes,
                                         worklist_raw: bytes,
                                         approved_source_sha256: dict) -> dict:
    """Validate exact source bytes and P02 identity before preparing grant evidence.

    All three pins must come from the independently approved Mac source snapshot,
    not from the grant submitter. The binding does not attest Mac currentness,
    ownership, human approval, preimage interpretation, or writer authority.
    """
    source = {"contract": contract_raw, "state": state_raw, "worklist": worklist_raw}
    result = {"state": "HOLD", "authorizedToWrite": False, "sourceSha256": {}}
    try:
        if type(approved_source_sha256) is not dict or set(approved_source_sha256) != set(source):
            raise ValueError("EXACT_APPROVED_SOURCE_PINS_REQUIRED")
        for name, raw in source.items():
            if type(raw) is not bytes or len(raw) > 1024 * 1024:
                raise ValueError("INVALID_SOURCE_" + name)
            pin = approved_source_sha256[name]
            if type(pin) is not str or not SHA.fullmatch(pin):
                raise ValueError("INVALID_SOURCE_PIN_" + name)
            digest = hashlib.sha256(raw).hexdigest()
            if digest != pin:
                raise ValueError("SOURCE_PIN_MISMATCH_" + name)
            result["sourceSha256"][name] = digest

        contract = json.loads(contract_raw, object_pairs_hook=_reject_duplicate_pairs)
        state = json.loads(state_raw, object_pairs_hook=_reject_duplicate_pairs)
        worklist = json.loads(worklist_raw, object_pairs_hook=_reject_duplicate_pairs)
        binding = contract["progressBinding"]
        if (contract.get("schema") != "enguru.work-contract/v1"
                or contract.get("projectId", contract.get("workId")) != PROJECT
                or contract.get("workId") != PROJECT
                or binding.get("projectId") != PROJECT
                or binding.get("state") != P02_STATE_PATH
                or binding.get("worklist") != P02_WORKLIST_PATH):
            raise ValueError("WORK_CONTRACT_BINDING_MISMATCH")
        if (state.get("schema") != "enguru.plive.p02.state/v1"
                or state.get("projectId") != PROJECT
                or state.get("activeItem") != ITEM
                or state.get("packages", {}).get("P02.S01", {}).get("items", {}).get(ITEM, {}).get("state") != "ACTIVE"):
            raise ValueError("P02_STATE_NOT_EXPECTED_ACTIVE_ITEM")
        if (worklist.get("schema") != "enguru.plive.p02.worklist/v1"
                or worklist.get("projectId") != PROJECT
                or type(worklist.get("packages")) is not list
                or len(worklist["packages"]) != 4
                or [item for p in worklist["packages"] for item in p["items"]].count(ITEM) != 1
                or sum(len(p["items"]) for p in worklist["packages"]) != 12):
            raise ValueError("P02_WORKLIST_SCOPE_MISMATCH")
        result["state"] = "PASS_SOURCE_BINDING_ONLY"
    except (ValueError, TypeError, KeyError, AttributeError, json.JSONDecodeError) as exc:
        result["error"] = str(exc)[:128]
    return result


def _reject_duplicate_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_SOURCE_KEY")
        out[key] = value
    return out

