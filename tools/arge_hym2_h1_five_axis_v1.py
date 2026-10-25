#!/usr/bin/env python3
"""HYM2 Hedef 1 source-bound five-axis GitHub preparation audit.

Reuse canonical Hybrid Project evaluator (no new scoring core).
Read-only tracked-byte audit; H1 A01-A09 acceptance remains HOLD until
product-specific reviewer, real customer evidence, security and human decisions.
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

from tools.hybrid_handoff import validate_hybrid_handoff as hybrid

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "tools/hybrid_handoff/labory-osi-project.example.json"
V3 = ROOT / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
LOCK = ROOT / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json"
CASES = ROOT / "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json"
UPSTREAM = ROOT / "governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_A04_UPSTREAM_LICENSE_PINS_V1.json"
V19_PIN = "3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08"
ORIGINAL_BLOCKS = (
    tuple(f"A{i:02}" for i in range(1, 10)),
    tuple(f"B{i:02}" for i in range(1, 10)),
    ("C01","C02","C03","D01","D02","D03","D04"),
    ("C04","C05","C06","E01","E02","E03","E04"),
    ("F01","F02","F03","F04"),
    ("G01","G02","G03","G04"),
)
H1_TASKS = (
    ("A01","18 vaka / 6 alan kaynak envanteri"),
    ("A02","234 hücre K01-K13 özgün kaynak matrisi"),
    ("A03","Ar-Ge canonical kabul sözleşmesi ve geçerli owner/reviewer yetkisi"),
    ("A04","7 teknoloji upstream sürüm/lisans/güvenlik kaynak denetimi"),
    ("A05","18 vaka müşteri kurulu sürüm ve kanıt"),
    ("A06","18 vaka bağımsız E5 doğrulaması"),
    ("A07","G01-G03 mimari güvence ve karşıt test"),
    ("A08","K12 5 yıllık ROI/TCO ve duyarlılık"),
    ("A09","Mimarlık Ar-Ge delilli birleştirme ve devir"),
)


def build_plan(root=ROOT):
    original = [cid for group in ORIGINAL_BLOCKS for cid in group]
    if len(original) != 40 or len(set(original)) != 40 or len(H1_TASKS) != 9:
        raise ValueError("HOLD_ORIGINAL_40_AND_H1_NINE")
    source = json.loads(CASES.read_text(encoding="utf-8"))
    upstream = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    if (source["baseline"]["rows"] != 234 or
        source["baseline"]["sha256"] != V19_PIN or
        len(source["cases"]) != 18 or
        len(upstream["tech"]) != 7 or
        lock["sha256"] != hashlib.sha256(V3.read_bytes()).hexdigest()):
        raise ValueError("HOLD_CANONICAL_SOURCE_PIN")
    packet = copy.deepcopy(json.loads(EXAMPLE.read_text(encoding="utf-8")))
    snapshot = hybrid.source_snapshot(root)
    packet.update(projectId="ENGURU-HYM-AR-GE",
                  subproduct="Hedef 1 — Mimarlık / B01-M01 A03+A04",
                  executionMode="GITHUB_FIRST",
                  sourceRef="ACTUAL_GITHUB_CI_CHECKOUT_HEAD",
                  sourceCommit=snapshot["commit"],
                  artifactDigest=snapshot["artifactDigest"],
                  verifiedFinish="HOLD")
    packet["fieldReceipt"]["osiFieldState"] = "UNVERIFIED"
    packet["humanAuthorityScope"] = {
        "state": "HOLD", "scope": "Owner-only H1 canonical research acceptance; real signed grant separate"}
    packet["progressProjectBinding"] = {
        "state": "HOLD_OFFICIAL_0_OF_40", "projectId": "ENGURU-HYM-AR-GE"}
    packet["suzgec"]["judgment"] = "HOLD"
    packet["suzgec"]["claim"] = "H1 source-prepared; no product/field acceptance"
    packet["testEvidence"] = [
        "PR #207 exact-head A03 preflight & H1 adversarial CI",
        "PR #207 A04 live pinned upstream bytes 13/13, actual CI required",
    ]
    packet["negativeEvidence"] = [
        "A03 issuer signer grant, independent PR review, A04 CVE/SBOM, E5 0/18",
        "OSi native field and DoneCheck Human Threshold held",
    ]
    packet["licenseSecurity"] = {
        "state": "HOLD_LICENSE_CVE_SBOM_CLEARANCE",
        "references": ["A04 pinned public upstream byte proof only"],
    }
    p = packet["projectPlan"]
    p.update(version="1", owner="engurulabory — single human owner; final human decision separate",
             goal="Hedef1 Mimarlık GitHub kaynak/test/simülasyon hazırlığı; A03+A04 özgün kapsam;",
             acceptance=[{
                 "CONTROL_ID": cid,
                 "REQUIREMENT": requirement,
                 "PASS_CONDITION": "Own canonical requirement accepted by authorized verifier",
                 "REQUIRED_EVIDENCE": "Real source/test/independent verification and approval as applicable",
                 "VERIFIER": "Existing GitHub tools, second-look and canonical DoneCheck",
                 "AUTHORITY": "ENGURU canonical owner and required independent reviewer",
                 "STATE": "HOLD"
             } for cid,requirement in H1_TASKS],
             refsDigest=snapshot["refsDigest"],
             dependencies=[{"id":cid,"requires":req} for cid,req in (
                 ("A01",[]),("A02",["A01"]),("A03",["A01","A02"]),
                 ("A04",["A01"]),("A05",["A04"]),("A06",["A05"]),
                 ("A07",["A03"]),("A08",["A02","A04"]),
                 ("A09",["A03","A04","A05","A06","A07","A08"]))],
             humanDecisionScope="One owner signs H1 A03/A04 exact task/source; field/acceptance separately gated",
             tools=["GitHub API + existing Actions", "Python 3.12 standard library", "Hybrid Project v1 source auditor"],
             steps=[
                 "Reconcile canonical V3, six blocks/40, and H1 A01-A09 exactly once",
                 "Complete source-backed A03 contract and A04 public upstream pin audit",
                 "Run 5 independent fixed GitHub-only design axes and negative cases",
                 "Reconcile exact checkout/PR HEAD, CI, source SHA256 and license/security HOLD",
                 "Offer only authenticated GitHub handoff; stop before Mac OSi activity",
             ],
             inventory={
                 "history":"Observed full git history and immutable commit; main drift separately reconciled",
                 "files":"Tracked source bytes SHA-256 and immutable research A03/A04 paths",
                 "branches":"Git ref digest; current PR review head vs latest main separately audited",
                 "githubRecords":"PR #207, Issue #205, real Actions run URLs; Git clone excludes comments",
                 "secrets":"Existing Mac OSi owner key stays local, excluded from GitHub and project manifest",
             },
             target={
                 "platform":"Mac OSi deferred, GitHub preparation only",
                 "path":"/ENGURU_HYM2_OWNER_APPROVED_DESTINATION_PENDING",
                 "collisionPolicy":"HOLD_PRESERVE_EXISTING",
                 "preserve":["Existing local OSi files","Mac Keychain + grants",
                             "GitHub main/PR audit records","DoneCheck ledger"],
             },
             budget={"purchasedCredits":0,"paidApi":0,"purchases":0,
                     "actionsBilling":"Public standard GitHub Actions; account consumption separately verifiable"},
             attempts=[], risks=[
                 "A03 real issuer/grant/reviewer authority HOLD",
                 "A04 7/7 source file identity != CVE/SBOM/license clearance",
                 "A05/A06 customer E5 0/18 and research-to-field boundaries",
             ],
             rollback={
                 "scope":"Only temporary H1 source audit workspaces; official GitHub/OSi remains protected",
                 "steps":"On drift, return HOLD and preserve source/owner files and previously verified artifacts",
                 "verification":"Re-read frozen Git refs, source byte digest, and hold all authority gates",
             })
    return packet


def main():
    try:
        data = build_plan()
        report = hybrid.simulate_project(data, ROOT)
        report.update(schema="enguru.hym2.h1.five-axis-github-source-audit/v1",
                      goal="HEDEF_1_MIMARLIK",
                      originalTaskCount=40, originalBlocks=6,
                      h1Tasks=[x[0] for x in H1_TASKS],
                      h1OfficialAccepted=0, all40OfficialAccepted=0,
                      a03RealSignedGrant="HOLD",
                      a04CveSbomAndLegal="HOLD",
                      independentReviewer="HOLD",
                      githubCiOutcome="SEPARATE_EXACT_HEAD_ACTIONS_REQUIRED",
                      osiField="NOT_EXECUTED", verifiedFinish="HOLD",
                      actualSourceCommit=data["sourceCommit"],
                      actualTrackedBytesSHA256=data["artifactDigest"])
        ok=(report["state"]=="PASS_GITHUB_PREPARATION_5X100"
            and report["scores"]=={k:100 for k in hybrid.FIVE_AXES}
            and report["gates"]["VERIFIED_FINISH"]=="HOLD"
            and report["sourceUnchanged"])
    except (OSError,ValueError,KeyError,TypeError) as exc:
        report={"state":"HOLD_H1_INPUT_OR_SOURCE","error_type":type(exc).__name__}
        ok=False
    print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2))
    return 0 if ok else 2


if __name__=="__main__":
    raise SystemExit(main())
