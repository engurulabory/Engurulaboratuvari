"""A07 G03: fail-closed temporal evidence intake over the 18 V19 cases.

Published historical testimonials are NOT a cryptographic source authority.
Even syntactically valid pins are only review candidates until externally signed.
"""
import re
from datetime import datetime, timezone, timedelta

_HASH = re.compile(r"[0-9a-f]{64}\Z")


def _timestamp(raw):
    if not isinstance(raw, str):
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None
    return dt.astimezone(timezone.utc)


def asof_case_check(case, asof, max_age_days=90):
    if not isinstance(case, dict) or not isinstance(asof, datetime) or asof.tzinfo is None:
        return {"state": "HOLD_INPUT_OR_CLOCK"}
    if not isinstance(max_age_days, int) or isinstance(max_age_days, bool) or not 1 <= max_age_days <= 3650:
        return {"state": "HOLD_TIME_POLICY"}
    proof = case.get("temporal_evidence")
    if not isinstance(proof, dict):
        return {"state": "HOLD_NO_OBSERVED_SOURCE_PIN"}
    source = case.get("current_public_source")
    if not isinstance(source, dict) or proof.get("url") != source.get("url"):
        return {"state": "HOLD_SOURCE_IDENTITY"}
    digest = proof.get("sha256")
    if not isinstance(digest, str) or not _HASH.fullmatch(digest):
        return {"state": "HOLD_SOURCE_DIGEST"}
    observed = _timestamp(proof.get("observed_at"))
    published = _timestamp(proof.get("published_at"))
    expiry = _timestamp(proof.get("valid_until"))
    if not observed or not published or not expiry:
        return {"state": "HOLD_TIME_PROVENANCE"}
    at = asof.astimezone(timezone.utc)
    if published > observed or observed > at or expiry <= at or expiry <= observed:
        return {"state": "HOLD_TIME_ORDER"}
    if at-observed > timedelta(days=max_age_days):
        return {"state": "HOLD_SOURCE_STALE"}
    if case.get("current_public_source", {}).get("freshness") == "HISTORICAL_SUPERSEDED_CLAIM":
        return {"state": "HOLD_CONFLICTING_NEWER_SOURCE"}
    if not proof.get("independent_verifier_receipt"):
        return {"state": "HOLD_INDEPENDENT_SOURCE_VERIFICATION"}
    # A user-provided receipt ID is not a verified signature or authority.
    return {"state": "SOURCE_TIME_PREFLIGHT_ONLY_REQUIRES_CRYPTO_VERIFICATION"}


def asof_batch(catalog, asof):
    cases = catalog.get("cases") if isinstance(catalog, dict) else None
    if not isinstance(cases, list) or len(cases) != 18:
        return {"state": "HOLD_CANONICAL_SCOPE"}
    states = []
    for case in cases:
        if not isinstance(case, dict):
            return {"state": "HOLD_CANONICAL_SCOPE"}
        states.append({"case_id": case.get("case_id"), **asof_case_check(case, asof)})
    return {"state": "HOLD_G03_AUTHORIZED_FRESHNESS", "source_time_approved": 0,
            "cases": states}
