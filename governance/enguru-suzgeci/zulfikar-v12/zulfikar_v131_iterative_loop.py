#!/usr/bin/env python3
"""Zulfikar v1.3.1 iterative governance LOOP (not a second task executor).

Inject existing trusted assess / simulate / repair / test functions. This
controller runs the canonical sequence, keeps prior achievements, and proposes
stage review only when all checks and actual test-verifier checks succeed.
Real owner, Mac, DoneCheck and GitHub exact-head CI are OUTSIDE its authority.
"""
from __future__ import annotations
import copy
import hashlib
import json

PHASES=("GOAL_LOCK","ARCHITECTURE","SIMULATION","ASSESS","GAP_ANALYSIS",
        "REPAIR","REAL_TEST","RESIMULATION","REASSESS","EVIDENCE")
VALID_STAGES=frozenset(("GOAL_ARCHITECTURE","PREPARATION","REAL_EXECUTION","PRODUCT_FINISH"))
MAX_ROUNDS=12


def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode("utf8")).hexdigest()


def score(checks, expected_ids):
    """A valid result needs the exact original check IDs and actual booleans."""
    if (not isinstance(checks,dict) or set(checks)!=set(expected_ids) or
        any(type(v) is not bool for v in checks.values())):
        raise ValueError("CHECK_ID_OR_BOOLEAN_DRIFT")
    return sum(checks.values())*100//len(expected_ids)


def hold(reason,goal_hash,history):
    return {"schema":"enguru.zulfikar.v131-iterative-loop/v1",
      "decision":"CONTINUE_IMPROVEMENT" if reason=="ITERATION_LIMIT" else "AWAIT_REPAIR_OR_EVIDENCE",
      "holdReason":reason,"goalDigest":goal_hash,"history":history,
      "acceptedScore":None,"stagePassIssued":False,
      "officialVerifiedFinish":"AWAIT_AUTHORIZED_DONECHECK_HUMAN_THRESHOLD",
      "newTaskExecutorCreated":False}


