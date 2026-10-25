#!/usr/bin/env python3
"""ENGURU Zulfikar v1.3 — executable, read-only goal/technical-infrastructure gates.

GITHUB_CODE score means actual checkout, source-pin, policy and subprocess
test coverage only. It NEVER represents a real Mac field score or a signer.
"""
from __future__ import annotations
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from zulfikar_v1_2_engine import CHECKS, assess, canonical_digest
from test_zulfikar_v1_2 import golden, MUTATIONS

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
V3 = REPO / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
LOCK = REPO / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json"
V3_PIN = "11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
GOAL_IDS = tuple(f"H{i:02d}" for i in range(1, 11))
CONTROL_IDS = tuple(f"C{i:02d}" for i in range(1, 11))
CONTROL_VERIFIERS = {f"C{i:02d}": f"goal_gate.H{i:02d}" for i in range(1, 11)}
CONTROL_AUTHORITIES = {id_: ("Human Threshold" if id_ in ("C04", "C10")
                            else "Independent reviewer") for id_ in CONTROL_IDS}
NEGATIVE_IDS = frozenset(("INVALID_GOAL", "MISSING_SOURCE",
                          "MISSING_AUTHORITY", "INCOMPLETE_DEPENDENCIES"))
INFRA_IDS = tuple(f"TA{i:02d}" for i in range(1, 11))
SRC = ("zulfikar_v1_2_engine.py","test_zulfikar_v1_2.py",
       "zulfikar_v1_2_five_gate.py","zulfikar_v1_3_gates.py",
       "test_zulfikar_v1_3_gates.py","ZULFIKAR_GOAL_V1_3.json")
HEX64 = re.compile(r"^[a-f0-9]{64}$")


def has_text(value, minimum=1):
    return isinstance(value, str) and len(value.strip()) >= minimum


def source_matches_checkout_head(repo_root: Path, source_paths) -> bool:
    """Compare actual bytes with immutable tracked blobs at this checkout HEAD.

    This is checkout integrity, not an independent reviewer or remote attestation.
    """
    try:
        if not (repo_root / ".git").exists():
            return False
        for source in source_paths:
            if not source.is_file() or source.is_symlink():
                return False
            rel = source.relative_to(repo_root).as_posix()
            recorded = subprocess.run(
                ["git", "-C", str(repo_root), "show", f"HEAD:{rel}"],
                capture_output=True, timeout=10,
            )
            if recorded.returncode != 0 or recorded.stdout != source.read_bytes():
                return False
        return True
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def score(checks):
    return {"score": sum(10 for ok in checks.values() if ok is True),
            "fixed_denominator": 100,
            "passed_ids": sorted(x for x, ok in checks.items() if ok is True),
            "open_ids": sorted(x for x, ok in checks.items() if ok is not True),
            "checks": checks}


def root_matches():
    try:
        data = json.loads(LOCK.read_text(encoding="utf8"))
        return (isinstance(data, dict)
                and hashlib.sha256(V3.read_bytes()).hexdigest() == V3_PIN
                and data.get("sha256") == V3_PIN)
    except (ValueError, OSError):
        return False


def dag_ok(edges, ids):
    if not isinstance(edges, dict) or set(edges) != ids:
        return False
    if any(not isinstance(v, list)
           or any(not isinstance(p, str) or p not in ids for p in v)
           or len(v) != len(set(v)) for v in edges.values()):
        return False
    seen, active = set(), set()
    def walk(x):
        if x in active: return False
        if x in seen: return True
        active.add(x)
        if any(not walk(p) for p in edges[x]): return False
        active.remove(x)
        seen.add(x)
        return True
    return all(walk(x) for x in ids)


