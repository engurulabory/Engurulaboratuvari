#!/usr/bin/env python3
"""Separate three-mode falsification of ENGURU 48-control semantic peer audit.

A second software mechanism checks provenance and explicitly human-audited labels.
It cannot independently prove semantic truth or substitute for authorized reviewers.
"""
from __future__ import annotations
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"governance/enguru-suzgeci/ENGURU_D48_SEMANTIK_KARSIT_INCELEME_V1.json"
MATRIX=ROOT/"governance/enguru-suzgeci/ENGURU_TASARIM_48_KONTROL_MATRISI_V1.json"
IDS=[f"D{x:02}" for x in range(1,49)]
WEAK={"D02","D08","D10","D12","D16","D18","D40","D42","D45"}
LIMITED={"D01","D03","D05","D09","D13","D15","D19","D26","D27","D28",
         "D32","D35","D36","D37","D39","D44","D46","D47","D11","D22","D23","D24"}
BOUNDARY={
 "EVIDENCE_NOT_EQUIVALENT":"REQUIRE_ENGURU_SPECIFIC_PROOF",
 "LIMITED_ANALOGY":"CONCEPTUAL_TRANSFER_NOT_NORMATIVE",
 "MECHANISM_ALIGNED":"MECHANISM_ONLY_NO_FIELD_CERTIFICATION",
}
SOURCES={"NIST_AI_RMF","DORA","SLSA","GOOGLE_SRE","NIST_SSDF",
         "ANTHROPIC_EVALS","OPENSSF","LANGGRAPH"}

def expected_class(control_id):
    return ("EVIDENCE_NOT_EQUIVALENT" if control_id in WEAK else
            "LIMITED_ANALOGY" if control_id in LIMITED else "MECHANISM_ALIGNED")

def check(matrix,review):
    if not isinstance(review,dict) or not isinstance(review.get("rows"),list):
        return False
    rows=review["rows"]
    controls=matrix["controls"]
    if (len(rows)!=48 or len(controls)!=48 or
        [x.get("control_id") for x in rows]!=IDS or
        [x.get("id") for x in controls]!=IDS or
        review.get("scope")!="DESKTOP_AI_SOURCE_SEMANTIC_AUDIT_NO_SEPARATE_HUMAN_REVIEW" or
        review.get("status")!="AI_SEMANTIC_SECOND_LOOK_COMPLETED_HUMAN_AUTHORITY_HOLD" or
        set(review.get("watchlist",[]))!=WEAK or
        len(review.get("references",[]))!=8):
        return False
    references={x.get("source_id"):x for x in review["references"]}
    if set(references)!=SOURCES or any(len(x.get("verified_scope",""))<20 for x in references.values()):
        return False
    counts={x:0 for x in BOUNDARY}
    for item,control in zip(rows,controls):
        label=expected_class(item["control_id"])
        peer=control["peer_evidence"]
        if (item.get("criterion")!=control["criterion"] or
            item.get("source_id")!=peer["source_id"] or
            item.get("source_url")!=peer["url"] or
            item.get("original_mechanism")!=peer["mechanism"] or
            references[peer["source_id"]]["url"]!=peer["url"] or
            item.get("classification")!=label or
            item.get("claim_boundary")!=BOUNDARY[label] or
            item.get("reviewed_by")!="AI_SOURCE_SECOND_LOOK_NOT_INDEPENDENT_HUMAN" or
            len(item.get("note",""))<37 or
            any(y in item["note"] for y in (
                "OFFICIAL_PASS", "HUMAN_APPROVED", "CERTIFIED_COMPLIANT")) or
            set(item)!={"control_id","criterion","source_id","source_url",
                         "original_mechanism","classification","note",
                         "claim_boundary","reviewed_by"}):
            return False
        counts[label]+=1
    return counts==review.get("counts") and sum(counts.values())==48

