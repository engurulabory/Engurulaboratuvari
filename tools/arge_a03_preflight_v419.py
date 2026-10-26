"""A03 review-only preflight: structural checks with external authority explicitly HOLD.

GitHub/OSi DoneCheck authority, reviewer identity and cryptographic proof must be
verified by the existing canonical verifier, never by this helper's self-assertions.
"""
from __future__ import annotations
import re
from typing import Mapping, Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
PINNED_GITHUB = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/"
    r"(?:blob/[0-9a-f]{40}/[^#?\s]+|commit/[0-9a-f]{40})"
    r"#sha256=[0-9a-f]{64}$"
)
PINNED_LOCAL = re.compile(r"^file:///(?:[^#?\s]+/)??[^#?\s]+#sha256=[0-9a-f]{64}$")
GATES = (
    "trust_anchor_verified", "task_grant_verified",
    "reviewer_independent_verified", "source_pinned_verified",
    "donecheck_authorized_verified",
)


def _plausible_pinned_reference(value: Any) -> bool:
    """Only validate a content-addressed reference *format*, never its truth."""
    return isinstance(value, str) and bool(
        PINNED_GITHUB.fullmatch(value) or PINNED_LOCAL.fullmatch(value)
    )


SOLO_SCOPE_GATES = tuple(f"GS{i:02d}" for i in range(1, 11))
SOLO_ORIGINAL_BLOCKS = (
    tuple(f"A{i:02d}" for i in range(1, 10)),
    tuple(f"B{i:02d}" for i in range(1, 10)),
    ("C01", "C02", "C03", "D01", "D02", "D03", "D04"),
    ("C04", "C05", "C06", "E01", "E02", "E03", "E04"),
    ("F01", "F02", "F03", "F04"),
    ("G01", "G02", "G03", "G04"),
)


def assess_solo_github_preparation(handoff: Mapping[str, Any]) -> dict[str, Any]:
    """V1.3.1 10-gate owner-only GitHub *scope* review, not A03 official grant.

    GitHub Actions supplies the independently executed test evidence separately.
    A source-declared control passing here cannot issue Ed25519 or DoneCheck.
    """
    doc = handoff if isinstance(handoff, Mapping) else {}
    policy = doc.get("solo_owner_github_preparation_v2")
    policy = policy if isinstance(policy, Mapping) else {}
    preserved = doc.get("preserved_scope")
    preserved = preserved if isinstance(preserved, Mapping) else {}
    owner = doc.get("governance")
    owner = owner if isinstance(owner, Mapping) else {}
    a03 = doc.get("A03")
    a03 = a03 if isinstance(a03, Mapping) else {}
    a04 = doc.get("A04")
    a04 = a04 if isinstance(a04, Mapping) else {}
    customers = doc.get("A05_A06")
    customers = customers if isinstance(customers, Mapping) else {}
    counters = doc.get("current_counters")
    counters = counters if isinstance(counters, Mapping) else {}
    donecheck = doc.get("donecheck_human")
    donecheck = donecheck if isinstance(donecheck, Mapping) else {}
    protected = doc.get("protected_operations")
    protected = protected if isinstance(protected, Mapping) else {}
    queue = doc.get("single_active_execution_queue")
    queue = queue if isinstance(queue, list) else []

    original_ids = [task for block in SOLO_ORIGINAL_BLOCKS for task in block]
    queued = []
    valid_queue = len(queue) == 10
    for item in queue:
        if not isinstance(item, Mapping) or not isinstance(item.get("scope"), list):
            valid_queue = False
            break
        queued.extend(item["scope"])
    valid_queue = (valid_queue and all(isinstance(x, str) for x in queued)
                   and len(queued) == len(original_ids)
                   and len(set(queued)) == 40
                   and set(queued) == set(original_ids))
    pins = owner.get("pins")
    pins = pins if isinstance(pins, Mapping) else {}
    verifier_text = policy.get("mechanical_verifier")
    verifier_text = verifier_text if isinstance(verifier_text, str) else ""
    readonly_fields = (
        "main_writes", "production_code_writes", "osi_actions",
        "external_customer_evidence_reads", "actual_owner_grants_created",
        "actual_independent_reviews_created", "donecheck_ledger_writes",
        "official_finishes_created",
    )
    checks = {
        "GS01": (doc.get("schema") ==
                 "enguru.arge.b01-m01.management-decision-handoff/v1"
                 and owner.get("repository") == "engurulabory/Engurulaboratuvari"
                 and owner.get("pr") == 207),
        "GS02": (valid_queue and preserved.get("original_tasks") == 40
                 and preserved.get("blocks") == 6
                 and preserved.get("block01") == list(SOLO_ORIGINAL_BLOCKS[0])
                 and preserved.get("cases") == 18
                 and preserved.get("cells") == 234
                 and preserved.get("chosen") == ["A03", "A04", "A05", "A06"]),
        "GS03": (policy.get("approved_owner") == "engurulabory"
                 and policy.get("final_github_integrator") == "engurulabory"
                 and policy.get("mode") == "SOLO_OWNER_GITHUB_AUTOMATED_CI"),
        "GS04": (policy.get("second_human_github_reviewer_required") is False
                 and policy.get("decision_scope") ==
                 "GITHUB_RESEARCH_AND_TECHNICAL_PREPARATION_ONLY"
                 and policy.get("ready_to_automatically_merge") is False
                 and verifier_text.startswith(
                     "GitHub Actions exact-head CI")),
        "GS05": (a03.get("decision") ==
                 "HOLD_REAL_A03_OWNER_ISSUER_REVIEWER_AUTHORITY"
                 and a03.get("real_owner_grant_ref") is None
                 and a03.get("authentic_scope_grant_ref") is None
                 and a03.get("independent_review_url") is None
                 and policy.get("signed_issuer_grant") ==
                 "REQUIRES_REAL_EXISTING_SOURCE_AND_SCOPE"),
        "GS06": (a04.get("decision") == "HOLD_OWNER_CANONICAL_SCOPE"
                 and a04.get("canonical_runtime_source") is None
                 and a04.get("documented_GE_execution") == "NOT_AUTHORIZED"
                 and policy.get("a04_research_preconstruction_scope") ==
                 "GITHUB_RESEARCH_ONLY_SOURCE_EVIDENCE_ALLOWED"
                 and policy.get("a04_implemented_runtime") ==
                 "HOLD_SOURCE_NOT_PROVEN"),
        "GS07": (customers.get("customer_deployment") == "0/18"
                 and customers.get("independent_e5") == "0/18"
                 and customers.get("private_location") ==
                 "AUTHORIZED_PRIVATE_STORE"
                 and policy.get("outside_customer_e5") ==
                 "REQUIRES_GENUINE_INDEPENDENT_CUSTOMER_USE_EVIDENCE"),
        "GS08": (pins.get("universal_v3_sha256") ==
                 "11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
                 and pins.get("V19_18x13_sha256") ==
                 "3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08"
                 and policy.get("official_donecheck_issuer") ==
                 "EXISTING_CANONICAL_ONLY"),
        "GS09": (all(type(protected.get(k)) is int and protected[k] == 0
                     for k in readonly_fields)),
        "GS10": (counters.get("overall_official") == "0/40"
                 and counters.get("block01_official") == "0/9"
                 and counters.get("osi_field") == "0/100"
                 and counters.get("github_preparation") == "50/100"
                 and counters.get("independent_e5", "0/18") == "0/18"
                 and counters.get("customer_deployments", "0/18") == "0/18"
                 and donecheck.get("requires_human_accepted") is True
                 and donecheck.get("requires_separate_task_scope_grant") is True
                 and donecheck.get("real_final_state") == "HOLD"),
    }
    passed = [name for name in SOLO_SCOPE_GATES if checks[name] is True]
    failed = [name for name in SOLO_SCOPE_GATES if checks[name] is not True]
    return {
        "schema": "enguru.hym2.a03.solo-github-preparation/v1",
        "scope": "GITHUB_RESEARCH_TECHNICAL_ONLY",
        "score": 10 * len(passed),
        "denominator": 100,
        "passed_ids": passed,
        "failed_ids": failed,
        "checks": checks,
        "state": ("PASS_SOLO_GITHUB_SCOPE_SPEC_ONLY" if not failed
                  else "HOLD_SOLO_GITHUB_SCOPE_SPEC"),
        "github_ci": "REQUIRES_EXACT_HEAD_GITHUB_ACTIONS_EVIDENCE",
        "real_owner_grant": "HOLD",
        "a03_official": "HOLD",
        "a04_official": "HOLD",
        "customer_e5": "HOLD_0_OF_18",
        "verified_finish": "HOLD",
    }