def goal_gate(data):
    """10 fixed checks for goal contract SPECIFICATION, not observed success."""
    if not isinstance(data, dict): data = {}
    controls = data.get("controls", [])
    if not isinstance(controls, list): controls = []
    identities = [c.get("id") for c in controls if isinstance(c, dict)]
    valid_controls = len(controls) == 10 and len(identities) == 10 and (
        all(has_text(i) for i in identities) and set(identities) == set(CONTROL_IDS))
    rights = data.get("authority") if isinstance(data.get("authority"), dict) else {}
    budget = data.get("budget") if isinstance(data.get("budget"), dict) else {}
    metrics = data.get("measurement") if isinstance(data.get("measurement"), dict) else {}
    risks = data.get("risks") if isinstance(data.get("risks"), list) else []
    negatives = data.get("negative_cases") if isinstance(data.get("negative_cases"), list) else []
    canonical = data.get("canonical") if isinstance(data.get("canonical"), dict) else {}
    checks = {
      "H01": data.get("goal_id") == "ZULFIKAR-OPERATIONAL-GITHUB-V13" and has_text(data.get("single_goal"),30),
      "H02": has_text(data.get("user_value"),20) and all(has_text(metrics.get(k)) for k in ("metric","unit","baseline_source","target","observation")),
      "H03": valid_controls and all(
            has_text(c.get("acceptance"))
            and c.get("verifier") == CONTROL_VERIFIERS[c["id"]]
            and c.get("authority") == CONTROL_AUTHORITIES[c["id"]]
            for c in controls),
      "H04": rights.get("scope")=="SINGLE_GOAL" and rights.get("owner_review")=="HUMAN_THRESHOLD" and rights.get("issuer")=="EXISTING_CANONICAL_ONLY",
      "H05": valid_controls and dag_ok(data.get("dependencies"),set(identities)),
      "H06": len(risks)>=3 and all(isinstance(x,dict) and all(has_text(x.get(k)) for k in ("risk","mitigation","negative_test")) for x in risks),
      "H07": len(negatives)>=4 and all(isinstance(x,dict) and has_text(x.get("case_id")) and x.get("expected")=="HOLD" for x in negatives)
             and len({x["case_id"] for x in negatives}) == len(negatives)
             and NEGATIVE_IDS.issubset({x["case_id"] for x in negatives}),
      "H08": valid_controls and all(has_text(c.get("evidence_source")) and c.get("state")=="HOLD_PENDING_REAL_EVIDENCE" for c in controls),
      "H09": root_matches() and canonical.get("v3_sha256")==V3_PIN and canonical.get("repository")=="engurulabory/Engurulaboratuvari",
      "H10": data.get("core")=="REUSE_EXISTING" and data.get("rollback")=="REVERT_ISOLATED_BRANCH" and type(budget.get("paid_api")) is int and budget.get("paid_api")==0 and data.get("osi_field")=="HOLD",
    }
    result = score(checks)
    return {"phase":"GOAL","assessment":result,
            "verdict":"GOAL_SPECIFICATION_100_CANDIDATE" if result["score"]==100 else "HOLD_GOAL_SPECIFICATION",
            "actual_user_goal_success":"HOLD_NOT_OBSERVED","human_authority":"HOLD"}