def attack(matrix,original,mode,index,variant):
    bad=copy.deepcopy(original)
    row=bad["rows"][index]
    if mode=="SOURCE":
        if variant==0:
            row["source_id"]="UNVERIFIED_VENDOR"
        elif variant==1:
            row["source_url"]="https://evidence.example/not-source"
        else:
            row["original_mechanism"]="FAKE_MECHANISM_CLAIM"
    elif mode=="SEMANTIC":
        if variant==0:
            row["classification"]="MECHANISM_ALIGNED" if expected_class(row["control_id"])!="MECHANISM_ALIGNED" else "EVIDENCE_NOT_EQUIVALENT"
        elif variant==1:
            row["claim_boundary"]="NORMATIVE_CERTIFIED_PASS"
        else:
            row["note"]=""
    elif mode=="AUTHORITY":
        if variant==0:
            row["control_id"]="D01" if index else "D48"
        elif variant==1:
            row["reviewed_by"]="INDEPENDENT_HUMAN_REVIEWER_APPROVED"
        else:
            row["claim_state"]="OFFICIAL_PASS"
    else:
        raise ValueError("invalid mode")
    return bad

def main(mode):
    if mode not in ("SOURCE","SEMANTIC","AUTHORITY"):
        raise ValueError("HOLD_UNKNOWN_TEST_MODE")
    rb=AUDIT.read_bytes()
    mb=MATRIX.read_bytes()
    review=json.loads(rb)
    matrix=json.loads(mb)
    baseline=check(matrix,review)
    false_pass=[]
    attempts=0
    for i in range(48):
        for v in range(3):
            attempts+=1
            if check(matrix,attack(matrix,review,mode,i,v)):
                false_pass.append(f"{mode}:D{i+1:02}:{v}")
    # Independent probe: tampered underlying matrix must invalidate unchanged review.
    if mode=="SOURCE":
        for i in range(48):
            attempts+=1
            damaged=copy.deepcopy(matrix)
            damaged["controls"][i]["peer_evidence"]["url"]="https://fake.example"
            if check(damaged,review):
                false_pass.append(f"MATRIX_PEER_DRIFT:D{i+1:02}")
    if mode=="SEMANTIC":
        for id in sorted(WEAK):
            attempts+=1
            bad=copy.deepcopy(review)
            entry=bad["rows"][int(id[1:])-1]
            entry["classification"]="MECHANISM_ALIGNED"
            entry["claim_boundary"]=BOUNDARY["MECHANISM_ALIGNED"]
            if check(matrix,bad):
                false_pass.append(f"UNSUPPORTED_DIRECT_PROOF:{id}")
    if mode=="AUTHORITY":
        for i in range(48):
            attempts+=1
            bad=copy.deepcopy(review)
            bad["rows"][i]["reviewed_by"]="HUMAN_APPROVED"
            if check(matrix,bad):
                false_pass.append(f"FORGED_HUMAN_CLAIM:D{i+1:02}")
    counts=review["counts"]
    success=baseline and not false_pass and counts=={
        "MECHANISM_ALIGNED":17,
        "LIMITED_ANALOGY":22,
        "EVIDENCE_NOT_EQUIVALENT":9,
    }
    receipt={
        "schema":"enguru.method.semantic-mutation-three-mode/v1",
        "mode":mode,"verdict":"PASS_SEMANTIC_SCOPE_TEST" if success else "HOLD_FALSE_PASS",
        "baseline_audit":baseline,"control_count":48,
        "source_count":8,"classifications":counts,
        "mutation_attempts":attempts,"caught":attempts-len(false_pass),
        "false_pass":false_pass,
        "source_matrix_sha256":hashlib.sha256(mb).hexdigest(),
        "semantic_review_sha256":hashlib.sha256(rb).hexdigest(),
        "independent_human_review":"HOLD",
        "real_product_saha":"HOLD","official_donecheck":"HOLD",
        "verified_finish":"HOLD"}
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2))
    return 0 if success else 2

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: checker SOURCE|SEMANTIC|AUTHORITY")
    raise SystemExit(main(sys.argv[1]))
