"""EMUS GH-04-C1: deterministically expose all 19-task gap conditions from canonical review counter."""
import json
from pathlib import Path

def evaluate(progress):
    rows=progress["rows"]
    matrix=[]
    for row in rows:
        missing=[c["id"] for c in row["criteria"] if c["state"]=="HOLD_UNVERIFIED"]
        if len(row["criteria"])!=4:raise ValueError("FOUR_CRITERIA_REQUIRED")
        matrix.append({"task_id":f"GH-{row['id']:02d}","missing":missing,
                       "evidenced":4-len(missing),"acceptance":"HOLD"})
    if len(matrix)!=19:raise ValueError("ORIGINAL_19_REQUIRED")
    return matrix

def main():
    root=Path(__file__).resolve().parents[1]
    progress=json.loads((root/"governance/emus/EMUS_V11_SUBCRITERION_PROGRESS_V1.json").read_text())
    matrix=evaluate(progress)
    remaining=sum(len(x["missing"]) for x in matrix)
    if remaining!=76-progress["counting_rules"]["evidenced_total"]:
        raise ValueError("GAP_COUNT_DRIFT")
    print(json.dumps({"state":"PASS_GAP_MATRIX_CI_ONLY","tasks":len(matrix),
                      "unverified":remaining,"per_task":matrix},sort_keys=True))
if __name__=="__main__":main()
