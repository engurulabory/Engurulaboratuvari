"""Read-only pilot proof gates. This module cannot issue owner acceptance."""
import hashlib
import hmac
from pathlib import Path

HOLD = "HOLD_GUVENLI_DUR"
def verify_source(root, relative_path, expected_sha256):
    root = Path(root).resolve(strict=True)
    if not isinstance(relative_path,str) or not relative_path or Path(relative_path).is_absolute() or ".." in Path(relative_path).parts:
        return {"state":HOLD,"reason":"PATH_SCOPE"}
    if not isinstance(expected_sha256,str) or len(expected_sha256)!=64 or any(x not in "0123456789abcdef" for x in expected_sha256):
        return {"state":HOLD,"reason":"INVALID_SHA_PIN"}
    target = root / relative_path
    if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root):
        return {"state":HOLD,"reason":"SOURCE_SCOPE"}
    data = target.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    if not hmac.compare_digest(digest,expected_sha256):
        return {"state":HOLD,"reason":"SOURCE_SHA_DRIFT","observed_sha256":digest}
    return {"state":"PASS_SOURCE_SHA256","source_sha256":digest}

def owner_gate(source_result, owner_claim, canonical_authority_verified=False, signature_verified=False, signer_scope_verified=False, human_threshold_verified=False):
    if source_result.get("state")!="PASS_SOURCE_SHA256":
        return {"state":HOLD,"reason":"SOURCE_EVIDENCE_REQUIRED"}
    if owner_claim!="engurulabory":
        return {"state":HOLD,"reason":"OWNER_SCOPE"}
    if not all((canonical_authority_verified,signature_verified,signer_scope_verified,human_threshold_verified)):
        return {"state":HOLD,"reason":"AUTHENTIC_OWNER_AUTHORITY_REQUIRED"}
    # Even booleans from callers do not constitute a cryptographic verification.
    return {"state":HOLD,"reason":"CANONICAL_VERIFIER_RECEIPT_REQUIRED"}