def infra_gate():
    """10 code-infrastructure checks performed against actual checked-out bytes."""
    present = all((HERE/n).is_file() and not (HERE/n).is_symlink() for n in SRC)
    try: syntax = all(ast.parse((HERE/n).read_text(encoding="utf8")) is not None
                      for n in SRC if n.endswith(".py")) if present else False
    except (OSError,UnicodeError,SyntaxError): syntax=False
    digest = {n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in SRC} if present else {}
    fixture = golden()
    positive = len(CHECKS)==7 and all(fn(fixture[key])==[] for key,fn in CHECKS.items())
    negative=True
    for key,mut,_ in MUTATIONS:
        x=copy.deepcopy(fixture)
        try: mut(x[key]); outcome=assess(x)
        except (KeyError,TypeError,IndexError): negative=False;break
        if outcome["state"]!="SIMULATED_HOLD" or key not in outcome["holds"]:negative=False;break
    result=assess(fixture)
    rejected=assess({**fixture,"Z10_SAFE_FIN":{**fixture["Z10_SAFE_FIN"],"verified_finish_claim":True}})
    guard=(result["eligible_for_automatic_signature"] is False
           and result["official_verdict"]=="NOT_EVALUATED"
           and rejected["state"]=="SIMULATED_HOLD")
    tests=subprocess.run([sys.executable,"-B","-m","unittest","-q",
                           "test_zulfikar_v1_2","test_zulfikar_v1_3_gates"],
                          cwd=HERE,capture_output=True,text=True,timeout=90)
    test_ok=(tests.returncode==0 and "Ran " in tests.stderr and "OK" in tests.stderr)
    cmd=subprocess.run([sys.executable,"-B",str(HERE/"zulfikar_v1_3_gates.py"),"assess"],
                        cwd=HERE,input=json.dumps(fixture),capture_output=True,text=True,timeout=20)
    try: replay = json.loads(cmd.stdout)==result and cmd.returncode==0
    except ValueError: replay=False
    checks={
      "TA01":sys.version_info >= (3,12),
      "TA02":present,
      "TA03":root_matches(),
      "TA04":syntax,
      "TA05":len(digest)==len(SRC) and all(HEX64.fullmatch(d) for d in digest.values())
             and source_matches_checkout_head(REPO, tuple(HERE/n for n in SRC)),
      "TA06":positive,
      "TA07":len(MUTATIONS)==45 and negative,
      "TA08":guard and canonical_digest(result)==canonical_digest(assess(golden())),
      "TA09":test_ok,
      "TA10":replay,
    }
    evidence=score(checks)
    return {"phase":"INFRA_GITHUB_CODE","assessment":evidence,
            "verdict":"INFRA_GITHUB_CODE_100_CANDIDATE" if evidence["score"]==100 else "HOLD_INFRA_GITHUB_CODE",
            "source_sha256":digest,"python_unittest_exit_code":tests.returncode,
            "cli_roundtrip":replay,"github_exact_head_ci":"REQUIRES_EXTERNAL_GITHUB_CHECK",
            "osi_infrastructure":"HOLD_NOT_EXECUTED","official_finish":"HOLD"}


def main():
    p=argparse.ArgumentParser(description="Zulfikar read-only CLI: goal, infra, assess, status")
    p.add_argument("command",choices=("goal","infra","assess","status"))
    p.add_argument("--input")
    args=p.parse_args()
    try:
        if args.command=="goal":
            contract=json.loads(Path(args.input).read_text(encoding="utf8")) if args.input else json.loads((HERE/"ZULFIKAR_GOAL_V1_3.json").read_text(encoding="utf8"))
            result=goal_gate(contract)
            exit_code=0 if result["assessment"]["score"]==100 else 2
        elif args.command=="infra":
            result=infra_gate()
            exit_code=0 if result["assessment"]["score"]==100 else 2
        elif args.command=="assess":
            raw=Path(args.input).read_text(encoding="utf8") if args.input else sys.stdin.read(2000001)
            if len(raw)>2000000: raise ValueError("INPUT_TOO_LARGE")
            result=assess(json.loads(raw))
            exit_code=0 if result["state"]=="SIMULATED_DESIGN_READY_TO_REQUEST_REVIEW" else 2
        else:
            result={"state":"ZULFIKAR_V1_3_GITHUB_ADAPTER_AVAILABLE",
                    "goal":"GOAL_COMMAND_AVAILABLE","infrastructure":"INFRA_COMMAND_AVAILABLE",
                    "osi_field":"HOLD","official_finish":"HOLD"};exit_code=0
    except (ValueError,OSError,TypeError):
        result={"state":"HOLD_INVALID_INPUT","official_finish":"HOLD"};exit_code=2
    print(json.dumps(result,sort_keys=True,ensure_ascii=False,separators=(",",":")))
    raise SystemExit(exit_code)


if __name__=="__main__":main()
