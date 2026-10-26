"""Existing DÖM coordinates real repairs to three source-pinned existing software utilities."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
from prepare_workspace import prepare
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DOM=ROOT/'governance/enguru-suzgeci/zulfikar-v12/v141/dom';sys.path.insert(0,str(DOM))
from engine import Contract,LocalJournal,execute
from verify_completed_task import verify

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def call(args,cwd=None):
 start=time.monotonic();p=subprocess.run([str(a) for a in args],cwd=cwd,capture_output=True,text=True,timeout=90)
 return {'command':[str(a) for a in args],'pidObserver':os.getpid(),'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'durationSeconds':time.monotonic()-start}

def run(out):
 out.mkdir(parents=True,exist_ok=True);plan=json.loads((HERE/'PLAN.json').read_text());source_records=json.loads((HERE/'UPSTREAM_SOURCES.json').read_text())
 for row in source_records:
  b=(HERE/row['localPath']).read_bytes();assert hashlib.sha256(b).hexdigest()==row['sha256']
  assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['gitBlob']
 results=[]
 for task in plan['tasks']:
  ident=task['id'];d=out/ident;d.mkdir();baseline=d/'baseline-repo';baseline.mkdir();prepare(ident,baseline)
  baseout=d/'baseline-output';base=call([sys.executable,'-B',HERE/'task_checks.py',ident,baseline,baseout]);write(d/'baseline-process.json',base)
  initial=json.loads((baseout/'checks.json').read_text());assert initial['met']<4
  repaired=d/'repaired-repo';repaired.mkdir();journal_dir=d/'journal';journal_dir.mkdir();finalout=d/'final-output';artifact=finalout/'checks.json'
  source=d/'fixed-task.json';write(source,{'goalId':plan['goalId'],'task':task,'upstream':[x for x in source_records if x['path']==task['source']],'patchSha256':digest(HERE/'patches'/f'{ident}.patch')})
  contract=Contract(plan['goalId']+'.'+ident,task['userValue'],'T01',tuple(task['criteria']),digest(source))
  commands=[]
  def evaluate(state,c):
   p=Path(state['artifact']);row=json.loads(p.read_text()) if p.exists() else {'criteria':{}}
   return {k:row['criteria'].get(k) is True for k in c['criteria']}
  def repair(state,gaps,c):
   head=prepare(ident,repaired,repaired=True);write(d/'repair-source.json',{'isolatedHead':head,'upstreamSource':task['source'],'upstreamCommit':next(x['commit'] for x in source_records if x['path']==task['source']),'patchSha256':digest(HERE/'patches'/f'{ident}.patch')})
   process=call([sys.executable,'-B',HERE/'task_checks.py',ident,repaired,d/'repair-output']);commands.append(process)
   write(d/'repair-process.json',process)
   return {'artifact':str(artifact.resolve()),'repaired':True}
  def test(state,c):
   process=call([sys.executable,'-B',HERE/'task_checks.py',ident,repaired,finalout]);commands.append(process);write(d/'regression-process.json',process)
   return {'processObserved':True,'exitCode':process['exitCode'],'scope':'LOCAL_DISPOSABLE_PROOF','artifactSha256':digest(artifact),'artifactPath':str(artifact.resolve())}
  def independent(state,c,proof):
   process=call([sys.executable,'-B',HERE/'verify_completed_task.py',ident,repaired,finalout]);write(d/'separate-verification.json',process)
   return process['exitCode']==0 and digest(artifact)==proof['artifactSha256']
  shared=dict(simulator=lambda *_:{'valid':True},evaluator=evaluate,repairer=repair,real_tester=test,independent_verifier=independent,source_probe=lambda c:digest(source)==c['sourcePin'],source_file=source)
  start={'artifact':str((baseout/'checks.json').resolve()),'repaired':False}
  first=execute(contract,start,LocalJournal(journal_dir),**shared);count=len(commands)
  finalstate={'artifact':str(artifact.resolve()),'repaired':True}
  replay=execute(contract,finalstate,LocalJournal(journal_dir),**shared)
  final=json.loads(artifact.read_text());allcriteria=set(final['criteria'])==set(task['criteria'])
  ok=(first.get('diagnostic')==100 and final['met']==4 and allcriteria and replay.get('replayedVerifiedCheckpoint') is True and replay.get('processObserved') is False and len(commands)==count)
  row={'taskId':ident,'initialCriteriaMet':initial['met'],'finalCriteriaMet':final['met'],'criteriaTotal':4,'originalCriteria':task['criteria'],'allOriginalCriteriaBound':allcriteria,'domExecution':first,'replay':replay,'duplicateTaskProcesses':len(commands)-count,'pass':ok,'openTechnicalItems':[] if ok else ['TASK_OR_REPLAY_INCOMPLETE'],'independentHumanAcceptance':'HOLD','peerComparison':'HOLD_NO_SEPARATE_PEER_EXECUTOR','sourceContractSha256':digest(source),'outputSha256':digest(artifact)}
  write(d/'task-result.json',row);results.append(row)
 summary={'goalId':plan['goalId'],'initialMet':sum(x['initialCriteriaMet'] for x in results),'finalMet':sum(x['finalCriteriaMet'] for x in results),'totalCriteria':12,'tasksPassed':sum(x['pass'] for x in results),'taskResults':results,'sourceEngineSha256':digest(DOM/'engine.py'),'planSha256':digest(HERE/'PLAN.json'),'independentAcceptance':'HOLD','officialVerifiedFinish':'HOLD'}
 write(out/'summary.json',summary);print(json.dumps({k:summary[k] for k in ('initialMet','finalMet','totalCriteria','tasksPassed','officialVerifiedFinish')}));return summary
if __name__=='__main__':x=run(Path(sys.argv[1]).resolve());sys.exit(0 if x['tasksPassed']==3 else 1)
