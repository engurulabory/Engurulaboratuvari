"""Zülfikar V1.3.1 explicit 10x10 acceptance-design verification.

PASS 100/100 describes *coverage of acceptance definitions*, not proof earned.
Official product and field require signed independent sources and Human Threshold.
"""
import copy
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXPECTED={"github":"G","osi":"O"}

def validate_contract(contract):
    if not isinstance(contract,dict) or contract.get("schema")!="enguru.harvest.zulfikar-v1.3.1-finish-gates/v1":
        return {"state":"HOLD_SCHEMA"}
    if (contract.get("owner")!="engurulabory" or contract.get("peer_review_required_for_github_technical") is not False or
            contract.get("issuer")!="EXISTING_CANONICAL_ONLY" or type(contract.get("osi_execution")) is not int or
            contract["osi_execution"]!=0 or type(contract.get("main_merge")) is not int or contract["main_merge"]!=0):
        return {"state":"HOLD_AUTHORITY"}
    out={}
    for scope,prefix in EXPECTED.items():
        stage=contract.get(scope)
        if not isinstance(stage,dict) or stage.get("state")!="HOLD":
            return {"state":"HOLD_SCOPE"}
        rows=stage.get("controls")
        if not isinstance(rows,list) or len(rows)!=10:
            return {"state":"HOLD_LENGTH"}
        for i,item in enumerate(rows,1):
            if not isinstance(item,dict) or item.get("id")!=f"{prefix}{i:02d}" or type(item.get("points")) is not int or item["points"]!=10:
                return {"state":"HOLD_ID_OR_POINTS"}
            for field in ("requirement","evidence","current"):
                if not isinstance(item.get(field),str) or not item[field].strip():
                    return {"state":"HOLD_REQUIRED_TEXT"}
            if item.get("approved") is not False or item.get("proof_sha256") is not None:
                return {"state":"HOLD_FORGED_ACCEPTANCE"}
        out[scope]={"target_definition":100,"definition_score":100,
                    "official_acceptance":"HOLD","approved_controls":0}
    if contract.get("acceptance_design_max")!=100:
        return {"state":"HOLD_MAX"}
    return {"state":"PASS_DEFINITION_ONLY","scopes":out}

def simulations(contract):
    # Three independent logical families, each 10 checks: identity, negative, finish
    identity=[]
    for scope,prefix in EXPECTED.items():
        identity.extend([len(contract[scope]["controls"])==10,
                         [r["id"] for r in contract[scope]["controls"]]==[f"{prefix}{i:02d}" for i in range(1,11)],
                         sum(r["points"] for r in contract[scope]["controls"])==100,
                         contract[scope]["state"]=="HOLD",
                         all(not r["approved"] for r in contract[scope]["controls"])])
    negatives=[]
    edits=[
        ("owner","other"),("issuer","FORGED"),
        ("main_merge",1),("osi_execution",1),("peer_review_required_for_github_technical",True),
    ]
    for key,bad in edits:
        sample=copy.deepcopy(contract)
        sample[key]=bad
        negatives.append(validate_contract(sample)["state"].startswith("HOLD"))
    for scope in EXPECTED:
        for bad in (True,"PASS"):
            sample=copy.deepcopy(contract)
            sample[scope]["controls"][0]["approved"]=bad
            negatives.append(validate_contract(sample)["state"]=="HOLD_FORGED_ACCEPTANCE")
        sample=copy.deepcopy(contract)
        sample[scope]["state"]="PASS"
        negatives.append(validate_contract(sample)["state"]=="HOLD_SCOPE")
    separation=[
        contract["github"]["state"]=="HOLD",
        contract["osi"]["state"]=="HOLD",
        contract["osi_execution"]==0,
        contract["main_merge"]==0,
        contract["owner"]=="engurulabory",
        contract["issuer"]=="EXISTING_CANONICAL_ONLY",
        contract["peer_review_required_for_github_technical"] is False,
        contract["acceptance_design_max"]==100,
        sum(x["approved"] is True for x in contract["github"]["controls"])==0,
        sum(x["approved"] is True for x in contract["osi"]["controls"])==0,
    ]
    suites={"SIM1_DEFINITION":identity,"SIM2_ADVERSARIAL":negatives,"SIM3_BOUNDARIES":separation}
    return {key:{"passed":sum(cases),"total":len(cases),
                  "state":"PASS_LOGICAL_ONLY" if all(cases) and len(cases)==10 else "HOLD"}
            for key,cases in suites.items()}

if __name__=="__main__":
    contract=json.loads((HERE/"ZULFIKAR_V131_100_GATE_CONTRACT.json").read_text(encoding="utf-8"))
    evaluated=validate_contract(contract)
    sims=simulations(contract)
    print(json.dumps({"design":evaluated,"logical_sims":sims,"official_verified_finish":"HOLD",
                      "osi_execution":0},ensure_ascii=False,sort_keys=True,indent=2))
    if evaluated["state"]!="PASS_DEFINITION_ONLY" or any(x["state"]!="PASS_LOGICAL_ONLY" for x in sims.values()):
        raise SystemExit(1)
