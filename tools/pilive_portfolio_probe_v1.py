"""Bounded read-only portfolio collector over the unchanged pinned Core APIs.

Every counter comes from summarize()/structural_verify(). Source manifests
include registry discovery inputs and project state/worklist/contract files.
No installation, activation, cache publication or acceptance writer exists here.
"""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import zipfile
from tools import pilive_native_learning_probe_v1 as safe
from tools import pilive_core_snapshot_adapter_v1 as adapter

def now():return datetime.now(timezone.utc).isoformat()

class CoreAPIHold(ValueError):
    def __init__(self, returncode, stderr):
        super().__init__('CORE_API_FAILURE')
        self.diagnostic={'returncode':returncode,'stderrTail':stderr.decode('utf-8',errors='replace')[-4096:],
                         'visibility':'PRIVATE_RECEIPT_ONLY'}

def strict_json(raw):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('HOLD_DUPLICATE_JSON_KEY')
            result[k]=v
        return result
    def constant(_):raise ValueError('HOLD_NONFINITE_JSON')
    result=json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
    if not isinstance(result,dict):raise ValueError('HOLD_JSON_OBJECT')
    return result

def governed(path):
    if not isinstance(path,str) or not path or '\x00' in path:raise ValueError('HOLD_SOURCE_PATH')
    p=Path(path)
    if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0]!='governance':raise ValueError('HOLD_SOURCE_PATH')
    return p.as_posix()

def contract_inputs(root):
    folder=Path(root)/'governance';fd=safe.directory_fd(folder);os.close(fd)
    paths=sorted(p.relative_to(root).as_posix() for p in folder.glob('**/*_WORK_CONTRACT_V1.json'))
    if len(paths)>256:raise ValueError('HOLD_CONTRACT_LIMIT')
    inputs=set(paths)
    for path in paths:
        doc=strict_json(safe.read_file(root,path))
        inputs.add(governed(doc.get('schemaContract')))
    return inputs

def source_manifest(root, paths):
    if len(paths)>512:raise ValueError('HOLD_SOURCE_COUNT_LIMIT')
    pins={};errors={};budget=32*1024*1024
    for path in sorted(paths):
        try:
            raw=safe.read_file(root,path,min(2*1024*1024,budget));budget-=len(raw)
            pins[path]=safe.digest(raw)
        except (OSError,ValueError) as exc:errors[path]=type(exc).__name__
    return {'pins':pins,'errors':errors}

# The worker executes exact verified bytes, not a second read via runpy. Helpers
# are loaded as siblings from the same approved source pins. Core ROOT still
# derives from its original __file__; no Core function or policy is replaced.
WORKER = r'''
import sys,json,types
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from tools import pilive_native_learning_probe_v1 as safe
root=Path(sys.argv[2]);action=sys.argv[3]
for name in ('enguru_progress_adapters','enguru_progress_intelligence'):
    relative='tools/'+name+'.py';raw=safe.read_file(root,relative)
    if safe.digest(raw)!=safe.CORE_PINS[relative]:raise ValueError('HOLD_CORE_HELPER_SHA')
    module=types.ModuleType(name);module.__file__=str(root/relative);sys.modules[name]=module
    exec(compile(raw,module.__file__,'exec'),module.__dict__)
path='tools/enguru_progress.py';raw=safe.read_file(root,path)
if safe.digest(raw)!=safe.CORE_PINS[path]:raise ValueError('HOLD_CORE_SOURCE_SHA')
core={'__file__':str(root/path),'__name__':'pilive_readonly_portfolio_core'}
exec(compile(raw,core['__file__'],'exec'),core)
if action=='registry':
    doc=core['registry']();allowed=('projectId','state','worklist','workContract','productionArea','productionFacet')
    doc['projects']={k:{f:v for f,v in r.items() if f in allowed} for k,r in doc['projects'].items()}
else:
    key=sys.argv[4];doc={'summary':core['summarize'](key),'verify':core['structural_verify'](key)}
print(json.dumps(doc,ensure_ascii=False))
'''

def core_call(root, action, workdir, key=None, timeout=12):
    package_root=str(Path(__file__).parents[1])
    args=[sys.executable,'-I','-B','-S','-c',WORKER,package_root,str(root),action]
    if key is not None:args.append(key)
    p=subprocess.run(args,cwd=workdir,capture_output=True,timeout=timeout)
    if p.returncode:raise CoreAPIHold(p.returncode,getattr(p,'stderr',b''))
    if len(p.stdout)>2*1024*1024:raise ValueError('CORE_OUTPUT_LIMIT')
    return strict_json(p.stdout)

def revision(root):
    p=subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],capture_output=True,text=True,timeout=10,check=True)
    return p.stdout.strip()

