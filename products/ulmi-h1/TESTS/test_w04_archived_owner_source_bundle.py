#!/usr/bin/env python3
"""Read-only H1 actual archived SHA-pinned 8 logical roles/6 source documents.
Archive is historical research source, not live main/owner producer authority.
"""
import hashlib,json,os,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'PRODUCT'))
import chat_bridge,contract_bridge
legacy=R/'RESEARCH_ARCHIVE'
source=legacy/'canonical_sources';baseline=legacy/'frozen_42'
contract=source/'03_ORNEK_MIMARI_KABUL_SOZLESMESI_A.json'
manifest=source/'manifest.json'
sha=lambda x:hashlib.sha256(x).hexdigest()
checks=[]
def ck(id,ok,desc=''):
 checks.append({'control':id,'pass':bool(ok),'observed':str(desc)[:250]})
 print(('PASS' if ok else 'FAIL'),id,str(desc)[:120],flush=True)
 if not ok:raise AssertionError(id)
ck('PILOT_A_PINNED_ARCHIVE_SHA',sha(contract.read_bytes())==contract_bridge.CONTRACT_PIN,sha(contract.read_bytes()))
ck('42_BASELINE_PINNED_MANIFEST_SHA',sha((baseline/'KAYNAK_MANIFEST.json').read_bytes())==contract_bridge.BASELINE_MANIFEST_PIN,sha((baseline/'KAYNAK_MANIFEST.json').read_bytes()))
with open(manifest,'rb') as f:manifest_data=f.read()
os.environ.update({'ENGURU_ULMI_CHAT_CONTRACT_FILE':str(contract),'ENGURU_ULMI_TRUSTED_BASELINE_ROOT':str(baseline),
 'ENGURU_ULMI_CHAT_CONTEXT_ROOT':str(source),'ENGURU_ULMI_CHAT_CONTEXT_MANIFEST_SHA256':sha(manifest_data)})
os.environ.pop('ENGURU_ULMI_CHAT_TEST_MODE',None)
try:graph,refs,context,is_test=chat_bridge.approved_context()
except (contract_bridge.ContractHold,chat_bridge.Hold) as e:
 print('HOLD_ARCHIVED_CONTEXT',type(e).__name__,e)
 raise
ck('NON_SYNTHETIC_ARCHIVED_PINNED_RESEARCH_SOURCE',not is_test,'source_class SHA_PINNED_RESEARCH_SOURCE_BUNDLE')
ck('EIGHT_ROLES_SOURCE_SHA_VERIFIED',len(refs)==8 and {r['role'] for r in refs}==set(chat_bridge.REQUIRED_ROLES),len(refs))
ck('SIX_UNIQUE_PHYSICAL_DOCUMENTS',len({r['sha256'] for r in refs})==6,len({r['sha256'] for r in refs}))
ck('42_BASELINE_ORIGINAL_PAYLOAD_FILES_VERIFIED',graph.get('baseline',{}).get('verified_files')==42,graph.get('baseline'))
ck('32K_LIMIT_WITH_REAL_SOURCE_BYTES',len(context.encode('utf-8'))<=32768,len(context.encode('utf-8')))
ck('DESIGN_ONLY_HUMAN_THRESHOLD',graph['gates']['owner_execution']=='HOLD_NO_GRANT',graph['gates'])
report={'schema':'enguru.ulmi.h1.v71.w04.archived-pinned-research-context-readback/v1',
 'source_class':'ARCHIVED_SHA_PINNED_RESEARCH_SOURCE_BUNDLE_NOT_LIVE_CURRENT_MAIN',
 'manifest_sha256':sha(manifest_data),'pinned_contract_sha256':sha(contract.read_bytes()),
 'pinned_baseline_manifest_sha256':sha((baseline/'KAYNAK_MANIFEST.json').read_bytes()),
 'context_bytes':len(context.encode('utf-8')),'roles':refs,'source_diff_current_main':'NOT_REVALIDATED_HERE',
 'owner_execution_grant':'NOT_ISSUED','independent_producer_identity':'NOT_PROVEN',
 'originated_in_older_p1_research_archive':True,'real_qwen':'NOT_EXECUTED','original_w04_full_closure':'HOLD',
 'checks':checks,'passed':len(checks),'total':len(checks)}
(R/'EVIDENCE/V71_W04_ARCHIVED_REAL_SOURCE_CONTEXT_SHA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('W04_ARCHIVED_RESEARCH_CONTEXT',len(checks),'/',len(checks))
