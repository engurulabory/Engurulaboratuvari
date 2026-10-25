"""EMUS GH-04-C2 deterministic execution dependency lock, review only."""
from tools.emus_gap_matrix import evaluate

BLOCKS={"B1":list(range(1,6)),"B2":list(range(6,10)),
        "B3":list(range(10,14)),"B4":list(range(14,17)),"B5":list(range(17,20))}
def decision(progress):
    matrix=evaluate(progress)
    tasks={int(row["task_id"][3:]):row for row in matrix}
    result={}
    for block,ids in BLOCKS.items():
        pending=[tasks[i]["task_id"] for i in ids if tasks[i]["missing"]]
        result[block]={"state":"HOLD" if pending else "EVIDENCE_READY_REVIEW_REQUIRED",
                       "pending_tasks":pending}
    ready=all(result[b]["state"]=="EVIDENCE_READY_REVIEW_REQUIRED" for b in ("B1","B2","B3","B4"))
    return {"blocks":result,"osi_field":"GITHUB_PREPARATION_REVIEW_REQUIRED" if ready else "WAIT_GITHUB_READINESS",
            "official_accepted_tasks":progress["counting_rules"]["official_accepted_tasks"],
            "finish":"HOLD"}
