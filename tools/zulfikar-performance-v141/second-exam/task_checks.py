"""Actual existing-source tasks; all writes restricted to the supplied disposable root."""
import hashlib,importlib.util,io,json,os,stat,subprocess,sys,zipfile
from pathlib import Path
from unittest.mock import patch

def load(path):
 spec=importlib.util.spec_from_file_location('subject_'+hashlib.sha256(str(path).encode()).hexdigest()[:12],path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def call(args,cwd=None):
 p=subprocess.run([str(x) for x in args],cwd=cwd,capture_output=True,text=True,timeout=40)
 return {'command':[str(x) for x in args],'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}

def receipt(repo,out):
 m=load(repo/'tools/enguru_evidence_receipt_io.py');root=out/'receipts';root.mkdir(exist_ok=True)
 dest=root/'task'/'result.json';payload={'goalId':'ZF.SECOND.S01','result':'makbuz doğru ve kalıcı','value':12}
 modes=[];fsync=os.fsync
 def observed(fd):modes.append('directory' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'file');return fsync(fd)
 with patch.object(m.os,'fsync',side_effect=observed):m.write_new_json(dest,payload,evidence_root=root)
 normal=json.loads(dest.read_text())==payload
 preserved=False
 try:m.write_new_json(dest,{'value':'overwrite'},evidence_root=root)
 except FileExistsError:preserved=dest.read_text()==json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
 finite=True;invalid=[]
 for i,value in enumerate([float('nan'),float('inf'),float('-inf')]):
  p=root/'invalid'/f'{i}.json'
  try:m.write_new_json(p,{'value':value},evidence_root=root);invalid.append(p.name);finite=False
  except ValueError:finite=finite and not p.exists()
 interrupted=root/'fault'/'interrupted.json'
 with patch.object(m.os,'fsync',side_effect=OSError('injected fsync failure')):
  try:m.write_new_json(interrupted,payload,evidence_root=root)
  except OSError:pass
 clean=not interrupted.exists() and not list(interrupted.parent.glob('*.tmp'))
 m.write_new_json(interrupted,payload,evidence_root=root)
 retry=json.loads(interrupted.read_text())==payload
 # Original regression source in a fresh process, including existing native/Steward guard calls.
 reg=call([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_enguru_p06_evidence_receipt_io.py','-v'],cwd=repo)
 return {'finite_json_only':finite,'unchanged_existing_receipts':normal and preserved,'directory_durability':modes.count('directory')>=2 and 'file' in modes,'retry_and_regression':clean and retry and reg['exitCode']==0}, {'normalReceipt':str(dest.relative_to(out)),'invalidPublished':invalid,'fsyncObserved':modes,'interruptionCleaned':clean,'regression':reg}

def management(repo,out):
 m=load(repo/'tools/enguru_management_v69_source_adapter.py');pin='a83f6f428b6a4373be60029cd99e18e9ebca501b';gate=json.dumps({'repository':m.EXPECTED_REPO,'state':'PAUSED_AUDITED'}).encode()
 def task(i,deps):return {'id':i,'state':'READY','action':'verify_file_digest','target_repo':m.EXPECTED_REPO,'path':'governance/source.txt','dependencies':deps}
 def run(tasks):return m.reconcile(json.dumps({'tasks':tasks}).encode(),gate,'isolated-original-source',pin)
 good=run([task('A',[]),task('B',['A']),task('C',['B'])]);(out/'inventory.json').write_text(json.dumps(good,sort_keys=True,indent=2)+'\n')
 cycles=[run([task('A',['A'])]),run([task('A',['B']),task('B',['A'])])]
 invalid=[]
 for deps in [[{}],[1],['A','A']]:
  try:invalid.append(run([task('A',deps)]))
  except Exception as e:invalid.append({'state':'UNCAUGHT_EXCEPTION','type':type(e).__name__})
 # Long acyclic worklists exercise stack-independent graph traversal.
 large=run([task(f'T{i}',[f'T{i-1}'] if i else []) for i in range(1500)])
 tasks=out/'tasks.json';tasks.write_text(json.dumps({'tasks':[task('A',[]),task('B',['A'])]}));g=out/'gate.json';g.write_bytes(gate)
 args=[sys.executable,'-B',repo/'tools/enguru_management_v69_source_adapter.py','--tasks',tasks,'--gate',g,'--source-ref','isolated-original-source','--source-commit',pin]
 first=call(args);second=call(args)
 reg=call([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_enguru_management_v69_source_adapter.py','-v'],cwd=repo)
 return {'valid_inventory_preserved':good['state']=='PASS_SOURCE_BOUND_MANAGEMENT_INVENTORY' and good['task_count']==3 and good['independently_accepted']==0,'dependency_cycles_hold':all(x['state']=='HOLD_GUVENLI_DUR' for x in cycles),'malformed_dependencies_hold':all(x['state']=='HOLD_GUVENLI_DUR' for x in invalid),'repeatable_cli_and_regression':large['task_count']==1500 and first['exitCode']==second['exitCode']==reg['exitCode']==0 and first['stdout']==second['stdout']},{'cycles':cycles,'malformed':invalid,'cli':first,'replay':second,'regression':reg}

def rebuild(packet,mutate,compression=zipfile.ZIP_STORED):
 target=io.BytesIO()
 with zipfile.ZipFile(io.BytesIO(packet)) as src,zipfile.ZipFile(target,'w',compression=compression) as dst:
  entries={n:src.read(n) for n in src.namelist()};mutate(entries)
  for n,b in entries.items():
   info=zipfile.ZipInfo(n,(2026,10,26,0,0,0));info.external_attr=0o100644<<16;info.compress_type=compression;dst.writestr(info,b)
 return target.getvalue()

def handoff(repo,out):
 mod=repo/'capabilities/enguru-harvest-v1/build_github_osi_handoff.py';m=load(mod)
 first=call([sys.executable,'-B',mod]);r=json.loads(first['stdout']);p=mod.parent/r['package_filename'];b=p.read_bytes();(out/'handoff.zip').write_bytes(b)
 normal=m.inspect(b);again=call([sys.executable,'-B',mod]);same=b==p.read_bytes()
 def large(entries):
  path='capabilities/enguru-harvest-v1/goal.json';content=b'x'*(m.MAX_PACKAGE_BYTES+1);entries[path]=content
  manifest=json.loads(entries['HANDOFF_MANIFEST.json']);manifest['sources'][path]={'sha256':hashlib.sha256(content).hexdigest(),'size':len(content)};entries['HANDOFF_MANIFEST.json']=json.dumps(manifest).encode()
 bomb=rebuild(b,large,zipfile.ZIP_DEFLATED);(out/'oversized-expanded.zip').write_bytes(bomb)
 budget=m.inspect(bomb)
 malformed=[]
 for mutation in [lambda e:e.update({'HANDOFF_MANIFEST.json':b'[]'}),lambda e:e.update({'HANDOFF_MANIFEST.json':b'null'})]:
  try:malformed.append(m.inspect(rebuild(b,mutation)))
  except Exception as exc:malformed.append({'state':'UNCAUGHT_EXCEPTION','type':type(exc).__name__})
 def badrow(e):
  v=json.loads(e['HANDOFF_MANIFEST.json']);v['sources']['AGENTS.md']=[];e['HANDOFF_MANIFEST.json']=json.dumps(v).encode()
 try:malformed.append(m.inspect(rebuild(b,badrow)))
 except Exception as exc:malformed.append({'state':'UNCAUGHT_EXCEPTION','type':type(exc).__name__})
 reg=call([sys.executable,'-B','-m','unittest','-v','test_github_osi_handoff'],cwd=mod.parent)
 return {'real_nine_source_package':first['exitCode']==0 and normal['state']=='PASS_GITHUB_PACKAGE_INTEGRITY_ONLY' and r['file_count']==9,'expanded_budget_enforced':len(bomb)<m.MAX_PACKAGE_BYTES and budget['state'].startswith('HOLD'),'malformed_manifest_hold':all(x['state'].startswith('HOLD') for x in malformed),'repeatable_build_and_regression':again['exitCode']==reg['exitCode']==0 and same},{'build':first,'replay':again,'normal':normal,'expandedAttack':budget,'expandedArchiveBytes':len(bomb),'malformed':malformed,'regression':reg}

if __name__=='__main__':
 task,repo,out=sys.argv[1],Path(sys.argv[2]).resolve(),Path(sys.argv[3]).resolve();out.mkdir(parents=True,exist_ok=True)
 try:
  checks,observations={'S01':receipt,'S02':management,'S03':handoff}[task](repo,out)
  result={'taskId':task,'criteria':checks,'met':sum(checks.values()),'total':len(checks),'observations':observations,'officialFinish':'HOLD'}
 except Exception as exc:
  result={'taskId':task,'criteria':{},'met':0,'total':4,'error':type(exc).__name__+': '+str(exc),'officialFinish':'HOLD'}
 (out/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(json.dumps(result,ensure_ascii=False,sort_keys=True));sys.exit(0 if result['met']==4 else 1)
