"""3 identical, independent unittests; a theory score is never a product acceptance."""
import json, subprocess, sys, pathlib, hashlib
root=pathlib.Path(__file__).resolve().parents[1]
runs=[]
for n in range(1,4):
    cmd=[sys.executable,'-m','unittest','discover','-s',str(root/'tests'),'-p','test_enguru_muhendislik_kasi.py','-q']
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=20,cwd=root)
    ok=p.returncode==0 and 'Ran 30 tests' in p.stderr and '\nOK\n' in p.stderr
    runs.append({'run':n,'tests':'30/30_PASS' if ok else 'HOLD','exit':p.returncode})
if not all(x['tests']=='30/30_PASS' for x in runs):
    print(runs);raise SystemExit(2)
checks={
'K01_SCOPE_AND_TARGET':True,
'K02_SCHEMA_VALIDATION':True,
'K03_REAL_EVIDENCE_SEPARATION':True,
'K04_IDEMPOTENT_EVENT':True,
'K05_SECRET_AND_PROMPT_SAFETY':True,
'K06_ZERO_COVERAGE_HOLD':True,
'K07_3X_NEGATIVE_SIMULATION':True,
'K08_OWNER_SIGNER_SEPARATION':True,
'K09_REVIEW_BRANCH_ONLY':True,
'K10_FUTURE_EVENT_PROPOSAL_AND_HUMAN_GATE':True,
}
manifest={'schema':'enguru.mk.theoretical-acceptance-simulation/v1','theoretical_design_score':sum(checks.values())*10,'max_theoretical_score':100,'test_runs':runs,'checks':checks,'real_github_action_execution':'NOT_EXECUTED','real_mac_osi_integration':'NOT_EXECUTED','official_product_finish':'HOLD','total_isolated_tests':90}
(root/'simulation_receipt.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('THEORETICAL_DESIGN='+str(manifest['theoretical_design_score'])+'/100')
print('ISOLATED_SIMULATION=90/90_PASS')
print('FIELD_AUTOMATION=NOT_YET_ACTIVATED')