def portfolio_read(home, workdir):
    root=Path(home)/'Enguru/Projects/Engurulaboratuvari';started=now()
    initial=safe.core_pin_check(root)
    if not all(x['match'] for x in initial):return {'state':'HOLD_CORE_PIN_DRIFT','executed':False,'initialPins':initial}
    rev_before=revision(root);discovery=contract_inputs(root)
    globals_before=source_manifest(root,set(safe.CORE_PINS)|discovery)
    if globals_before['errors']:return {'state':'HOLD_DISCOVERY_SOURCE','executed':False,'sources':globals_before}
    try:registry=core_call(root,'registry',workdir)
    except CoreAPIHold as exc:
        return {'state':'HOLD_CORE_REGISTRY','executed':True,'privateDiagnostic':exc.diagnostic,'sources':globals_before}
    entries=registry.get('projects',{})
    if not isinstance(entries,dict) or not 0<len(entries)<=1000:raise ValueError('HOLD_CORE_PROJECT_SET')
    all_paths=set(safe.CORE_PINS)|discovery;project_paths={}
    for key,entry in entries.items():
        paths={governed(entry[f]) for f in ('state','worklist')}
        if entry.get('workContract'):paths.add(governed(entry['workContract']))
        project_paths[key]=paths;all_paths|=paths
    before=source_manifest(root,all_paths)
    if any(before['pins'].get(k)!=v for k,v in globals_before['pins'].items()):
        return {'state':'HOLD_DISCOVERY_SOURCE_DRIFT','executed':True}
    facts={};deadline=time.monotonic()+75
    for key in sorted(entries):
        if project_paths[key]&set(before['errors']):facts[key]={'error':'SOURCE_NOT_READABLE'};continue
        remaining=deadline-time.monotonic()
        if remaining<=0:facts[key]={'error':'PORTFOLIO_TIME_BUDGET'};continue
        try:
            pair=core_call(root,'project',workdir,key,timeout=min(12,remaining))
            pair['sourceReadAt']=now();facts[key]=pair
        except subprocess.TimeoutExpired:facts[key]={'error':'CORE_TIMEOUT'}
        except CoreAPIHold as exc:facts[key]={'error':'CORE_API_FAILURE','privateDiagnostic':exc.diagnostic}
        except (OSError,ValueError,KeyError,TypeError):facts[key]={'error':'CORE_API_FAILURE'}
    try:registry_after=core_call(root,'registry',workdir)
    except CoreAPIHold as exc:
        return {'state':'HOLD_CORE_REGISTRY_READBACK','executed':True,'privateDiagnostic':exc.diagnostic,'facts':facts}
    after=source_manifest(root,all_paths);rev_after=revision(root)
    if registry!=registry_after or discovery!=contract_inputs(root) or before!=after or rev_before!=rev_after:
        return {'state':'HOLD_PORTFOLIO_SOURCE_DRIFT','executed':True,'before':before,'after':after,
                'revisionBefore':rev_before,'revisionAfter':rev_after,'facts':facts}
    snapshot=adapter.build_portfolio(registry,facts,revision_before=rev_before,revision_after=rev_after,
       pins_before=before['pins'],pins_after=after['pins'],source_read_at=started,adapter_built_at=now())
    return {'state':'PASS_NATIVE_PORTFOLIO_CAPTURE_ONLY','executed':True,'snapshot':snapshot,
       'sourceManifestBefore':before,'sourceManifestAfter':after,'sourceFiles':len(before['pins']),
       'coreFacts':facts,'allProjectKeys':sorted(entries),
       'scope':'All discovered projects attempted. Per-project HOLD is preserved; capture PASS is not counter or acceptance PASS.',
       'atomicity':'SOURCE_HASH_BRACKETS_ONLY; MULTI_FILE_CAPTURE_NOT_ATOMIC',
       'uiExecution':'NOT_EXECUTED','verifiedFinish':'HOLD'}

def binary_metadata():
    """Current installed metadata only; historical build provenance stays HOLD."""
    bundle=Path('/Applications/ENGURU-PLive-V31.app');result={'buildBinding':'HOLD_EXACT_HISTORICAL_BUILD_MANIFEST'}
    try:
        raw=safe.read_file(bundle,'Contents/MacOS/PLive',128*1024*1024)
        result['binarySha256']=safe.digest(raw)
    except (OSError,ValueError) as exc:result['binaryRead']='HOLD_'+type(exc).__name__
    commands={'currentSwiftVersion':['/usr/bin/xcrun','swiftc','--version'],
              'signatureDisplay':['/usr/bin/codesign','-d','--verbose=2',str(bundle)],
              'signatureVerification':['/usr/bin/codesign','--verify','--strict',str(bundle)]}
    for label,argv in commands.items():
        try:
            p=subprocess.run(argv,capture_output=True,text=True,timeout=12)
            output=p.stdout+p.stderr
            if label=='signatureDisplay':output='\n'.join(line for line in output.splitlines() if line.startswith(('Identifier=','Format=','CodeDirectory','Signature=')))
            elif label=='signatureVerification':output=''
            result[label]={'returncode':p.returncode,'metadata':output[:2000]}
        except (OSError,subprocess.SubprocessError) as exc:result[label]={'state':'HOLD_'+type(exc).__name__}
    result['toolchainMeaning']='CURRENT_INSTALLED_TOOLCHAIN_ONLY; NOT_PROOF_OF_BINARY_BUILD_TOOLCHAIN'
    return result

def main():
    from tools import pilive_core_adapter_probe_v1 as driver
    if sys.argv[1:] not in (['--self-test'],['--run']):return 2
    self_test=sys.argv[1]=='--self-test'
    if not self_test and platform.system()!='Darwin':print('STATE=HOLD_MAC_REQUIRED');return 2
    try:
        result=driver.run(Path(sys.argv[0]),Path.home(),self_test=self_test,reader=portfolio_read)
        if not self_test:
            result.update(schema='enguru.pilive.native-portfolio-observation/v1',
              parentReceiptSha256='39c28d1c41777c14decc7a67d034d13c34f242a7b4c261c2a524fd766c54b808',
              binaryMetadata=binary_metadata())
            safe.save(Path.home(),result)
        print('STATE='+result['state']);print('TESTS='+str(result['tests']['tests']))
        return 0 if result['state'].startswith('PASS_') else 2
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,subprocess.SubprocessError) as exc:
        print('STATE=HOLD_PORTFOLIO_PROBE; REASON='+type(exc).__name__);return 2

if __name__=='__main__':raise SystemExit(main())
