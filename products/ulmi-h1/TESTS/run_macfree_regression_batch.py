#!/usr/bin/env python3
"""Exact frozen-source, author-side macOS-independent reproducibility runner. Not independent DoneCheck."""
import subprocess,sys,time,json,hashlib,pathlib
root=pathlib.Path(__file__).resolve().parents[1];e=root/'EVIDENCE'/'W01_W11_FINAL';e.mkdir(parents=True,exist_ok=True)
suites=[
 'reconcile_v22_12_original_tasks.py',
 'run_v4_safe_rollback.py',
 'run_v4_http_rollback_e2e.py',
 'run_project_bound_e2e.py',
 'run_generated_taskboard_e2e.py',
 'run_final_e2e.py',
 'run_v5_uat_http_readiness.py',
 'run_v7_model_provenance_e2e.py',
 'run_v7_shared_ai_source_boundary.py',
 'run_v7_source_build_identity_e2e.py',
 'e09_independent_process_source_audit.py',
 'run_v22_http_framing_and_replay.py',
 'run_v7_w07_w08_real_http_and_restart.py',
 'test_w04_role_context_contract.py',
 'test_w04_archived_owner_source_bundle.py',
 'test_w04_nofollow_green.py',
 'test_w04_context_http_e2e.py',
 'run_w08_file_reader_race.py'
]
extra={
 'run_v22_http_framing_and_replay.py':['--product',str(root/'PRODUCT'),'--out',str(e/'v22_http_framing_replay.json')],
 'run_v7_w07_w08_real_http_and_restart.py':['--product',str(root/'PRODUCT'),'--output',str(e/'W07_W08_HTTP_RESTART.json')],
 'run_w08_file_reader_race.py':['--mode','green','--product',str(root/'PRODUCT')]
}
results=[]
for name in suites:
 start=time.time();cmd=[sys.executable,'-B',str(root/'TESTS'/name),*extra.get(name,[])]
 try:
  p=subprocess.run(cmd,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90,text=True)
  ok=p.returncode==0;log=p.stdout;exit_code=p.returncode
 except subprocess.TimeoutExpired as err:
  ok=False;log=(err.stdout or b'').decode('utf8','replace')+'\nTIMEOUT';exit_code='TIMEOUT'
 raw=log.encode('utf8');(e/(name+'.log')).write_bytes(raw)
 results.append({'suite':name,'pass':ok,'exit':exit_code,'seconds':round(time.time()-start,2),'log':'EVIDENCE/W01_W11_FINAL/'+name+'.log','log_sha256':hashlib.sha256(raw).hexdigest()})
 print(('PASS' if ok else 'HOLD'),name,'exit',exit_code,'s',round(time.time()-start,2),flush=True)

# Older source must reproduce its documented RED, without making a new product bug.
name='W08_PRE_RACE_REPRODUCIBLE_RED'
command=[sys.executable,'-B',str(root/'TESTS'/'run_w08_file_reader_race.py'),'--mode','red','--product',str(root/'ORIGINALS/W08_BEFORE_RACE_PRODUCT')]
p=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=12,text=True)
real_red=p.returncode==0 and 'W08_FIFO_REAL_BLOCK_RED=CONFIRMED' in p.stdout
raw=p.stdout.encode();(e/(name+'.log')).write_bytes(raw)
results.append({'suite':name,'pass':real_red,'exit':p.returncode,'seconds':None,'log':'EVIDENCE/W01_W11_FINAL/'+name+'.log','log_sha256':hashlib.sha256(raw).hexdigest(),'scope':'INTENTIONAL_OLD_SOURCE_RED_REPRODUCED'})
print(('PASS' if real_red else 'HOLD'),name,flush=True)
record={'schema':'enguru.ulmi.h1.v7-11-macfree-regression-batch/v2','suites':results,'pass':sum(i['pass'] for i in results),'total':len(results),'scope':'REAL_ISOLATED_AUTHOR_SIDE_NOT_OWNER_MAC_NOT_INDEPENDENT_DONECHECK','original_v22_full_closures_new':0}
(e/'BATCH_RESULT_FINAL.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('FINAL',record['pass'],'/',record['total'],flush=True)
if not all(x['pass'] for x in results):sys.exit(1)
