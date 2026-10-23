"""3 identical, independent unittests; a theory score is never a product acceptance."""
import json, subprocess, sys, pathlib, hashlib, re
root=pathlib.Path(__file__).resolve().parents[1]
runs=[]
for n in range(1,4):
    cmd=[sys.executable,'-m','unittest','discover','-s',str(root/'tests'),'-p','test_enguru_muhendislik_kasi.py','-q']
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=20,cwd=root)
    ok=p.returncode==0 and 'Ran 30 tests' in p.stderr and '\nOK\n' in p.stderr
    runs.append({'run':n,'tests':'30/30_PASS' if ok else 'HOLD','exit':p.returncode})
if not all(x['tests']=='30/30_PASS' for x in runs):
    print(runs);raise SystemExit(2)
core=(root/'tools/enguru_muhendislik_kasi.py').read_text(encoding='utf-8')
tests=(root/'tests/test_enguru_muhendislik_kasi.py').read_text(encoding='utf-8')
workflow=(root/'.github/workflows/enguru-muhendislik-kasi.yml').read_text(encoding='utf-8')
test_ids=set(re.findall(r'^\s+def (test_\d\d_[A-Za-z0-9_]+)\(',tests,flags=re.M))
def tested(*names):
    return all(name in test_ids for name in names)
checks={
 'K01_SCOPE_AND_TARGET': m_target in core if (m_target := 'ENGURU_MANAGEMENT_V69_PR_203') else False,
 'K02_SCHEMA_VALIDATION': tested('test_05_unknown_field','test_06_duplicate_json_keys','test_07_bad_sha'),
 'K03_REAL_EVIDENCE_SEPARATION': tested('test_08_no_evidence_no_pass','test_15_evidence_sha_valid','test_16_evidence_sha_invalid'),
 'K04_IDEMPOTENT_EVENT': tested('test_02_idempotent','test_03_conflict','test_27_replay_hash'),
 'K05_SECRET_AND_PROMPT_SAFETY': tested('test_11_secret_key','test_12_password_value','test_13_raw_html_escaped','test_26_no_automatic_code_execution'),
 'K06_ZERO_COVERAGE_HOLD': tested('test_09_zero_examined') and 'ZERO_COVERAGE_IS_NOT_ABSENCE_PROOF' in core,
 'K07_3X_NEGATIVE_SIMULATION': len(test_ids)==30 and len(runs)==3 and all(x['tests']=='30/30_PASS' for x in runs),
 'K08_OWNER_SIGNER_SEPARATION': tested('test_22_missing_authorized_actor','test_25_negative_not_owner_decision') and 'UNCHANGED_HOLD' in core,
 'K09_REVIEW_BRANCH_ONLY': 'ref: docs/enguru-osi-muhendislik-kasi-20261023' in workflow and 'git push origin HEAD:refs/heads/docs/enguru-osi-muhendislik-kasi-20261023' in workflow and 'ENGURU_MK_OWNER_LOGIN' in workflow,
 'K10_FUTURE_EVENT_PROPOSAL_AND_HUMAN_GATE': 'REVIEW_REQUIRED' in core and 'def add_event(' in core and 'def parse_event(' in core,
}

manifest={'schema':'enguru.mk.theoretical-acceptance-simulation/v1','theoretical_design_score':sum(checks.values())*10,'max_theoretical_score':100,'test_runs':runs,'checks':checks,'real_github_action_execution':'NOT_EXECUTED','real_mac_osi_integration':'NOT_EXECUTED','official_product_finish':'HOLD','total_isolated_tests':90}
(root/'simulation_receipt_verified_v2.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('THEORETICAL_DESIGN='+str(manifest['theoretical_design_score'])+'/100')
print('ISOLATED_SIMULATION=90/90_PASS')
print('FIELD_AUTOMATION=NOT_YET_ACTIVATED')