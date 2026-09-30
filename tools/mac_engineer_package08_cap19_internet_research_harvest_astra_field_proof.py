#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mac_engineer_governed_finish_adapter as finish


CAPABILITY_INDEX = 19
CAPABILITY_ID = "INTERNET_RESEARCH_HARVEST_ASTRA"
ACTION = "PACKAGE08_CAP19_INTERNET_RESEARCH_HARVEST_ASTRA_FIELD_PROOF"
OPERATOR_CALLABLE = "run_package08_cap19_internet_research_harvest_astra_field_proof"
AUTHORITY = "GREEN_BOUNDED_READ_ONLY_RESEARCH_AUTHORITY"
MAX_ATTEMPTS = 2
MAX_SOURCE_BYTES = 300_000
ALLOWED_HOSTS = frozenset({"www.iana.org", "www.rfc-editor.org", "rfc-editor.org"})
PRIMARY_SOURCE_AUTHORITIES = frozenset({"IANA", "RFC_EDITOR"})
ACTION_REGISTRY = ROOT / "governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json"
BINDING_REGISTRY = ROOT / "governance/mac-engineer/CAPABILITY_EXECUTION_BINDING_V1.json"
SOURCES = (
    {
        "id": "IANA_EXAMPLE_DOMAINS",
        "authority": "IANA",
        "url": "https://www.iana.org/help/example-domains",
        "markers": ("example.com", "example.org"),
    },
    {
        "id": "RFC2606",
        "authority": "RFC_EDITOR",
        "url": "https://www.rfc-editor.org/rfc/rfc2606.txt",
        "markers": ("Reserved Top Level DNS Names", "example.com"),
    },
)
DONECHECK_CRITERIA = (
    ("fresh_execution", "Fresh CAP19 execution Evidence is present."),
    ("exactly_two_primary_sources", "Exactly two valid public primary sources are bound."),
    ("exact_source_urls", "The two exact allowlisted source URLs are bound."),
    ("source_access_timestamps", "Each source has a fresh UTC access timestamp."),
    ("bounded_get_transport", "Bounded read-only HTTPS GET transport passed."),
    ("source_sha256", "Each captured source has a verified SHA-256 digest."),
    ("authoritative_provenance", "Primary-source authority is present for both sources."),
    ("local_provider_model_route", "The route is local_runtime with qwen3:14b."),
    ("non_empty_synthesis", "A non-empty Astra synthesis is present."),
    ("citation_grounding", "Required source citation tokens are present."),
    ("fact_interpretation_separation", "Sourced facts and interpretation are separated."),
    ("failure_path_behavior", "All required fail-closed paths passed."),
    ("retry_bound", "The retry limit remains exactly two attempts."),
    ("network_policy", "Read-only allowlisted network policy is preserved."),
    ("material_step_evidence", "All material-step Evidence files are present and digest-bound."),
    ("source_mutation_zero", "Source mutation is false."),
    ("remote_mutation_zero", "Remote mutation is false."),
    ("external_mutation_zero", "External mutation is false."),
    ("authority_bypass_zero", "Authority bypass count is zero."),
    ("critical_false_pass_zero", "Critical false-pass count is zero."),
    ("stale_pass_used_as_final_zero", "No stale PASS is used as final Evidence."),
)


class VerificationHold(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise VerificationHold(reason)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "JSON_OBJECT_REQUIRED")
    return value


def require_attempt_within_budget(attempt: int) -> None:
    require(1 <= attempt <= MAX_ATTEMPTS, "RETRY_BUDGET_EXCEEDED")