def run(goal,state,assess,simulate,repair,real_test,verify_test,max_rounds=3):
    """Real tests/repairs are supplied by an existing AUTHORIZED operator.

    Returns stage 100 candidate rather than claiming a real authorized PASS.
    Bound iterations are one invocation; CONTINUE persists as a subsequent job.
    """
    if (not isinstance(goal,dict) or not isinstance(state,dict) or
        type(max_rounds) is not int or not 1<=max_rounds<=MAX_ROUNDS or
        goal.get("stage") not in VALID_STAGES or
        type(goal.get("targetScore")) is not int or goal["targetScore"]!=100 or
        not isinstance(goal.get("goalId"),str) or not goal["goalId"].strip() or
        not isinstance(goal.get("checkIds"),list) or not goal["checkIds"] or
        any(not isinstance(x,str) or not x.strip() for x in goal["checkIds"]) or
        len(set(goal["checkIds"]))!=len(goal["checkIds"]) or
        not all(callable(fn) for fn in (assess,simulate,repair,real_test,verify_test))):
        return hold("INVALID_GOAL_OR_HANDLERS",None,[])
    frozen_goal=copy.deepcopy(goal)
    frozen_goal_digest=digest(frozen_goal)
    ids=tuple(frozen_goal["checkIds"])
    current=copy.deepcopy(state)
    history=[]
    previous_verified=set()

    for iteration in range(1,max_rounds+1):
        try:
            if digest(goal)!=frozen_goal_digest:
                return hold("GOAL_IDENTITY_CHANGED",frozen_goal_digest,history)
            before_checks=assess(copy.deepcopy(current),copy.deepcopy(frozen_goal))
            before_score=score(before_checks,ids)
            prior_closed={key for key,v in before_checks.items() if v is True}
            if not previous_verified.issubset(prior_closed):
                return hold("PREVIOUS_ACHIEVEMENT_REGRESSION",frozen_goal_digest,history)
            simulation=simulate(copy.deepcopy(current),copy.deepcopy(frozen_goal))
            if not isinstance(simulation,dict) or simulation.get("status")!="PASS_SIMULATION":
                return hold("SIMULATION_FAILED",frozen_goal_digest,history)
            gaps=sorted(key for key,v in before_checks.items() if not v)
            entry={"round":iteration,"phases":list(PHASES),"goalDigest":frozen_goal_digest,
                   "before":{"diagnostic":before_score,"openChecks":gaps},
                   "simulation":{"status":simulation["status"]},"repairApplied":False,
                   "afterRealTest":None,"afterResimulation":None,"afterAssessment":None}
            if gaps:
                proposed=repair(copy.deepcopy(current),tuple(gaps),copy.deepcopy(frozen_goal))
                if not isinstance(proposed,dict) or proposed==current:
                    history.append(entry)
                    return hold("NO_AUTHORIZED_REPAIR_OR_PROGRESS",frozen_goal_digest,history)
                candidate=copy.deepcopy(proposed)
                entry["repairApplied"]=True
            else:
                candidate=copy.deepcopy(current)

            # Real test happens on the candidate, not a synthetic score claim.
            tested=real_test(copy.deepcopy(candidate),copy.deepcopy(frozen_goal))
            verified=verify_test(copy.deepcopy(candidate),copy.deepcopy(frozen_goal),tested)
            if (not isinstance(tested,dict) or tested.get("actualSubprocessObserved") is not True or
                tested.get("exitCode")!=0 or type(tested.get("exitCode")) is not int or
                verified is not True):
                history.append(entry)
                return hold("REAL_TEST_OR_INDEPENDENT_MECHANISM_FAILED",frozen_goal_digest,history)
            entry["afterRealTest"]={"mechanismVerified":True,"actualSubprocessObserved":True}

            again=simulate(copy.deepcopy(candidate),copy.deepcopy(frozen_goal))
            if not isinstance(again,dict) or again.get("status")!="PASS_SIMULATION":
                history.append(entry)
                return hold("RESIMULATION_FAILED",frozen_goal_digest,history)
            entry["afterResimulation"]={"status":"PASS_SIMULATION"}
            after_checks=assess(copy.deepcopy(candidate),copy.deepcopy(frozen_goal))
            after_score=score(after_checks,ids)
            after_closed={key for key,v in after_checks.items() if v is True}
            entry["afterAssessment"]={"diagnostic":after_score,
              "openChecks":sorted(key for key,v in after_checks.items() if not v)}
            if not prior_closed.issubset(after_closed) or after_score<before_score:
                history.append(entry)
                return hold("REGRESSION_AFTER_REPAIR",frozen_goal_digest,history)
            history.append(entry)
            current=candidate
            previous_verified=after_closed
            if not gaps and before_score==100 and after_score!=100:
                return hold("STAGE_REGRESSION",frozen_goal_digest,history)
            if after_score==100:
                # Authenticated CI and owner decision MUST be performed outside.
                return {"schema":"enguru.zulfikar.v131-iterative-loop/v1",
                  "decision":"STAGE_100_CANDIDATE_EXTERNAL_ACCEPTANCE_REQUIRED",
                  "stage":goal["stage"],"goalId":goal["goalId"],
                  "goalDigest":frozen_goal_digest,"diagnostic":100,
                  "history":history,"acceptedScore":None,"stagePassIssued":False,
                  "officialVerifiedFinish":"AWAIT_AUTHORIZED_DONECHECK_HUMAN_THRESHOLD",
                  "newTaskExecutorCreated":False}
        except (ValueError,TypeError,KeyError,OverflowError,RecursionError):
            return hold("INVALID_SOURCE_OR_OPERATOR_RESULT",frozen_goal_digest,history)
    return hold("ITERATION_LIMIT",frozen_goal_digest,history)
