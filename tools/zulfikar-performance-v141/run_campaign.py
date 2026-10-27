"""Five disposable real task families using existing Work/GitHub subprocess runtime."""
from __future__ import annotations
import hashlib,json,os,sqlite3,subprocess,sys,tempfile,zipfile,io
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'governance/enguru-suzgeci/zulfikar-v12/v141/dom').exists() or (p/'source/governance/enguru-suzgeci/zulfikar-v12/v141/dom').exists())
DOM=ROOT/'governance/enguru-suzgeci/zulfikar-v12/v141/dom'
if not DOM.exists(): DOM=ROOT/'source/governance/enguru-suzgeci/zulfikar-v12/v141/dom'
sys.path.insert(0,str(DOM))
from engine import Contract,LocalJournal,execute
from proof_chain import audit_evidence,finish_readiness
from completion_guard import audit_completion_claim

def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,sort_keys=True,ensure_ascii=False)+'\n')
def proc(args,**kw):
 p=subprocess.run(args,capture_output=True,text=True,timeout=20,**kw)
 return {'args':[str(x) for x in args], 'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def py(code,*args):return proc([sys.executable,'-B','-c',code,*map(str,args)])
def must(v,msg):
 if not v:raise AssertionError(msg)

def cli(d):
 p=d/'total.py';code="import json,sys\na=json.loads(sys.argv[1])\nassert isinstance(a,list) and all(type(x) is int for x in a)\nprint(sum(a))\n";p.write_text(code)
 def test():
  obs=[proc([sys.executable,'-B',str(p),x]) for x in ['[2,3,7]','[]','[-3,1]','[true]']]
  return obs,all(obs[i]['exitCode']==0 and obs[i]['stdout'].strip()==str(v) for i,v in enumerate([12,0,-2])) and obs[3]['exitCode']!=0
 b,ok=test();p.write_text('if BROKEN SYNTAX\n');f=proc([sys.executable,'-B',str(p),'[1]']);p.write_text(code);r,end=test()
 return b,{'faultObserved':f['exitCode']!=0,'observations':[f]},r,[ok,end,p.read_text()==code]

def db(d):
 p=d/'tasks.sqlite'
 code="""import sqlite3,sys,os
c=sqlite3.connect(sys.argv[1]);c.execute('create table if not exists operations(id text primary key)');c.execute('create table if not exists rows(id integer primary key,value integer)');c.commit()
if not c.execute("select 1 from operations where id='job-1'").fetchone():
 c.execute("insert into operations values('job-1')")
 c.execute('insert into rows values(1,2)')
 if sys.argv[2]=='crash': os._exit(23)
 c.executemany('insert into rows values(?,?)',[(2,3),(3,7)]);c.commit()
"""
 def verify():
  with sqlite3.connect(p) as c:return c.execute('select count(*),sum(value) from rows').fetchone()==(3,12) and c.execute('pragma integrity_check').fetchone()==('ok',) and c.execute('select count(*) from operations').fetchone()==(1,)
 b=py(code,p,'run');ok=verify()
 # Fresh database is an explicit new failure experiment, separate from baseline.
 q=d/'crash.sqlite';f=py(code,q,'crash')
 with sqlite3.connect(q) as c:rollback=c.execute('select count(*) from rows').fetchone()==(0,)
 rr=py(code,q,'run');again=py(code,q,'run')
 with sqlite3.connect(q) as c:recovered=c.execute('select count(*),sum(value) from rows').fetchone()==(3,12)
 return [b],{'faultObserved':f['exitCode']==23 and rollback,'observations':[f],'rollback':rollback},[rr,again],[ok,recovered,verify()]

def archive(d):
 p=d/'handoff.zip'
 code="""import zipfile,sys
with zipfile.ZipFile(sys.argv[1],'w') as z:
 for n,b in [('goal.txt',b'fixed target'),('result.txt',b'12')]:
  i=zipfile.ZipInfo(n,(2026,1,1,0,0,0));i.external_attr=0o600<<16;z.writestr(i,b)
"""
 def verify(path):
  try:
   with zipfile.ZipFile(path) as z:
    names=z.namelist()
    return names==['goal.txt','result.txt'] and z.read('goal.txt')==b'fixed target' and z.read('result.txt')==b'12'
  except (ValueError,zipfile.BadZipFile,KeyError):return False
 b=py(code,p);original=h(p);ok=verify(p)
 raw=bytearray(p.read_bytes());raw[38]^=1;p.write_bytes(raw);tamper=not verify(p)
 evil=d/'traversal.zip'
 with zipfile.ZipFile(evil,'w') as z:z.writestr('../outside','bad')
 traversal=not verify(evil)
 r=py(code,p);return [b],{'faultObserved':tamper and traversal,'observations':[],'tamperRejected':tamper,'traversalRejected':traversal},[r],[ok,verify(p),h(p)==original]

def loop(d):
 source=d/'source.txt';source.write_text('fixed source');out=d/'output.txt';out.write_text('0')
 contract=Contract('ZF.R04','Repair real output with source and replay guard','T01',('output',),h(source))
 state={'value':'0'};j=LocalJournal(d)
 def evaluator(s,c):return {'output':out.read_text()=='12' and s['value']=='12'}
 def repair(s,g,c):out.write_text('12');return {'value':'12'}
 def tester(s,c):
  p=proc(['sha256sum',str(out)]);return {'processObserved':True,'exitCode':p['exitCode'],'scope':'LOCAL_DISPOSABLE_PROOF','artifactSha256':p['stdout'].split()[0],'artifactPath':str(out)}
 def verifier(s,c,r):return h(out)==r['artifactSha256'] and out.read_text()==s['value']
 def drive(st=state,**replace):
  kw=dict(simulator=lambda *_:{'valid':True},evaluator=evaluator,repairer=repair,real_tester=tester,independent_verifier=verifier,source_probe=lambda c:h(source)==c['sourcePin'])
  kw.update(replace)
  return execute(contract,st,LocalJournal(d),source_file=source,**kw)
 forged=drive(real_tester=lambda *_:{'processObserved':True,'exitCode':0,'scope':'LOCAL_DISPOSABLE_PROOF','artifactSha256':'0'*64})
 b=drive();ok=b.get('diagnostic')==100
 source.write_text('drift');drift=drive({'value':'12'});source.write_text('fixed source')
 out.write_text('TAMPERED');stale=drive({'value':'12'})
 # Existing checkpoint must validate real output without rerunning repairs.
 rejected=stale.get('diagnostic')!=100
 out.write_text('12');r=drive({'value':'12'});events=len(LocalJournal(d).events)
 return [b],{'faultObserved':rejected and drift.get('diagnostic')!=100 and forged.get('reason')=='REAL_TEST_OR_INDEPENDENT_VERIFY_FAILED','observations':[forged,drift,stale],'staleOutputRejected':rejected},[r],[ok,r.get('diagnostic')==100,events==1]

def evidence(d):
 p=d/'output.txt';p.write_text('actual output');criteria={'C1':{'kinds':['EXECUTION'],'minRoots':1}}
 row={'evidenceId':'E1','goalId':'ZF.R05','criterionId':'C1','kind':'EXECUTION','provenanceRoot':'work-runtime','contentSha256':h(p),'relativePath':p.name}
 b=audit_evidence(d,criteria,[row],goal_id='ZF.R05');wrong={**row,'contentSha256':'0'*64};f=audit_evidence(d,criteria,[wrong],goal_id='ZF.R05')
 duplicate=audit_evidence(d,{'C1':{'kinds':['EXECUTION'],'minRoots':2}},[row,{**row,'evidenceId':'E2','provenanceRoot':'invented-reviewer'}],goal_id='ZF.R05')
 contract=Contract('ZF.R05','Guard evidence and finish','T01',('C1',),h(p));guard=audit_completion_claim(d,contract,{'selfReportedScore':100})
 finish=finish_readiness('ZF.R05',b,{},observed_working_result=True,independent_review=None,owner_decision={'goalId':'ZF.R05'},donecheck={'goalId':'ZF.R05'})
 r=audit_evidence(d,criteria,[row],goal_id='ZF.R05')
 return [b],{'faultObserved':f['state']=='EVIDENCE_HOLD' and duplicate['state']=='EVIDENCE_HOLD' and guard['state']=='COMPLETION_HOLD' and finish['state']=='FINISH_HOLD','observations':[f,duplicate,guard,finish]},[r],[b['criteriaMet']==1,r['criteriaMet']==1,finish['verifiedFinishIssued'] is False]

FUNCS=[cli,db,archive,loop,evidence]
def run(output):
 output.mkdir(parents=True,exist_ok=True);results=[];orchestrations=[]
 for i,fn in enumerate(FUNCS,1):
  with tempfile.TemporaryDirectory(prefix='zulfikar-real-') as tmp:
   d=Path(tmp);journal_dir=d/'coordinator';journal_dir.mkdir()
   task_source=d/'task-contract.json'
   plan=json.loads(Path(__file__).with_name('PLAN.json').read_text())
   dump(task_source,plan['tasks'][i-1]);receipt=d/'task-result.json'
   goal=Contract(f'ZF.R{i:02d}.COORDINATED',plan['tasks'][i-1]['outcome'],'T01',('measured_task_result',),h(task_source))
   def evaluate(state,contract):
    return {'measured_task_result':receipt.exists() and state.get('completed') is True and json.loads(receipt.read_text())['pass'] is True}
   def repair(state,gaps,contract):
    b,f,r,checks=fn(d)
    row={'taskId':f'R{i:02d}','family':fn.__name__,'BASELINE':b,'ADVERSARIAL':f,'REPAIR_RETEST':r,'semanticChecks':checks,'pass':all(checks) and f['faultObserved'],'scope':'DISPOSABLE_REAL_RUNTIME_ONLY','officialVerifiedFinish':'HOLD'}
    dump(receipt,row);return {'completed':True}
   def test(state,contract):
    observed=proc([sys.executable,'-B',str(Path(__file__).with_name('verify_task.py')),str(d),str(i)])
    return {'processObserved':True,'exitCode':observed['exitCode'],'scope':'LOCAL_DISPOSABLE_PROOF','artifactSha256':h(receipt),'independentProcess':observed,'artifactPath':str(receipt)}
   def verify(state,contract,proof):
    check=proc(['sha256sum',str(receipt)])
    return check['exitCode']==0 and check['stdout'].split()[0]==proof['artifactSha256'] and json.loads(receipt.read_text())['pass'] is True
   orchestration=execute(goal,{'completed':False},LocalJournal(journal_dir),simulator=lambda *_:{'valid':True},evaluator=evaluate,repairer=repair,real_tester=test,independent_verifier=verify,source_probe=lambda c:h(task_source)==c['sourcePin'],source_file=task_source)
   orchestrations.append(orchestration)
   row=json.loads(receipt.read_text());row['domCoordinator']=orchestration
   row['pass']=row['pass'] and orchestration.get('diagnostic')==100
   dest=output/f'R{i:02d}';dest.mkdir(exist_ok=True)
   for artifact in d.iterdir():
    if artifact.is_file() and not artifact.name.startswith('.'): (dest/artifact.name).write_bytes(artifact.read_bytes())
   (dest/'coordinator').mkdir(exist_ok=True)
   for artifact in journal_dir.iterdir():
    if artifact.is_file() and not artifact.name.startswith('.'): (dest/'coordinator'/artifact.name).write_bytes(artifact.read_bytes())
   dump(output/f'R{i:02d}.json',row);results.append(row)
 summary={'tasks':5,'passed':sum(r['pass'] for r in results),'results':results,'sourceEngineSha256':h(DOM/'engine.py'),'planSha256':h(Path(__file__).with_name('PLAN.json')),'independentHumanAcceptance':'HOLD','verifiedFinish':'HOLD'}
 dump(output/'summary.json',summary)
 print(json.dumps({'tasks':5,'passed':summary['passed'],'officialVerifiedFinish':'HOLD'}))
 return summary
if __name__=='__main__':
 x=run(Path(sys.argv[1]) if len(sys.argv)>1 else Path('campaign-output'));sys.exit(0 if x['passed']==5 else 1)
