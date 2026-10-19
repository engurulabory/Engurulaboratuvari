#!/usr/bin/env python3
"""G3-A exact build provenance proof candidate. Pure, read-only, no key use.

Manifest claims are untrusted until independently pinned and producer-attested.
A byte match is only build provenance, NEVER secure key issuer qualification.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

HASH = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = {"schema", "sourceSha256", "buildCommandSha256", "unsignedBinarySha256",
            "signedBinarySha256", "signingReceiptSha256", "teamId",
            "bundleId", "profileEligibilityEvidenceSha256"}

def check(manifest_raw: bytes, files: dict[str, bytes],
          *, approved_manifest_sha256: str) -> dict:
    result = {"state": "HOLD", "buildProvenance": "HOLD", "nativeIssuer": "HOLD",
              "authorizedToWrite": False, "signingOperations": 0,
              "keychainOperations": 0, "canonicalWrites": 0}
    try:
        if not HASH.fullmatch(approved_manifest_sha256):
            raise ValueError("EXTERNAL_MANIFEST_PIN_REQUIRED")
        if hashlib.sha256(manifest_raw).hexdigest() != approved_manifest_sha256:
            raise ValueError("MANIFEST_PIN_MISMATCH")
        if len(manifest_raw) > 16384:
            raise ValueError("OVERSIZED_MANIFEST")
        def unique_pairs(pairs):
            out = {}
            for k, v in pairs:
                if k in out:
                    raise ValueError("DUPLICATE_KEY")
                out[k] = v
            return out
        manifest = json.loads(manifest_raw, object_pairs_hook=unique_pairs,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE")))
        if not isinstance(manifest, dict) or set(manifest) != REQUIRED:
            raise ValueError("EXACT_MANIFEST_FIELDS_REQUIRED")
        if manifest["schema"] != "enguru.p02.g3a.exact-build-provenance/v1":
            raise ValueError("WRONG_SCHEMA")
        if not isinstance(manifest["teamId"], str) or not re.fullmatch(r"[A-Z0-9]{10}", manifest["teamId"]):
            raise ValueError("TEAM_ID")
        if not isinstance(manifest["bundleId"], str) or not re.fullmatch(r"[a-zA-Z0-9.-]{5,150}", manifest["bundleId"]):
            raise ValueError("BUNDLE_ID")
        if set(files) != {"source", "buildCommand", "unsignedBinary", "signedBinary",
                          "signingReceipt", "profileEligibilityEvidence"}:
            raise ValueError("EXACT_FILE_SET_REQUIRED")
        for key, payload in files.items():
            if type(payload) is not bytes:
                raise ValueError("INVALID_FILE_" + key)
            digest = manifest[key + "Sha256"]
            if not isinstance(digest, str) or not HASH.fullmatch(digest):
                raise ValueError("BAD_DIGEST_" + key)
            if hashlib.sha256(payload).hexdigest() != digest:
                raise ValueError("FILE_DIGEST_MISMATCH_" + key)
        # Build inputs, unsigned and signed artifact must all be present in the
        # SAME pinned provenance record. Hash matching cannot prove that a
        # stated compiler command actually produced the unsigned artifact.
        result["state"] = "PASS_PINNED_PROVENANCE_BYTES_ONLY"
        result["buildProvenance"] = "HOLD_PRODUCER_ATTESTATION_REQUIRED"
        result["reason"] = "BUILD_EXECUTION_AND_SIGNING_PRODUCER_NOT_INDEPENDENTLY_ATTESTED"
    except (ValueError, TypeError, UnicodeError) as e:
        result["reason"] = str(e)
    return result
