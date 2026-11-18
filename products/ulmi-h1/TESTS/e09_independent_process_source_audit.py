#!/usr/bin/env python3
"""Separate-process author-controlled source audit, NOT independent signed DoneCheck."""
import json,hashlib,re,ast,subprocess,sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'PRODUCT';OR=ROOT/'ORIGINALS';E=ROOT/'EVIDENCE';Q=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(name,condition):
 ok=bool(condition);Q.append({'check':name,'pass':ok});print(('PASS' if ok else 'FAIL'),name,flush=True)
 if not ok:raise AssertionError(name)
verify('original_V22_byte_SHA',sha(OR/'V22_IMMUTABLE_SOURCE.json')=='069c03b0f299e76ef46e26a25eb4284474ae5219353185a88386ee5df9f39304')
verify('original_pilot_ABC_byte_SHA',sha(OR/'PILOT_ABC_IMMUTABLE_SOURCE.json')=='5beb10d407dc550d7f979062fef6bdcfd451791103d5b02fc1c2d05a1786d79b')
orders=sorted((ROOT/'EMIRLER').glob('E0*_*.md'))
verify('9_original_v11_order_documents',len(orders)==9)
for i,o in enumerate(orders,1):verify('order_document_'+str(i),f'E0{i}' in o.name and 'HOLD' in o.read_text())
html=(P/'index.html').read_text();js=(P/'app.js').read_text();server=(P/'server.py').read_text();soup=BeautifulSoup(html,'html.parser');ids={x.get('id') for x in soup.select('[id]')}
jsids=set(re.findall(r"\$\('([a-z-]+)'\)",js))
verify('all_app_JS_IDs_exist_in_HTML',not (jsids-ids))
verify('HTML_has_samedomain_assets',soup.select_one('script[src="/app.js"]') is not None and soup.select_one('link[href="/style.css"]') is not None)
verify('seven_cards_including_unverified_qwen',set(x.get('data-kind') for x in soup.select('[data-kind]'))=={'python','html','taskboard','projectboard','diagnostic','repair','qwen_plan'})
verify('V7_QWEN_RESEARCH_ROUTE_PROVENANCE', 'qwen-prompt' in ids and 'model-route-evidence' in ids and "selectedKind==='qwen_plan'" in js and 'HOLD_OLLAMA_REPORTED_MODEL' in server)
verify('V3_project_selection_option_carries_SHA', 'o.dataset.sha=p.sha256' in js)
verify('V3_project_board_real_API', '/api/desk/project-board/plan' in server and 'project_board_plan(payload)' in server)
verify('V3_project_board_user_UI', 'choice-projectboard' in ids and "selectedKind==='projectboard'" in js)
verify('V3_project_before_execute_recheck', 'verify_project_board_task(row,data)' in server and 'HOLD_SCOPED_TEMPLATE_SOURCE_MISMATCH' in server)
verify('V3_exact_template_SHA_PIN', 'TASKBOARD_TEMPLATE_PIN' in server and 'HOLD_TRUSTED_TASKBOARD_TEMPLATE_SOURCE_SHA' in server)
verify('V3_project_real_49_checks', json.loads((E/'V3_PROJECT_BOUND_E2E_RECEIPT.json').read_text())['passed']==49)
verify('generated_taskboard_reviewed_fixture',"TASKBOARD_FIXTURE = (BASE / 'taskboard_template.py').read_text('utf-8')" in server and 'trusted_taskboard' in server)
verify('taskboard_source_Python_AST',ast.parse((P/'taskboard_template.py').read_text()) is not None)
verify('E05_search_and_status_UI',all(x in ids for x in ['task-search','task-status-filter','task-search-button']))
verify('E05_SQLite_parameterization','instr(lower(path),lower(?))' in server and 'HOLD_STATUS_FILTER' in server)
verify('E06_safe_file_no_stale_receipt','HOLD_OUTPUT_INTEGRITY' in server and 'HOLD_UNRECEIPTED_FILE' in server)
verify('E06_real_bounded_source_repair',all(x in server for x in ['restricted_python_syntax_repair','PASS_SCOPED_STATIC','HOLD_SOURCE_ALREADY_PARSES']))
verify('E04_preserves_existing_single_executor',server.count('def execute(')==1 and 'ThreadingHTTPServer' in server and 'db_conn' in server)
verify('nine_H00_H08_map_IDs',set(x['id'] for x in json.loads((P/'maps/map_index.json').read_text())['maps'])=={'H0'+str(i) for i in range(9)})
verify('maps_present_in_UI','id="haritalar"' in html and 'refreshMaps()' in js)
verify('client_receipt_requires_fresh_verify',"const verified=liveVerify?.match===true" in js)
verify('safe_bound_localhost_default',"HOST = '127.0.0.1'" in server)
verify('preserve_H2_PARKED','PARKED_MAC' in server)
verify('JS_node_syntax',subprocess.run(['node','--check',str(P/'app.js')],capture_output=True).returncode==0)
verify('Python_source_AST_parses',ast.parse(server) is not None)
receipt=json.loads((E/'E05_E06_E07_REAL_E2E_TEST_RECEIPT.json').read_text());verify('actual_disposable_real_http_49_checks',receipt['passed']==receipt['total']==49)
generated=json.loads((E/'E04_E09_TASKBOARD_REAL_E2E_RECEIPT.json').read_text());verify('new_real_generated_taskboard_44_checks',generated['passed']==generated['total']==44)
verify('three_REAL_distinct_HTTP_runs',len(receipt['runs'])==3 and all(x['pass'] for x in receipt['runs']))
red=(E/'E06_REAL_RED.log').read_text();verify('historical_RED_reproduced','RED_REPRODUCED' in red)
browser=json.loads((E/'E08_REAL_BROWSER_POLICY_AND_UAT_BOUNDARY.json').read_text());verify('real_browser_truth_boundary',browser['chromium_attempted'] and not browser['browser_page_loaded'] and browser['owner_uat']=='NOT_EXECUTED')
verify('original_4H56_not_promoted',receipt['donecheck_official']=='NOT_TESTED' and receipt['owner_acceptance']=='NOT_TESTED')
report={'schema':'enguru.ulmi.h1.e09.separate-process-source-audit/v1','checks':Q,'passed':sum(x['pass'] for x in Q),'total':len(Q),'audit_type':'AUTHOR_CONTROLLED_SEPARATE_PROCESS_NOT_INDEPENDENT_DONECHECK','official_decision':'HOLD_NO_SIGNED_REVIEWER_OWNER','h1':'HOLD','h2':'PARKED','v22_formal':'0/12','v22_technical_historical':'4/12','browser_uat':'HOLD_BROWSER_POLICY','pilot_A_B_C_formal':'0/8_EACH'}
(E/'E09_SCOPED_SOURCE_AUDIT_RECEIPT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('E09_AUTHOR_SCOPED_AUDIT',report['passed'],'/',report['total'])