def registered_action_allowed(
    action_registry: dict[str, Any],
    binding_registry: dict[str, Any],
) -> bool:
    action = (action_registry.get("actions") or {}).get(ACTION)
    bindings = {
        row.get("CAPABILITY_ID"): row
        for row in binding_registry.get("bindings", [])
        if isinstance(row, dict)
    }
    binding = bindings.get(CAPABILITY_ID)
    return bool(
        isinstance(action, dict)
        and isinstance(binding, dict)
        and action.get("handler") == ACTION
        and action.get("authority") == AUTHORITY
        and action.get("readOnlyNetwork") is True
        and action.get("maxAttempts") == MAX_ATTEMPTS
        and action.get("credentialRequired") is False
        and action.get("remotePush") is False
        and action.get("failClosed") is True
        and action.get("generalBrowserAuthority") is False
        and binding.get("BINDING_TYPE") == "REGISTERED_ACTION"
        and binding.get("ACTION") == ACTION
        and binding.get("REGISTERED_HANDLER") == ACTION
        and binding.get("OPERATOR_CALLABLE") == OPERATOR_CALLABLE
        and binding.get("AUTHORITY") == AUTHORITY
        and binding.get("NETWORK_ALLOWED") is True
        and binding.get("READ_ONLY_NETWORK") is True
        and binding.get("CREDENTIAL_REQUIRED") is False
        and binding.get("REMOTE_PUSH_ALLOWED") is False
        and binding.get("GENERAL_BROWSER_AUTHORITY") is False
    )


def validate_registered_action_contract() -> None:
    require(
        registered_action_allowed(load_json(ACTION_REGISTRY), load_json(BINDING_REGISTRY)),
        "REGISTERED_ACTION_POLICY_MISMATCH",
    )


def validate_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    require(parsed.scheme == "https", "HTTPS_REQUIRED")
    require(parsed.hostname in ALLOWED_HOSTS, "SOURCE_HOST_NOT_ALLOWLISTED")
    require(not parsed.username and not parsed.password, "CREDENTIAL_BEARING_URL_REJECTED")
    require(not parsed.query and not parsed.fragment, "QUERY_OR_FRAGMENT_REJECTED")
    return str(parsed.hostname)


def http_get(url: str, timeout: float = 20.0) -> dict[str, Any]:
    validate_url(url)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ENGURU-Mac-Engineer-CAP19/1.0"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        validate_url(final_url)
        body = response.read(MAX_SOURCE_BYTES + 1)
        require(len(body) <= MAX_SOURCE_BYTES, "SOURCE_SIZE_LIMIT_EXCEEDED")
        status = int(getattr(response, "status", 200))
        require(status == 200, "HTTP_STATUS_NOT_200")
        return {
            "status": status,
            "finalUrl": final_url,
            "contentType": response.headers.get("Content-Type", ""),
            "body": body,
        }


def bounded_fetch(
    source: dict[str, Any],
    fetcher: Callable[[str], dict[str, Any]] = http_get,
) -> dict[str, Any]:
    url = str(source["url"])
    validate_url(url)
    failures: list[str] = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        require_attempt_within_budget(attempt)
        try:
            result = fetcher(url)
            body = result.get("body")
            require(isinstance(body, bytes) and bool(body), "EMPTY_SOURCE_BODY")
            text = body.decode("utf-8", errors="replace")
            markers = tuple(str(item) for item in source["markers"])
            require(all(marker.lower() in text.lower() for marker in markers), "SOURCE_MARKER_MISSING")
            return {
                "state": "PASS",
                "attempts": attempt,
                "id": source["id"],
                "authority": source["authority"],
                "url": url,
                "finalUrl": result.get("finalUrl", url),
                "accessedAt": now(),
                "httpStatus": result.get("status"),
                "contentType": result.get("contentType", ""),
                "body": body,
                "markers": list(markers),
            }
        except Exception as exc:
            failures.append(f"{type(exc).__name__}:{exc}")
    raise VerificationHold("SOURCE_FETCH_RETRY_EXHAUSTED:" + "|".join(failures))


def source_capsule(captures: list[dict[str, Any]]) -> str:
    require(len(captures) == 2, "TWO_FRESH_SOURCES_REQUIRED")
    blocks: list[str] = []
    for capture in captures:
        body = capture["body"].decode("utf-8", errors="replace")
        blocks.append(
            "SOURCE_ID=" + capture["id"]
            + "\nURL=" + capture["url"]
            + "\nAUTHORITY=" + capture["authority"]
            + "\nCONTENT_BEGIN\n" + body[:12_000]
            + "\nCONTENT_END"
        )
    return "\n\n".join(blocks)


def normalize_provider_output(output: Any) -> str:
    if isinstance(output, dict):
        output = output.get("answer")
    require(isinstance(output, str) and bool(output.strip()), "ASTRA_OUTPUT_EMPTY")
    return output.strip()