def assess_a03(record: Mapping[str, Any]) -> dict[str, Any]:
    """Fail closed on untrusted evidence; this helper cannot grant acceptance.

    Even a fully formed self-reported record requires actual independent issuer,
    signer, reviewer, source and evidence verification by existing authorities.
    """
    blockers: list[str] = []
    if not isinstance(record, Mapping):
        record = {}
        blockers.append("INVALID_RECORD")

    if record.get("task_id") != "A03":
        blockers.append("TASK_SCOPE")
    if not isinstance(record.get("source_commit"), str) or not SHA1.fullmatch(record["source_commit"]):
        blockers.append("SOURCE_COMMIT_FORMAT")
    if not isinstance(record.get("artifact_sha256"), str) or not SHA256.fullmatch(record["artifact_sha256"]):
        blockers.append("ARTIFACT_DIGEST_FORMAT")

    producer = record.get("producer_id")
    reviewer = record.get("reviewer_id")
    if not isinstance(producer, str) or not producer.strip():
        blockers.append("PRODUCER_ID_MISSING")
    if not isinstance(reviewer, str) or not reviewer.strip():
        blockers.append("REVIEWER_ID_MISSING")
    if isinstance(producer, str) and isinstance(reviewer, str) and producer.strip() and reviewer.strip() and producer.strip() == reviewer.strip():
        blockers.append("REVIEWER_NOT_INDEPENDENT")

    for gate in GATES:
        if record.get(gate) is not True:
            blockers.append(gate.upper())
        if not _plausible_pinned_reference(record.get(gate + "_evidence_ref")):
            blockers.append(gate.upper() + "_EVIDENCE_REF_INVALID")

    # A self-declared boolean, 40-hex SHA or URL is never proof of real authority.
    format_ok = not blockers
    return {
        "state": "HOLD",
        "structural_preflight": "PASS_FORMAT_ONLY" if format_ok else "HOLD_INVALID_INPUT",
        "blockers": blockers + ["EXTERNAL_AUTHORITY_VERIFICATION_REQUIRED"],
        "official_acceptance": False,
        "verified_finish": False,
    }
