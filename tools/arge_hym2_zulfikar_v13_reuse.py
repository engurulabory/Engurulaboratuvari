#!/usr/bin/env python3
"""HYM2: actually execute pinned Zülfikar V1.3 GOAL and INFRA in an isolated checkout.

V1.3 has its own user goal and cannot change the HYM2 acceptance rubric or
V4.7 historical 50/100 by implication. Immutable upstream Git blob identity
is checked before writing into a throwaway temp directory. There are no
GitHub main, product, OSi, credential, customer or ledger writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

REPO="engurulabory/Engurulaboratuvari"
Z13_HEAD="5720cd0de67f959d44ea8ace42a3a716753077f1"
PREFIX="governance/enguru-suzgeci/zulfikar-v12/"
FILES={
 "zulfikar_v1_2_engine.py":"a5a20b8fedbd3e13ddd5fcc4eed8e59dc388bc61",
 "test_zulfikar_v1_2.py":"a11f5c451e5566cd9a22a7bb605466118143907f",
 "zulfikar_v1_2_five_gate.py":"b5c28b388870dc4ec3cdb6d51ea340f6d5472391",
 "zulfikar_v1_3_gates.py":"d2722d3965cd74e24675867e4436d2929eba582f",
 "test_zulfikar_v1_3_gates.py":"12c82bea34e6a179e4cd90728c36c4d9353b5433",
 "ZULFIKAR_GOAL_V1_3.json":"bc53e003f19cb59ef9413bcf6ef21580220f8481",
}
V3_PATH="governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
V3_LOCK="governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json"
PIN_V3="11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
RECONCILE="governance/enguru-suzgeci/reviews/ENGURU_ARGE_B01_M01_GITHUB_PREP_GATE_RECONCILIATION_V1.json"
H1_MATRIX="governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_EVIDENCE_MATRIX_V424.json"
MAX_BYTES=100000


def blob_hash(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def fetch(filename,timeout=22):
    if filename not in FILES:
        raise ValueError("UNPINNED_SOURCE_NAME")
    url="https://raw.githubusercontent.com/"+REPO+"/"+Z13_HEAD+"/"+urllib.parse.quote(PREFIX+filename)
    req=urllib.request.Request(url,headers={"User-Agent":"ENGURU-HYM2-ZULFIKAR-V13-EXACT-PIN/1"})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        p=urllib.parse.urlparse(response.geturl())
        if p.scheme!="https" or p.hostname!="raw.githubusercontent.com":
            raise ValueError("BAD_SOURCE_REDIRECT")
        result=response.read(MAX_BYTES+1)
    if not result or len(result)>MAX_BYTES:
        raise ValueError("SOURCE_BYTES_BUDGET")
    return result


def verify_source(fetcher=fetch):
    if len(FILES)!=6:
        raise ValueError("SOURCE_PIN_SET_DRIFT")
    result={}
    for name,sha1 in FILES.items():
        raw=fetcher(name)
        if not isinstance(raw,bytes) or not raw or len(raw)>MAX_BYTES:
            raise ValueError("SOURCE_INVALID:"+name)
        if blob_hash(raw)!=sha1:
            raise ValueError("SOURCE_PIN_MISMATCH:"+name)
        result[name]=raw
    return result


def read_canonical(root):
    v3=(root/V3_PATH).read_bytes()
    lock=json.loads((root/V3_LOCK).read_text(encoding="utf8"))
    h=hashlib.sha256(v3).hexdigest()
    if h!=PIN_V3 or lock.get("sha256")!=PIN_V3:
        raise ValueError("CANONICAL_V3_DRIFT")
    h1=json.loads((root/H1_MATRIX).read_text(encoding="utf8"))
    gate=json.loads((root/RECONCILE).read_text(encoding="utf8"))
    if (h1.get("official_pass")!="0/9" or
        len(h1.get("tasks",{}))!=9 or
        gate.get("score_accounting",{}).get("github_preparation_last_authoritative_record")!="50/100" or
        "NOT a replacement authoritative 5/10 measurement" not in
        gate.get("score_accounting",{}).get("proposed_gate_register","")):
        raise ValueError("HYM2_ORIGINAL_RUBRIC_OR_AUTHORITY_DRIFT")
    return v3,(root/V3_LOCK).read_bytes()


def evaluate(root,fetcher=fetch,runner=subprocess.run):
    receipt={
        "schema":"enguru.hym2.zulfikar-v13-exact-pinned-reuse/v1",
        "state":"HOLD","owner":"ONE_HUMAN_OWNER","original_40_official":"0/40",
        "original_V47_github_readiness":"50/100_HOLD",
        "hym2_goal_design_theory":"SEPARATE_PRIOR_CI_EVIDENCE",
        "hym2_five_by_100":"SEPARATE_EXACT_PR_HEAD_CI",
        "osi_handoff":"HOLD","product_acceptance":"HOLD","verified_finish":"HOLD",
        "new_core":0,"product_code_writes":0,"main_writes":0
    }
    try:
        files=verify_source(fetcher)
        v3,lock=read_canonical(root)
        with tempfile.TemporaryDirectory(prefix="hym2-zulfikar-v13-") as tmp:
            base=pathlib.Path(tmp)
            src=base/PREFIX
            src.mkdir(parents=True)
            for name,contents in files.items():
                (src/name).write_bytes(contents)
            for name,contents in ((V3_PATH,v3),(V3_LOCK,lock)):
                p=base/name;p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(contents)
            results={}
            for command in ("goal","infra","status"):
                process=runner(
                    [sys.executable,"-B",str(src/"zulfikar_v1_3_gates.py"),command],
                    cwd=src,capture_output=True,text=True,timeout=150)
                if process.returncode!=0:
                    raise ValueError("Z13_COMMAND_FAILED:"+command+":"+process.stderr[-80:])
                results[command]=json.loads(process.stdout)
            goal=results["goal"]; infra=results["infra"];status=results["status"]
            if (goal.get("verdict")!="GOAL_SPECIFICATION_100_CANDIDATE" or
                goal.get("assessment",{}).get("score")!=100 or
                len(goal["assessment"].get("passed_ids",[]))!=10 or
                goal.get("actual_user_goal_success")!="HOLD_NOT_OBSERVED" or
                goal.get("human_authority")!="HOLD"):
                raise ValueError("GOAL_SCOPE_OR_SCORE_MISMATCH")
            if (infra.get("verdict")!="INFRA_GITHUB_CODE_100_CANDIDATE" or
                infra.get("assessment",{}).get("score")!=100 or
                len(infra["assessment"].get("passed_ids",[]))!=10 or
                infra.get("python_unittest_exit_code")!=0 or
                infra.get("cli_roundtrip") is not True or
                infra.get("osi_infrastructure")!="HOLD_NOT_EXECUTED" or
                infra.get("official_finish")!="HOLD"):
                raise ValueError("INFRA_SCOPE_OR_SCORE_MISMATCH")
            if status.get("official_finish")!="HOLD" or status.get("osi_field")!="HOLD":
                raise ValueError("Z13_EARLY_FINISH")
        receipt.update({
            "state":"PASS_Z13_PINNED_OPERATIONAL_ADAPTER_ONLY",
            "zulfikar_V13_commit":Z13_HEAD,
            "source_blob_count":len(files),
            "verified_byte_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},
            "z13_goal_specification":goal["assessment"]["score"],
            "z13_infra_github_code":infra["assessment"]["score"],
            "z13_negative_tests":"RAN_V13_SUBPROCESS_TESTS",
            "z13_canonical_method":"REUSES_V12_ENGINE_AND_ORIGINAL_ENGURU_V3",
            "verified_stage_separation":"PASS_100_GOAL_100_INFRA_VS_HYM2_ORIGINAL_V47_50",
            "next":"LOCATE_V47_ORIGINAL_RUBRIC_THEN_CLOSE_ACTUAL_SOURCE_PREPARATION_GAPS",
        })
    except (OSError,ValueError,KeyError,TypeError,UnicodeError,subprocess.TimeoutExpired,
            json.JSONDecodeError) as e:
        receipt["hold_reason"]=type(e).__name__+":"+str(e)[:180]
    return receipt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=pathlib.Path,required=True)
    a=ap.parse_args()
    result=evaluate(pathlib.Path(__file__).resolve().parents[1])
    a.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:result.get(k) for k in
                     ("state","source_blob_count","z13_goal_specification",
                      "z13_infra_github_code","original_V47_github_readiness",
                      "original_40_official","hold_reason")},sort_keys=True))
    return 0 if result["state"]=="PASS_Z13_PINNED_OPERATIONAL_ADAPTER_ONLY" else 2


if __name__=="__main__":
    raise SystemExit(main())