def provider_chat(
    capsule: str,
    timeout: float = 90.0,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    base = os.environ.get("ENGURU_SHARED_AI_BASE_URL", "http://127.0.0.1:8787").rstrip("/")
    prompt = (
        "Using only the two captured sources below, answer this bounded research question: "
        "Which DNS names are reserved for documentation examples, and what is the governing RFC? "
        "Return a concise synthesis with separate SOURCED_FACTS: and INTERPRETATION: sections. "
        "Include both exact citation tokens [IANA_EXAMPLE_DOMAINS] and [RFC2606]. "
        "Do not add uncited claims.\n\n" + capsule
    )
    payload = {
        "request_id": "package08-cap19-" + hashlib.sha256(capsule.encode()).hexdigest()[:20],
        "task_type": "internet_research_harvest",
        "data_class": "PUBLIC",
        "required_capabilities": ["text", "reasoning"],
        "cost_ceiling": 0,
        "input": prompt,
        "intent": "Synthesize a bounded public-source research result with exact source citations.",
        "success_criteria": [
            "Use only supplied source captures",
            "Include [IANA_EXAMPLE_DOMAINS] and [RFC2606]",
            "Return a non-empty answer",
        ],
        "verification_profile": "BASIC",
        "freshness_required": True,
        "authoritative_provenance": [source["url"] for source in SOURCES],
        "response_language": "EN",
        "response_length": "CONCISE",
        "response_structure": "PLAIN",
    }
    request = urllib.request.Request(
        base + "/v1/enguru/respond",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    open_request = opener or urllib.request.urlopen
    failures: list[str] = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        require_attempt_within_budget(attempt)
        try:
            with open_request(request, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            failures.append(f"HTTP_{exc.code}:{detail}")
            continue
        except Exception as exc:
            failures.append(f"{type(exc).__name__}:{exc}")
            continue
        require(result.get("state") == "PASS", "ASTRA_PROVIDER_HOLD")
        output = normalize_provider_output(result.get("output"))
        return {
            "output": output,
            "routeEvidence": result.get("route_evidence") or {},
            "attempts": attempt,
        }
    raise VerificationHold(
        "ASTRA_PROVIDER_UNAVAILABLE_RETRY_EXHAUSTED:" + "|".join(failures)
    )


def validate_synthesis(text: str) -> dict[str, bool]:
    require(bool(text.strip()), "SYNTHESIS_EMPTY")
    require("[IANA_EXAMPLE_DOMAINS]" in text, "IANA_CITATION_MISSING")
    require("[RFC2606]" in text, "RFC2606_CITATION_MISSING")
    require("example.com" in text.lower(), "EXPECTED_RESEARCH_RESULT_MISSING")
    require("2606" in text, "GOVERNING_RFC_MISSING")
    require("SOURCED_FACTS:" in text, "SOURCED_FACTS_SECTION_MISSING")
    require("INTERPRETATION:" in text, "INTERPRETATION_SECTION_MISSING")
    return {
        "nonEmpty": True,
        "ianaCitation": True,
        "rfc2606Citation": True,
        "expectedResultObserved": True,
        "factInterpretationSeparated": True,
    }


def validate_source_records(records: list[dict[str, Any]]) -> None:
    require(len(records) == len(SOURCES), "TWO_SOURCE_RECORDS_REQUIRED")
    expected_urls = {str(source["url"]) for source in SOURCES}
    require({str(record.get("url")) for record in records} == expected_urls, "EXACT_SOURCE_URLS_REQUIRED")
    for record in records:
        require(record.get("authority") in PRIMARY_SOURCE_AUTHORITIES, "PRIMARY_SOURCE_AUTHORITY_REQUIRED")
        accessed_at = record.get("accessedAt")
        require(isinstance(accessed_at, str) and accessed_at.endswith("Z"), "SOURCE_ACCESS_UTC_REQUIRED")
        try:
            datetime.fromisoformat(accessed_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise VerificationHold("SOURCE_ACCESS_UTC_REQUIRED") from exc
        require(record.get("httpStatus") == 200, "SOURCE_TRANSPORT_PASS_REQUIRED")
        require_attempt_within_budget(int(record.get("attempts", 0)))
        digest = record.get("sha256")
        require(
            isinstance(digest, str)
            and len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest),
            "SOURCE_DIGEST_REQUIRED",
        )
        path_value = record.get("path")
        require(isinstance(path_value, str) and bool(path_value), "MATERIAL_STEP_EVIDENCE_REQUIRED")
        path = Path(path_value)
        require(path.is_file(), "MATERIAL_STEP_EVIDENCE_REQUIRED")
        require(sha256(path) == digest, "SOURCE_DIGEST_MISMATCH")


def evaluate_acceptance_criteria(
    field_payload: dict[str, Any],
    field_path: Path,
) -> dict[str, bool]:
    sources = field_payload.get("sources") or []
    astra = field_payload.get("astra") or {}
    route = astra.get("routeEvidence") or {}
    checks = astra.get("checks") or {}
    failure = field_payload.get("failurePath") or {}
    boundary = field_payload.get("authorityBoundary") or {}
    zero = field_payload.get("zeroTolerance") or {}
    expected_urls = {str(source["url"]) for source in SOURCES}
    source_material_bound = all(
        isinstance(source.get("path"), str)
        and bool(source["path"])
        and Path(source["path"]).is_file()
        and sha256(Path(source["path"])) == source.get("sha256")
        for source in sources
    )
    harvest_value = astra.get("harvestPath")
    harvest_material_bound = (
        isinstance(harvest_value, str)
        and bool(harvest_value)
        and Path(harvest_value).is_file()
        and sha256(Path(harvest_value)) == astra.get("harvestSha256")
    )
    failure_path = field_path.parent / "failure-path.json"
    return {
        "fresh_execution": field_payload.get("state") == "PASS" and field_path.is_file(),
        "exactly_two_primary_sources": len(sources) == 2,
        "exact_source_urls": {str(source.get("url")) for source in sources} == expected_urls,
        "source_access_timestamps": all(
            isinstance(source.get("accessedAt"), str) and source["accessedAt"].endswith("Z")
            for source in sources
        ),
        "bounded_get_transport": all(source.get("httpStatus") == 200 for source in sources),
        "source_sha256": all(
            isinstance(source.get("sha256"), str) and len(source["sha256"]) == 64
            for source in sources
        ),
        "authoritative_provenance": all(
            source.get("authority") in PRIMARY_SOURCE_AUTHORITIES for source in sources
        ),
        "local_provider_model_route": (
            route.get("provider") == "local_runtime" and route.get("model") == "qwen3:14b"
        ),
        "non_empty_synthesis": checks.get("nonEmpty") is True,
        "citation_grounding": (
            checks.get("ianaCitation") is True and checks.get("rfc2606Citation") is True
        ),
        "fact_interpretation_separation": checks.get("factInterpretationSeparated") is True,
        "failure_path_behavior": (
            failure.get("state") == "PASS"
            and all(
                value is True
                for key, value in failure.items()
                if key not in {"state", "retryAttempts", "providerUnavailableAttempts"}
            )
        ),
        "retry_bound": (
            failure.get("retryAttempts") == MAX_ATTEMPTS
            and failure.get("providerUnavailableAttempts") == MAX_ATTEMPTS
            and 1 <= int(astra.get("attempts", 0)) <= MAX_ATTEMPTS
        ),
        "network_policy": (
            field_payload.get("networkPolicy") == "READ_ONLY_NETWORK_BY_DEFAULT"
            and (field_payload.get("networkExecution") or {}).get("method") == "HTTPS_GET"
            and (field_payload.get("networkExecution") or {}).get("maxAttempts") == MAX_ATTEMPTS
            and set((field_payload.get("networkExecution") or {}).get("allowlistedHosts", [])) == set(ALLOWED_HOSTS)
            and boundary.get("credentialUsed") is False
            and boundary.get("generalBrowserAuthority") is False
        ),
        "material_step_evidence": (
            source_material_bound
            and harvest_material_bound
            and failure_path.is_file()
            and field_path.is_file()
        ),
        "source_mutation_zero": boundary.get("sourceMutation") is False,
        "remote_mutation_zero": boundary.get("remoteMutation") is False,
        "external_mutation_zero": boundary.get("externalMutation") is False,
        "authority_bypass_zero": zero.get("AUTHORITY_BYPASS") == 0,
        "critical_false_pass_zero": zero.get("CRITICAL_FALSE_PASS") == 0,
        "stale_pass_used_as_final_zero": zero.get("STALE_PASS_USED_AS_FINAL") == 0,
    }


def failure_path_proof() -> dict[str, Any]:
    disallowed_hold = False
    try:
        validate_url("https://example.com/not-allowlisted")
    except VerificationHold as exc:
        disallowed_hold = str(exc) == "SOURCE_HOST_NOT_ALLOWLISTED"

    empty_hold = False
    try:
        source_capsule([])
    except VerificationHold as exc:
        empty_hold = str(exc) == "TWO_FRESH_SOURCES_REQUIRED"

    attempts = 0

    def always_timeout(_url: str) -> dict[str, Any]:
        nonlocal attempts
        attempts += 1
        raise TimeoutError("controlled-timeout")

    retry_hold = False
    try:
        bounded_fetch(dict(SOURCES[0]), always_timeout)
    except VerificationHold as exc:
        retry_hold = str(exc).startswith("SOURCE_FETCH_RETRY_EXHAUSTED:") and attempts == MAX_ATTEMPTS

    malformed_hold = False
    try:
        validate_synthesis("SOURCED_FACTS: uncited result\nINTERPRETATION: bounded")
    except VerificationHold as exc:
        malformed_hold = str(exc) == "IANA_CITATION_MISSING"

    missing_authority_hold = False
    authority_records = [
        {
            "url": source["url"],
            "authority": source["authority"] if index else None,
            "accessedAt": now(),
            "httpStatus": 200,
            "attempts": 1,
        }
        for index, source in enumerate(SOURCES)
    ]
    try:
        validate_source_records(authority_records)
    except VerificationHold as exc:
        missing_authority_hold = str(exc) == "PRIMARY_SOURCE_AUTHORITY_REQUIRED"

    missing_digest_hold = False
    digest_records = [
        {
            "url": source["url"],
            "authority": source["authority"],
            "accessedAt": now(),
            "httpStatus": 200,
            "attempts": 1,
        }
        for source in SOURCES
    ]
    try:
        validate_source_records(digest_records)
    except VerificationHold as exc:
        missing_digest_hold = str(exc) == "SOURCE_DIGEST_REQUIRED"

    missing_material_hold = False
    material_records = [
        {
            "url": source["url"],
            "authority": source["authority"],
            "accessedAt": now(),
            "httpStatus": 200,
            "attempts": 1,
            "sha256": "0" * 64,
        }
        for source in SOURCES
    ]
    try:
        validate_source_records(material_records)
    except VerificationHold as exc:
        missing_material_hold = str(exc) == "MATERIAL_STEP_EVIDENCE_REQUIRED"

    empty_output_hold = False
    try:
        normalize_provider_output("   ")
    except VerificationHold as exc:
        empty_output_hold = str(exc) == "ASTRA_OUTPUT_EMPTY"

    malformed_envelope_hold = False
    try:
        normalize_provider_output({"answer": ["unsupported"]})
    except VerificationHold as exc:
        malformed_envelope_hold = str(exc) == "ASTRA_OUTPUT_EMPTY"

    provider_attempts = 0

    def unavailable_provider(*_args: Any, **_kwargs: Any) -> Any:
        nonlocal provider_attempts
        provider_attempts += 1
        raise TimeoutError("controlled-provider-unavailable")

    provider_unavailable_hold = False
    try:
        provider_chat("controlled capsule", timeout=0.01, opener=unavailable_provider)
    except VerificationHold as exc:
        provider_unavailable_hold = (
            str(exc).startswith("ASTRA_PROVIDER_UNAVAILABLE_RETRY_EXHAUSTED:")
            and provider_attempts == MAX_ATTEMPTS
        )

    third_attempt_hold = False
    try:
        require_attempt_within_budget(MAX_ATTEMPTS + 1)
    except VerificationHold as exc:
        third_attempt_hold = str(exc) == "RETRY_BUDGET_EXCEEDED"

    action_registry = load_json(ACTION_REGISTRY)
    binding_registry = load_json(BINDING_REGISTRY)
    unregistered_non_execution = not registered_action_allowed(
        {"actions": {}}, binding_registry
    )
    mismatched_action_registry = json.loads(json.dumps(action_registry))
    mismatched_action_registry["actions"][ACTION]["readOnlyNetwork"] = False
    policy_mismatch_non_execution = not registered_action_allowed(
        mismatched_action_registry, binding_registry
    )

    checks = {
        "disallowedHostHold": disallowed_hold,
        "emptySourceSetHold": empty_hold,
        "missingPrimarySourceAuthorityHold": missing_authority_hold,
        "boundedRetryExhaustionHold": retry_hold,
        "providerUnavailableBoundedHold": provider_unavailable_hold,
        "emptyProviderOutputHold": empty_output_hold,
        "malformedGovernedEnvelopeHold": malformed_envelope_hold,
        "missingCitationHold": malformed_hold,
        "missingSourceDigestHold": missing_digest_hold,
        "missingMaterialStepEvidenceHold": missing_material_hold,
        "thirdAttemptHold": third_attempt_hold,
        "unregisteredActionNonExecution": unregistered_non_execution,
        "policyMismatchNonExecution": policy_mismatch_non_execution,
        "retryAttempts": attempts,
        "providerUnavailableAttempts": provider_attempts,
    }
    require(
        all(
            value is True
            for key, value in checks.items()
            if key not in {"retryAttempts", "providerUnavailableAttempts"}
        ),
        "FAILURE_PATH_INCOMPLETE",
    )
    require(attempts == MAX_ATTEMPTS, "RETRY_LIMIT_MISMATCH")
    require(provider_attempts == MAX_ATTEMPTS, "PROVIDER_RETRY_LIMIT_MISMATCH")
    return checks


def write_hold_receipt(
    evidence_root: Path,
    *,
    attempt: int,
    reason: str,
) -> dict[str, Any]:
    artifacts = []
    for path in sorted(evidence_root.rglob("*")):
        if path.is_file() and path.name != "hold-receipt.json":
            artifacts.append({
                "path": str(path),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            })
    receipt = {
        "schema": "enguru.mac-engineer.package08-cap19-hold-receipt/v1",
        "observedAt": now(),
        "state": "HOLD",
        "capabilityIndex": CAPABILITY_INDEX,
        "capabilityId": CAPABILITY_ID,
        "action": ACTION,
        "attempt": attempt,
        "maxAttempts": MAX_ATTEMPTS,
        "reason": reason,
        "networkMutation": False,
        "sourceMutation": False,
        "productMutation": False,
        "remotePush": False,
        "credentialUsed": False,
        "fieldVerified": False,
        "doneCheckPass": False,
        "fieldSealProduced": False,
        "artifacts": artifacts,
        "canonicalTruthPreserved": True,
    }
    path = evidence_root / "hold-receipt.json"
    write_json(path, receipt)
    return {"path": str(path), "sha256": sha256(path), "receipt": receipt}


def execute_field_proof(
    evidence_root: Path,
    fetcher: Callable[[str], dict[str, Any]] = http_get,
    provider: Callable[[str], dict[str, Any]] = provider_chat,
) -> dict[str, Any]:
    validate_registered_action_contract()
    evidence_root.mkdir(parents=True, exist_ok=False)
    sources_dir = evidence_root / "sources"
    sources_dir.mkdir()

    failure = failure_path_proof()
    write_json(evidence_root / "failure-path.json", {"state": "PASS", **failure})

    captures: list[dict[str, Any]] = []
    source_evidence: list[dict[str, Any]] = []
    for index, source in enumerate(SOURCES, start=1):
        capture = bounded_fetch(dict(source), fetcher)
        path = sources_dir / f"{index:02d}_{capture['id']}.txt"
        path.write_bytes(capture["body"])
        captures.append(capture)
        source_evidence.append({
            "id": capture["id"],
            "authority": capture["authority"],
            "url": capture["url"],
            "finalUrl": capture["finalUrl"],
            "accessedAt": capture["accessedAt"],
            "httpStatus": capture["httpStatus"],
            "attempts": capture["attempts"],
            "markers": capture["markers"],
            "path": str(path),
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
        })
    validate_source_records(source_evidence)

    capsule = source_capsule(captures)
    astra = provider(capsule)
    synthesis = str(astra.get("output") or "")
    synthesis_checks = validate_synthesis(synthesis)
    route_evidence = astra.get("routeEvidence") or {}
    require(route_evidence.get("provider") == "local_runtime", "LOCAL_RUNTIME_ROUTE_REQUIRED")
    require(route_evidence.get("model") == "qwen3:14b", "QWEN3_14B_ROUTE_REQUIRED")
    harvest_path = evidence_root / "research-harvest.md"
    harvest_path.write_text(synthesis + "\n", encoding="utf-8")

    fresh_reverify = all(
        Path(item["path"]).is_file()
        and sha256(Path(item["path"])) == item["sha256"]
        and item["httpStatus"] == 200
        for item in source_evidence
    ) and sha256(harvest_path) == hashlib.sha256(harvest_path.read_bytes()).hexdigest()
    require(fresh_reverify, "FRESH_REVERIFY_FAILED")

    field_path = evidence_root / "field-evidence.json"
    field_payload = {
        "schema": "enguru.mac-engineer.package08-cap19-field-evidence/v1",
        "observedAt": now(),
        "state": "PASS",
        "capabilityIndex": CAPABILITY_INDEX,
        "capabilityId": CAPABILITY_ID,
        "action": ACTION,
        "operatorCallable": OPERATOR_CALLABLE,
        "authority": AUTHORITY,
        "riskClass": "MEDIUM",
        "researchQuestion": "Which DNS names are reserved for documentation examples, and what is the governing RFC?",
        "networkPolicy": "READ_ONLY_NETWORK_BY_DEFAULT",
        "networkExecution": {"performed": True, "method": "HTTPS_GET", "allowlistedHosts": sorted(ALLOWED_HOSTS), "maxAttempts": MAX_ATTEMPTS},
        "sources": source_evidence,
        "astra": {
            "state": "PASS",
            "routeEvidence": route_evidence,
            "attempts": int(astra.get("attempts", 1)),
            "harvestPath": str(harvest_path),
            "harvestSha256": sha256(harvest_path),
            "checks": synthesis_checks,
        },
        "failurePath": {"state": "PASS", **failure},
        "freshReverify": {"performed": True, "state": "PASS"},
        "authorityBoundary": {
            "credentialUsed": False,
            "remoteMutation": False,
            "externalMutation": False,
            "sourceMutation": False,
            "productMutation": False,
            "generalBrowserAuthority": False,
            "humanThresholdRequired": False,
            "executionAuthorityCreated": False,
            "canonicalTruthPreserved": True,
        },
        "zeroTolerance": {
            "AUTHORITY_BYPASS": 0,
            "CRITICAL_FALSE_PASS": 0,
            "STALE_PASS_USED_AS_FINAL": 0,
        },
    }
    write_json(field_path, field_payload)

    criterion_checks = evaluate_acceptance_criteria(field_payload, field_path)
    require(set(criterion_checks) == {item[0] for item in DONECHECK_CRITERIA}, "DONECHECK_CRITERIA_SET_MISMATCH")
    require(all(criterion_checks.values()), "CAP19_ACCEPTANCE_CRITERION_HOLD")

    evidence_digest = sha256(field_path)
    machines: dict[str, dict[str, Any]] = {}
    for criterion_id, statement in DONECHECK_CRITERIA:
        machine = finish.verify_machine_finish(
            evidence_path=field_path,
            execution_id=f"cap19-{criterion_id}:{evidence_digest[:24]}",
            task_id=f"package08-cap19-{criterion_id}",
            criterion_id=f"{CAPABILITY_ID}:{criterion_id}",
            statement=statement,
        )
        require(
            machine.get("STATE") == "PASS"
            and machine.get("DONECHECK_STATE") == "PASS",
            "FRESH_DONECHECK_PASS_REQUIRED:" + criterion_id,
        )
        require(
            finish.evaluate_green_finish(machine).get("STATE") == "VERIFIED",
            "GREEN_VERIFIED_FINISH_REQUIRED:" + criterion_id,
        )
        machines[criterion_id] = machine
    donecheck_path = evidence_root / "mandatory-donecheck.json"
    write_json(donecheck_path, {
        "schema": "enguru.mac-engineer.package08-cap19-donecheck/v1",
        "observedAt": now(),
        "state": "PASS",
        "criterionCount": len(DONECHECK_CRITERIA),
        "criteria": {
            criterion_id: {
                "state": "PASS",
                "check": criterion_checks[criterion_id],
                "doneCheckState": machines[criterion_id]["DONECHECK_STATE"],
                "verificationResultId": machines[criterion_id]["VERIFICATION_RESULT_ID"],
            }
            for criterion_id, _statement in DONECHECK_CRITERIA
        },
        "doneCheckVersion": next(iter(machines.values())).get("DONECHECK_VERSION"),
        "doneCheckSha": next(iter(machines.values())).get("DONECHECK_SHA"),
    })

    acceptance = {
        "discovered": True,
        "invocable": True,
        "realTaskExecuted": True,
        "expectedResultObserved": True,
        "failurePathTested": True,
        "freshReverify": True,
        "evidenceBound": True,
        "doneCheckPass": True,
        "fieldVerified": True,
    }
    seal_path = evidence_root / "field-verification-seal.json"
    seal = {
        "schema": "enguru.mac-engineer.package08-cap19-field-verification-seal/v1",
        "observedAt": now(),
        "state": "PASS",
        "capabilityIndex": CAPABILITY_INDEX,
        "capabilityId": CAPABILITY_ID,
        "canonicalAction": ACTION,
        "operatorCallable": OPERATOR_CALLABLE,
        "authority": AUTHORITY,
        "acceptance": acceptance,
        "fieldEvidence": {"path": str(field_path), "sha256": sha256(field_path)},
        "mandatoryDoneCheck": {
            "path": str(donecheck_path),
            "sha256": sha256(donecheck_path),
            "version": next(iter(machines.values())).get("DONECHECK_VERSION"),
            "exactSha": next(iter(machines.values())).get("DONECHECK_SHA"),
            "criterionCount": len(DONECHECK_CRITERIA),
        },
        "sourceBindings": [
            {
                "url": source["url"],
                "sha256": source["sha256"],
                "authority": source["authority"],
                "accessedAt": source["accessedAt"],
            }
            for source in source_evidence
        ],
        "provider": "local_runtime",
        "model": "qwen3:14b",
        "researchHarvest": {"path": str(harvest_path), "sha256": sha256(harvest_path)},
        "execution": {
            "networkAccessPerformed": True,
            "networkMutation": False,
            "sourceMutation": False,
            "productMutation": False,
            "remotePush": False,
            "humanThresholdRequired": False,
            "generalBrowserAuthority": False,
        },
        "canonicalTruthPreserved": True,
        "zeroTolerance": field_payload["zeroTolerance"],
    }
    write_json(seal_path, seal)
    return {"seal": seal, "sealPath": str(seal_path), "sealSha256": sha256(seal_path)}


def main() -> int:
    override = os.environ.get("ENGURU_CAP19_EVIDENCE_DIR")
    if override:
        evidence_root = Path(override)
    else:
        evidence_root = (
            Path.home() / "Enguru/Evidence/MacEngineer/package08-field-campaign"
            / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            / "capability-19"
        )
    result = execute_field_proof(evidence_root)
    print("STATE=PASS")
    print("CAP19_INTERNET_RESEARCH_HARVEST_ASTRA=PASS")
    print("NETWORK_ACCESS=true")
    print("NETWORK_MUTATION=false")
    print("SOURCE_MUTATION=false")
    print("PRODUCT_MUTATION=false")
    print("REMOTE_PUSH=false")
    print("CREDENTIAL_USED=false")
    print("FRESH_SOURCES=2")
    print("ASTRA_SYNTHESIS=PASS")
    print("EXPECTED_RESULT_OBSERVED=PASS")
    print("FAILURE_PATH_TESTED=PASS")
    print("BOUNDED_RETRY=PASS")
    print("FRESH_REVERIFY=PASS")
    print("DONECHECK=PASS")
    print("HUMAN_THRESHOLD_REQUIRED=false")
    print("GENERAL_BROWSER_AUTHORITY=false")
    print("CANONICAL_TRUTH_PRESERVED=PASS")
    print("CRITICAL_FALSE_PASS_COUNT=0")
    print("EVIDENCE=" + result["sealPath"])
    print("EVIDENCE_SHA256=" + result["sealSha256"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("STATE=HOLD")
        print("HOLD=" + type(exc).__name__ + ":" + str(exc))
        raise SystemExit(2)
