#!/usr/bin/env python3
"""ENGURU V5 GitHub-side advisory: deterministic, owner-authenticated, immutable."""
from pathlib import Path
import hashlib,json,os,re,sys

ROOT=Path('governance/enguru-suzgeci/learning/bridge/pilot')
SCHEMA='enguru.mk.peer-diagnosis/v5'
TASK='ENGURU_MK_BRIDGE_PILOT_V1'
CODES={
 'PILOT_HELLO':('SUCCESS','OBSERVED','ACK_GAP',('ACK_RECONCILE','LEDGER_AUDIT'),'INSPECT_LOCAL_LEDGER'),
 'GITHUB_RECEIVED':('SUCCESS','OBSERVED','RETURN_ACK_GAP',('LEDGER_AUDIT','ACK_RECONCILE'),'INSPECT_LOCAL_LEDGER'),
 'PILOT_RECOVERY':('WARNING','HYPOTHESIS','REPLAY_OR_CURSOR',('CURSOR_AUDIT','ACK_RECONCILE'),'INSPECT_LOCAL_LEDGER'),
 'RUNTIME_DRIFT':('MISMATCH','HYPOTHESIS','RUNTIME_PIN',('RUNTIME_AUDIT','TEST_COMPATIBILITY'),'INSPECT_RUNTIME'),
 'PACKAGE_ABSENT':('MISSING','HYPOTHESIS','PACKAGE_PIN',('PACKAGE_SHA_AUDIT','SOURCE_AUDIT'),'INSPECT_PACKAGE'),
 'INTERACTIVE_TIMEOUT':('ERROR','HYPOTHESIS','OWNER_BOUNDARY',('TIMEOUT_REVIEW','AUDIT_RETRY'),'INSPECT_TIMEOUT'),
 'NODE_TAP_MISMATCH':('INCORRECT','HYPOTHESIS','CONTRACT_DRIFT',('FORMAT_REGRESSION','SOURCE_AUDIT'),'INSPECT_TEST_CONTRACT')}
COST={'ACK_RECONCILE':1,'LEDGER_AUDIT':1,'CURSOR_AUDIT':2,'RUNTIME_AUDIT':2,'TEST_COMPATIBILITY':3,'PACKAGE_SHA_AUDIT':1,'SOURCE_AUDIT':2,'TIMEOUT_REVIEW':2,'AUDIT_RETRY':3,'FORMAT_REGRESSION':2}
FIELDS={'schema','eventId','taskId','blockId','producer','sequence','type','code','sourceCommit','evidenceSha256','observedAt','visibility'}
class Hold(Exception):pass

def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode()
def digest(x):return hashlib.sha256(canon(x)).hexdigest()
def unique(kv):
 d={}
 for k,v in kv:
  if k in d:raise Hold('DUPLICATE_JSON_KEY')
  d[k]=v
 return d

def event(data,producer,seq):
 if not isinstance(data,dict) or set(data)!=FIELDS or data['schema']!='enguru.mk.bridge-event/v1' or data['taskId']!=TASK:raise Hold('EVENT_SCHEMA')
 if data['producer']!=producer or data['visibility']!='PUBLIC_SANITIZED' or data['code'] not in CODES:raise Hold('EVENT_SCOPE')
 if type(data['sequence']) is not int or data['sequence']!=seq or data['eventId']!=('MAC-' if producer=='MAC_OSI_MK' else 'GH-')+f'{seq:08d}':raise Hold('EVENT_SEQUENCE')
 if data['type'] not in ('SUCCESS','ERROR','NEED','MISMATCH'):raise Hold('EVENT_TYPE')
 if not re.fullmatch(r'[a-f0-9]{40}',data['sourceCommit']) or not re.fullmatch(r'[a-f0-9]{64}',data['evidenceSha256']):raise Hold('EVENT_SHA')
 if not re.fullmatch(r'OSIBLOCK-[0-9]{8}-[A-Z0-9]{3,16}',data['blockId']):raise Hold('EVENT_BLOCK')
 from datetime import datetime
 try:
  ts=datetime.fromisoformat(data['observedAt'].replace('Z','+00:00'))
  if ts.utcoffset() is None:raise ValueError('tz')
 except (ValueError,TypeError,AttributeError):raise Hold('EVENT_TIMESTAMP')
 return data

