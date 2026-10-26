#!/usr/bin/env python3
"""HYM2 Hedef 1: reuse pinned Zülfikar V1.2 as a source-bound advisory gate.

No new core, issuer, second owner, PR merge, production work, or OSi writes.
The V1.2 9-hop, event and FIN oracles are *actually executed* against scoped
HYM2 observations; missing real evidence must produce HOLD, not simulation PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import types
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ORIGIN="engurulabory/Engurulaboratuvari"
Z_COMMIT="5b189e04b91dab4eb8099891188ca908f67bc816"
Z_ROOT="governance/enguru-suzgeci/zulfikar-v12/"
SOURCE_PINS={
    Z_ROOT+"zulfikar_v1_2_engine.py":"a5a20b8fedbd3e13ddd5fcc4eed8e59dc388bc61",
    Z_ROOT+"zulfikar_v1_2_design_contract.json":"632c2fa87063f16dcc44f02d68f577be9acabc5a",
}
BLOCKS=(
    tuple(f"A{i:02d}" for i in range(1,10)),
    tuple(f"B{i:02d}" for i in range(1,10)),
    ("C01","C02","C03","D01","D02","D03","D04"),
    ("C04","C05","C06","E01","E02","E03","E04"),
    ("F01","F02","F03","F04"),
    ("G01","G02","G03","G04"),
)
TASKS=tuple(x for block in BLOCKS for x in block)
V3_SHA="11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
MATRIX="governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_EVIDENCE_MATRIX_V424.json"
CASES="governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json"
PROVENANCE="governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_PROVENANCE_V425.json"
REAL_CI="https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40210177791"
CATEGORIES=("K01","K02","K03","K04")


def git_blob(body:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(body)).encode("ascii")+b"\0"+body).hexdigest()


def fetch_remote(path:str,timeout:float=20)->bytes:
    url="https://raw.githubusercontent.com/"+ORIGIN+"/"+Z_COMMIT+"/"+urllib.parse.quote(path)
    request=urllib.request.Request(url,headers={"User-Agent":"ENGURU-HYM2-ZULFIKAR-V12-pinned-reuse/1"})
    with urllib.request.urlopen(request,timeout=timeout) as reply:
        final=urllib.parse.urlparse(reply.geturl())
        if final.scheme!="https" or final.hostname!="raw.githubusercontent.com":
            raise ValueError("UNTRUSTED_ZULFIKAR_REDIRECT")
        data=reply.read(160_001)
    if not data or len(data)>160_000:
        raise ValueError("INVALID_ZULFIKAR_BYTES")
    return data


def read_zulfikar(fetch=fetch_remote,pins=SOURCE_PINS):
    if set(pins)!=set(SOURCE_PINS):
        raise ValueError("ZULFIKAR_SOURCE_SCOPE_CHANGED")
    data={}
    for path,expected in pins.items():
        body=fetch(path)
        if not isinstance(body,bytes) or git_blob(body)!=expected:
            raise ValueError("ZULFIKAR_SOURCE_BLOB_MISMATCH")
        data[path]=body
    contract=json.loads(data[Z_ROOT+"zulfikar_v1_2_design_contract.json"])
    if (contract.get("main_snapshot")!="8947cb6c240a12950be1f8be9e186d0ecbfa3022" or
        contract.get("scope")!="DESIGN_ONLY / LOCAL_OFFLINE_VALIDATOR" or
        contract.get("sha256_canonical_v3_lock")!=V3_SHA or
        set(contract.get("packages",{}))!=set(CATEGORIES) or
        set(contract.get("closure_ids",[]))!={
            "Z02_EVENT","Z03_TRANSFER","Z04_LINEAGE","Z05_BENCHMARK",
            "Z08_IMPACT","Z10_CONCURRENCY","Z10_SAFE_FIN"} or
        contract.get("new_core_created") is not False or
        contract.get("new_owner_created") is not False):
        raise ValueError("ZULFIKAR_CONTRACT_SCOPE_DRIFT")
    # Immutable, byte-verified source is executed in the GitHub CI runner;
    # only Zülfikar's existing pure policy oracle is reused.
    mod=types.ModuleType("verified_pinned_zulfikar_v12")
    exec(compile(data[Z_ROOT+"zulfikar_v1_2_engine.py"],Z_ROOT+"zulfikar_v1_2_engine.py","exec"),mod.__dict__)
    if (set(mod.CHECKS)!=set(contract["closure_ids"]) or
        mod.evaluate_design_coverage(contract,True)["provisional"]!=100):
        raise ValueError("ZULFIKAR_ORACLE_CONTRACT_DRIFT")
    return mod,contract,[{"path":p,"commit":Z_COMMIT,
                          "git_blob_sha1":pins[p],
                          "sha256":hashlib.sha256(v).hexdigest()} for p,v in data.items()]


def crosswalk():
    """Structural adapter; original A01–G04 controls keep their own authority."""
    work={}
    for task in TASKS:
        if task.startswith("A"):
            index=int(task[1:])
            modes={
                1:("K01","K02"),2:("K02",),3:("K02","K04"),
                4:("K02","K03"),5:("K01","K04"),6:("K02","K04"),
                7:("K03",),8:("K03","K04"),9:("K02","K04")}
            keys=modes[index]
        elif task.startswith("B"):keys=("K01","K03")
        elif task.startswith(("C","E")):keys=("K02","K04")
        elif task.startswith("D"):keys=("K02",)
        elif task.startswith("F"):keys=("K02","K04")
        else:keys=("K04",)
        work[task]={"zulfikar_advisory_packages":list(keys),
                    "real_task_acceptance":"HOLD",
                    "original_contract_authority":"UNCHANGED"}
    return work


def validate_hym_data(root:Path=ROOT):
    if (len(TASKS)!=40 or len(set(TASKS))!=40 or len(BLOCKS)!=6 or
        set(crosswalk())!=set(TASKS)):
        raise ValueError("ORIGINAL_40_OR_SIX_BLOCKS_CHANGED")
    v3=(root/"governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md").read_bytes()
    if hashlib.sha256(v3).hexdigest()!=V3_SHA:
        raise ValueError("V3_CANONICAL_BYTES_DRIFT")
    lock=json.loads((root/"governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json").read_text())
    if lock["sha256"]!=V3_SHA:
        raise ValueError("V3_LOCK_DRIFT")
    files={p:(root/p).read_bytes() for p in (MATRIX,CASES,PROVENANCE)}
    matrix=json.loads(files[MATRIX]);cases=json.loads(files[CASES]);pr=json.loads(files[PROVENANCE])
    if (matrix.get("block")!="BLOCK01" or set(matrix.get("tasks",{}))!=set(BLOCKS[0])
        or matrix.get("official_pass")!="0/9" or
        any(t.get("official")!="HOLD" or t.get("authority")!="HOLD" for t in matrix["tasks"].values())
        or cases.get("baseline",{}).get("rows")!=234
        or len(cases.get("cases",[]))!=18
        or cases.get("baseline",{}).get("all_18_e5_original_status")!="HOLD"
        or pr.get("acceptance")!="HOLD" or pr.get("osi")!="NOT_STARTED"
        or pr.get("a04_canonical_scope_boundary",{}).get("status")!="HOLD_OWNER_PRIVATE_CANONICAL_OR_EXPLICIT_RESEARCH_SCOPE"):
        raise ValueError("HYM_ORIGINAL_ACCEPTANCE_DRIFT")
    return files


def check_advisory(mod,files,work):
    """Never fabricate real nine-hop execution, real user results or owner sign."""
    digest=hashlib.sha256(files[MATRIX]).hexdigest()
    observation={"event_id":"HYM2-H1-A04-SOURCE-CI-READBACK",
        "task_id":"A04","owner":"engurulabory",
        "source_uri":"https://github.com/"+ORIGIN+"/pull/207",
        "provenance_digest":digest,"observed_at":"2026-10-25T16:10:00Z",
        "outcome":"PARTIAL","cause_status":"EVIDENCE_CONFIRMED",
        "cause_evidence_uri":REAL_CI,"promote_as_success":False}
    if mod.check_event(observation):
        raise ValueError("ZULFIKAR_EVENT_SCHEMA_REJECTED")
    stages=mod.CHAIN
    observed={
        "INTENT":"https://github.com/"+ORIGIN+"/issues/205",
        "GOAL":"https://github.com/"+ORIGIN+"/issues/205",
        "CONTRACT":MATRIX,
        "PLAN":"https://github.com/"+ORIGIN+"/issues/205",
        "SOURCE":PROVENANCE,
        "TEST":REAL_CI,
    }
    chain={"project_id":"ENGURU-HYM-AR-GE","target_sha":digest,
           "contract_controls":list(BLOCKS[0]),
           "contract_scope":"H1_SOURCE_RESEARCH_ONLY",
           "claim_scope":"H1_SOURCE_RESEARCH_ONLY",
           "chain":[{"stage":stage,"project_id":"ENGURU-HYM-AR-GE",
                     "source_sha":digest,"control_id":"A04",
                     "evidence_ref":observed.get(stage,"")}
                    for stage in stages]}
    errors=mod.check_lineage(chain)
    required={"CHAIN_EXECUTION_EVIDENCE_MISSING",
              "CHAIN_USER_OUTCOME_EVIDENCE_MISSING",
              "CHAIN_AUTHORITY_EVIDENCE_MISSING"}
    if not required.issubset(errors):
        raise ValueError("ZULFIKAR_REAL_CHAIN_MISSING_EVIDENCE_NOT_DETECTED")
    # Existing adviser remains read-only; missing K1-K7 and Human Threshold HOLD.
    fin={"k_gates":{},"unique_controls":True,"evidence_verified":False,
         "independent_review":False,"field_required":True,
         "field_evidence":False,"human_threshold_required":True,
         "human_authorization":False,"benchmark_claimed":False,
         "verified_finish_claim":False}
    fer=mod.check_fin(fin)
    if "FIN_K1_REMAINS_OPEN" not in fer or "FIN_HUMAN_DECISION_REQUIRED" not in fer:
        raise ValueError("ZULFIKAR_FAKE_FIN_NOT_BLOCKED")
    assessment=mod.assess({"Z02_EVENT":observation,"Z04_LINEAGE":chain,"Z10_SAFE_FIN":fin})
    if (assessment["state"]!="SIMULATED_HOLD" or
        assessment["official_verdict"]!="NOT_EVALUATED" or
        assessment["eligible_for_automatic_signature"] is not False):
        raise ValueError("ZULFIKAR_ILLEGAL_OFFICIAL_PASS")
    return {"event_schema":"PASS_OBSERVED_EVENT_SHAPE_ONLY",
            "lineage_state":"HOLD_THREE_REAL_HOPS",
            "unobserved_hops":["EXECUTION","USER_OUTCOME","AUTHORITY"],
            "fin_state":"HOLD_EXISTING_K1_K7_AND_OWNER",
            "assessment_state":assessment["state"],
            "checked_zulfikar_oracles":["Z02_EVENT","Z04_LINEAGE","Z10_SAFE_FIN"],
            "real_three_task_transfer":"HOLD_NOT_OBSERVED",
            "real_paired_peer_benchmark":"HOLD_NOT_MEASURED",
            "user_impact":"HOLD_NOT_OBSERVED",
            "owner_official_decision":"HOLD",
            "Zulfikar_oracle_holds":assessment["holds"]}


def review(root=ROOT,fetch=fetch_remote,pins=SOURCE_PINS):
    result={"schema":"enguru.hym2.zulfikar-v12-source-crosswalk/v1",
            "state":"HOLD","verified_finish":"HOLD","official_total":"0/40",
            "mac_osi_handoff":"HOLD","main_merge":"HOLD",
            "owner":"ONE_HUMAN_OWNER",
            "new_core":0,"new_issuer":0}
    try:
        files=validate_hym_data(root)
        mod,contract,pin_proofs=read_zulfikar(fetch,pins)
        work=crosswalk()
        gates=check_advisory(mod,files,work)
        result.update(
            state="PASS_PINNED_ZULFIKAR_ADVISORY_INTEGRATION_ONLY",
            zulfikar_source_commit=Z_COMMIT,
            zulfikar_source_pins=pin_proofs,
            source_file_sha256={p:hashlib.sha256(d).hexdigest() for p,d in files.items()},
            preservation={"portfolio_goals_preserved":9,
                          "portfolio_goal_names_verified_in_this_contract":False,
                          "original_task_count":40,"original_block_count":6,
                          "active_goal":"HEDEF_1_MIMARLIK","official_tasks":"0/40",
                          "official_h1":"0/9","independent_e5":"0/18",
                          "original_case_count":18,"original_criteria_cells":234},
            k01_k04_advisory_crosswalk=work,
            h1_zulfikar_live_advisory_checks=gates,
            zulfikar_design="100/100_CANDIDATE_ONLY",
            zulfikar_real_benchmark="HOLD",
            h1_a03="HOLD_REAL_OWNER_SCOPE_GRANT",
            h1_a04="HOLD_CANONICAL_KASIFI_OR_OWNER_RESEARCH_SCOPE",
            pr207_technical_preparation="PREVIOUS_EXACT_HEAD_CI_ONLY",
            pr242_technical_preparation="PREVIOUS_EXACT_HEAD_CI_ONLY",
            next_task="H1_A04_OWNER_PRIVATE_KASIFI_CANONICAL_OR_EXPLICIT_RESEARCH_ONLY_SCOPE_PROOF"
        )
    except (OSError,ValueError,KeyError,TypeError,UnicodeError) as exc:
        result["hold_reason"]=type(exc).__name__+":"+str(exc)[:160]
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--receipt",type=Path,required=True)
    args=p.parse_args()
    out=review()
    args.receipt.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"state":out["state"],"source_pins":len(out.get("zulfikar_source_pins",[])),
        "original_tasks":out.get("preservation",{}).get("original_task_count"),
        "actual_oracles":out.get("h1_zulfikar_live_advisory_checks",{}).get("checked_zulfikar_oracles"),
        "official_total":out["official_total"],"verified_finish":out["verified_finish"],
        "hold_reason":out.get("hold_reason")},sort_keys=True))
    return 0 if out["state"]=="PASS_PINNED_ZULFIKAR_ADVISORY_INTEGRATION_ONLY" else 2


if __name__=="__main__":
    raise SystemExit(main())
