"""Bounded, pure Süzgeç v2.4 eight-stage decision evaluator (candidate; no native grants)."""
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1]/"governance/work-protocol/ENGURU_SUZGEC_V24_LANGUAGE_ALIGNMENT_CONTRACT_V1.json"
REQUIRED=("goal_id","goal_statement","scope_version","owner")
CRITERION=("criterion_id","evidence_requirement","pass_threshold","verifier","authority_requirement")

def decide(work):
    out={"state":"HOLD_GUVENLI_DUR","verifiedFinish":"HOLD","next_stage":"01","blockers":[],"authority":"NATIVE_OSi_ONLY"}
    try:
        c=json.loads(CONTRACT.read_text(encoding="utf-8"))
        rule=c["eightStageGoalAcceptanceLoop"]
        if len(c["eightStages"])!=8 or c["existingFinishGates"]!=["T01","T02","T03","T04"] or not all(rule[k] for k in ("noNinthStage","noNewCore","noNewGate")):
            raise ValueError("CANONICAL_STAGE_OR_GATE_DRIFT")
        if not isinstance(work,dict) or any(not isinstance(work.get(k),str) or not work[k].strip() for k in REQUIRED):
            raise ValueError("GOAL_LOCK_INCOMPLETE")
        out["next_stage"]="03"
        items=work.get("criteria")
        if not isinstance(items,list) or not items:
            raise ValueError("ACCEPTANCE_EMPTY")
        ids=set()
        for item in items:
            if not isinstance(item,dict) or any(not isinstance(item.get(k),str) or not item[k].strip() for k in CRITERION):
                raise ValueError("ACCEPTANCE_CRITERION_INCOMPLETE")
            if item["criterion_id"] in ids: raise ValueError("DUPLICATE_CRITERION")
            ids.add(item["criterion_id"])
        if work.get("acceptance_locked") is not True:
            raise ValueError("ACCEPTANCE_NOT_LOCKED")
        out["next_stage"]="06"
        if any(item.get("result")!="PASS" or item.get("evidence_verified") is not True for item in items):
            raise ValueError("CRITERION_NOT_VERIFIED")
        if work.get("source_verified") is not True or work.get("value_preserved") is not True or work.get("negative_simulation_verified") is not True:
            raise ValueError("SOURCE_PRESERVATION_OR_SIMULATION_HOLD")
        if work.get("existing_finish_gates")!={"T01":"PASS","T02":"PASS","T03":"PASS","T04":"PASS"}:
            raise ValueError("EXISTING_GATES_HOLD")
        if work.get("authenticated_human_threshold") is not True or work.get("native_verified_finish") is not True:
            raise ValueError("NATIVE_FINISH_AUTHORITY_HOLD")
        if work.get("field_provenance_verified") is not True:
            raise ValueError("FIELD_PROVENANCE_HOLD")
        # A local JSON declaration is NOT authenticated OSi evidence. This candidate
        # has no native verifier and never returns official BITTI_DUR.
        out["state"]="PASS_STATIC_FINISH_PREDICATES_ONLY"
        out["next_stage"]="08"
        out["blockers"]=["NATIVE_OSi_VERIFIER_NOT_INTEGRATED"]
    except (ValueError,TypeError,KeyError,OSError) as e:
        out["blockers"].append(str(e))
    if out["state"]=="HOLD_GUVENLI_DUR":
        try:
            tries=work.get("retry_count",0) if isinstance(work,dict) else 0
            limit=work.get("retry_limit",0) if isinstance(work,dict) else 0
            if not isinstance(tries,int) or isinstance(tries,bool) or not isinstance(limit,int) or isinstance(limit,bool) or tries<0 or limit<0 or tries>=limit:
                out["next_action"]="STOP_AND_ASSIGN_BLOCKER_OWNER"
            else:
                out["next_action"]="REENTER_EXISTING_STAGE_WITHIN_SAME_LOCKED_SCOPE"
        except (TypeError,AttributeError):
            out["next_action"]="STOP_AND_ASSIGN_BLOCKER_OWNER"
    return out