def assess(ev):
 cat,level,hyp,options,step=CODES[ev['code']]
 alt=sorted([{'solutionCode':c,'score':80-COST[c]*4,'verifiedCases':0,'evidenceNeeded':'INDEPENDENT_OUTCOME_PROOF','action':'REVIEW_OR_READONLY','reversible':True} for c in options],key=lambda x:(-x['score'],x['solutionCode']))
 return {'schema':SCHEMA,'reportId':'DIA-'+ev['eventId'],'eventId':ev['eventId'],'eventSha256':digest(ev),
 'producer':ev['producer'],'recipient':'GITHUB_MK' if ev['producer']=='MAC_OSI_MK' else 'MAC_OSI_MK',
 'taskId':ev['taskId'],'blockId':ev['blockId'],'visibility':'PUBLIC_SANITIZED','category':cat,
 'findingCode':'REPORTED_'+ev['code'],'observationCode':ev['code'],
 'needs':['EVIDENCE_CORRELATION','POST_ACTION_VERIFICATION'] if level=='HYPOTHESIS' else ['TRANSPORT_RECONCILIATION'],
 'requirements':['SOURCE_SHA_ANCHOR','INDEPENDENT_VERIFIER','OWNER_REVIEW_FOR_CHANGES'],
 'hypothesisCode':hyp,'claimLevel':level,'rootCause':'UNCONFIRMED',
 'alternatives':alt,'suggestedSolutionCode':alt[0]['solutionCode'],'alignedNextStep':step,
 'nextStepPolicy':'READONLY_OR_OWNER_REVIEW','authority':'SUGGESTION_ONLY','productWrites':0,'officialAcceptance':'HOLD'}

def write_once(path,raw):
 if path.is_symlink():raise Hold('SYMLINK_OUTPUT')
 if path.exists():
  if path.read_bytes()!=raw:raise Hold('IMMUTABLE_CONFLICT')
  return 0
 path.parent.mkdir(parents=True,exist_ok=True)
 with open(path,'xb') as f:f.write(raw)
 return 1

def process(worktree,owner,actor):
 if not owner or actor!=owner or actor.endswith('[bot]'):raise Hold('OWNER_ACTOR')
 base=Path(worktree)/ROOT;new=0;count=0
 for producer,dir_in,dir_out,prefix in [('MAC_OSI_MK','streams/mac','diagnostics/mac','MAC'),('GITHUB_MK','streams/github','diagnostics/github','GH')]:
  src=base/dir_in;dst=base/dir_out
  if src.is_symlink() or dst.is_symlink():raise Hold('DIR_SYMLINK')
  if not src.exists():continue
  files=sorted(src.iterdir())
  if len(files)>100:raise Hold('CAPACITY')
  for number,p in enumerate(files,1):
   if p.is_symlink() or not p.is_file() or p.stat().st_size>4096 or p.name!=f'{prefix}-{number:08d}.json':raise Hold('SOURCE_FILE')
   try:obj=json.loads(p.read_bytes(),object_pairs_hook=unique)
   except (ValueError,UnicodeError,TypeError) as e:raise Hold('BAD_JSON') from e
   ev=event(obj,producer,number)
   new+=write_once(dst/p.name,canon(assess(ev)));count+=1
 return {'state':'PASS_V5_BOUNDED_DIAGNOSTICS','cases':count,'newRecords':new,'productWrites':0,'officialAcceptance':'HOLD'}

def main():
 try:
  if sys.argv[1:]==['--self-test']:
   import tempfile
   with tempfile.TemporaryDirectory() as td:
    p=Path(td)/ROOT/'streams/mac';p.mkdir(parents=True)
    ev={'schema':'enguru.mk.bridge-event/v1','eventId':'MAC-00000001','taskId':TASK,'blockId':'OSIBLOCK-20261024-PILOT','producer':'MAC_OSI_MK','sequence':1,'type':'SUCCESS','code':'PILOT_HELLO','sourceCommit':'a'*40,'evidenceSha256':'a'*64,'observedAt':'2026-10-24T14:00:00Z','visibility':'PUBLIC_SANITIZED'}
    (p/'MAC-00000001.json').write_bytes(canon(ev))
    assert process(td,'owner','owner')['newRecords']==1
    assert process(td,'owner','owner')['newRecords']==0
    print('GH_INTELLIGENCE_V5_SELFTEST=PASS')
  else:print(json.dumps(process('.',os.getenv('ENGURU_MK_OWNER',''),os.getenv('ENGURU_MK_ACTOR','')),sort_keys=True))
 except (Hold,OSError) as e:
  print('STATE=HOLD_GUVENLI_DUR; REASON='+str(e));raise SystemExit(50)
if __name__=='__main__':main()
