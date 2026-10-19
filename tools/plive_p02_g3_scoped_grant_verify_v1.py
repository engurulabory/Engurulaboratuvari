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
    return value


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
    # UTC timestamp lexicographic comparison is safe only with exact canonical format.
    timestamp = re.compile(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]T[0-2][0-9]:[0-5][0-9]:[0-5][0-9]Z\Z")
    for value in (grant["issuedAt"], grant["expiresAt"], observed_at):
        if not timestamp.fullmatch(value):
            errors.append("TIME_FORMAT")
            return errors
    if not grant["issuedAt"] <= observed_at < grant["expiresAt"]:
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
