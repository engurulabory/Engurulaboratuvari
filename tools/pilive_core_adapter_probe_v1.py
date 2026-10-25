"""Native read-only P02 adapter dry-run plus remaining source dependencies.

Uses the existing pinned Core and existing native regression probe. Installs and
activates nothing. Other project identities stay visible with unavailable data.
"""
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
import zipfile
from tools import pilive_native_learning_probe_v1 as safe
from tools import pilive_core_snapshot_adapter_v1 as adapter

CORE_READ = r'''
import sys,json,runpy
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'tools'))
core=runpy.run_path(str(root/'tools/enguru_progress.py'),run_name='pilive_readonly_core')
registry=core['registry']()
allowed=('projectId','state','worklist','workContract','productionArea','productionFacet')
registry['projects']={k:{f:v for f,v in row.items() if f in allowed} for k,row in registry['projects'].items()}
key='plive-p02-user-screen'
facts={key:{'summary':core['summarize'](key),'verify':core['structural_verify'](key)}}
print(json.dumps({'registry':registry,'facts':facts},ensure_ascii=False))
'''

def head(root):
    p=subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],capture_output=True,text=True,timeout=10,check=True)
    return p.stdout.strip()

def native_read(home, workdir):
    root=Path(home)/'Enguru/Projects/Engurulaboratuvari'
    before=safe.core_pin_check(root)
    if not all(row['match'] for row in before):return {'state':'HOLD_CORE_PIN_DRIFT','before':before,'executed':False}
    rev_before=head(root)
    p=subprocess.run([sys.executable,'-B','-S','-c',CORE_READ,str(root)],cwd=workdir,
                     capture_output=True,text=True,timeout=60)
    after=safe.core_pin_check(root);rev_after=head(root)
    if p.returncode or before!=after:return {'state':'HOLD_CORE_READ','executed':True,'returncode':p.returncode,'before':before,'after':after}
    require_size=len(p.stdout.encode())<=2*1024*1024
    if not require_size:raise ValueError('CORE_OUTPUT_LIMIT')
    data=json.loads(p.stdout)
    try:
        snapshot=adapter.build(data['registry'],data['facts'],revision_before=rev_before,
          revision_after=rev_after,pins_before={r['path']:r['sha256'] for r in before},
          pins_after={r['path']:r['sha256'] for r in after},
          source_read_at=datetime.now(timezone.utc).isoformat(),
          adapter_built_at=datetime.now(timezone.utc).isoformat())
    except adapter.Hold as exc:
        code=str(exc)
        return {'state':'HOLD_ADAPTER_VALIDATION','reason':code if re.fullmatch(r'HOLD_[A-Z_]+',code) else 'HOLD_UNCLASSIFIED_VALIDATION',
          'executed':True,'before':before,'after':after,'revisionBefore':rev_before,
          'revisionAfter':rev_after,'coreRegistry':data['registry'],'coreFacts':data['facts'],
          'diagnosticVisibility':'PRIVATE_RECEIPT_ONLY','verifiedFinish':'HOLD'}
    p02=[r for r in snapshot['projects'] if r['projectId']=='ENGURU_PLIVE_P02_USER_SCREEN']
    good=len(p02)==1 and p02[0]['status']=='PASS_CORE_READ_ONLY'
    return {'state':'PASS_NATIVE_P02_ADAPTER_DRY_RUN_ONLY' if good else 'HOLD_P02_ADAPTER',
      'executed':True,'before':before,'after':after,'snapshot':snapshot,
      'scope':'All Core-discovered identities; qualified counter/active facts for P02 only; other rows HOLD',
      'uiExecution':'NOT_EXECUTED','verifiedFinish':'HOLD'}

def dependencies(home):
    rows=[]
    scopes=[(Path(home)/'Library/Application Support/ENGURU/LiveProgress/v4',['bridge.py','legacy_snapshot.py']),
            (Path('/Applications/ENGURU-PLive-V31.app/Contents/Resources'),['projection_v6.py'])]
    for root,names in scopes:
        for name in names:
            row={'path':str(root/name)}
            try:
                raw=safe.read_file(root,name)
                row.update(state='CAPTURED_ONLY',sha256=safe.digest(raw),bytes=len(raw),contentUtf8=raw.decode())
            except (OSError,ValueError,UnicodeError) as exc:row.update(state='HOLD_EXACT_DEPENDENCY',reason=type(exc).__name__)
            rows.append(row)
    return rows

def run(archive, home, *, self_test=False):
    with zipfile.ZipFile(archive) as z:
        manifest_raw=z.read('MANIFEST.json');manifest=json.loads(manifest_raw)
        if not isinstance(manifest['files'],dict) or len(manifest['files'])>30:raise ValueError('MANIFEST_SCOPE')
        with tempfile.TemporaryDirectory(prefix='enguru-pilive-adapter-') as temp:
            temp=Path(temp).resolve(strict=True)
            for name,pin in manifest['files'].items():
                rel=Path(name)
                if rel.is_absolute() or '..' in rel.parts or not rel.parts:raise ValueError('MANIFEST_PATH')
                raw=z.read('payload/'+name)
                if safe.digest(raw)!=pin:raise ValueError('PACKAGE_SOURCE_SHA')
                out=temp/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
            p=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py','-q'],
                             cwd=temp,capture_output=True,text=True,timeout=120)
            logs=p.stdout+p.stderr
            import re
            counts=re.findall(r'Ran\s+(\d+)\s+tests?',logs)
            tests={'returncode':p.returncode,'tests':int(counts[-1]) if counts else 0,
                   'state':'PASS' if p.returncode==0 and counts else 'HOLD',
                   'outputSha256':safe.digest(logs.encode()),'failureOutput':logs[:16000] if p.returncode else ''}
            if self_test:return {'state':'PASS_PACKAGE_SELF_TEST_ONLY' if tests['state']=='PASS' else 'HOLD_PACKAGE_TESTS','tests':tests}
            try:
                native=native_read(home,temp) if tests['state']=='PASS' else {'state':'NOT_EXECUTED_TESTS_HOLD','executed':False}
            except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:
                native={'state':'HOLD_NATIVE_READ_DIAGNOSTIC','reason':type(exc).__name__,
                        'verifiedFinish':'HOLD','executionCompletion':'UNKNOWN_AFTER_EXCEPTION'}
            good=tests['state']=='PASS' and native['state']=='PASS_NATIVE_P02_ADAPTER_DRY_RUN_ONLY'
            return {'schema':'enguru.pilive.native-core-adapter-observation/v1',
              'observedAtUtc':datetime.now(timezone.utc).isoformat(),'platform':platform.system(),
              'packageSourceCommit':manifest['sourceCommit'],'packageManifestSha256':safe.digest(manifest_raw),
              'parentReceiptSha256':'150c772bbec5d536f884888e84f1e9ee47bb6b6b870cbfe7ec4263df1b6c88b7',
              'tests':tests,'nativeAdapter':native,'dependencies':dependencies(home),
              'state':'PASS_NATIVE_TESTS_AND_P02_DRY_RUN_ONLY' if good else 'HOLD_NATIVE_ADAPTER_REVIEW',
              'canonicalWrites':0,'nativeMuscleWrites':0,'sqliteConnections':0,'networkRequests':0,
              'keychainReads':0,'appLaunches':0,'runtimeActivations':0,'installedAppWrites':0,
              'temporaryTestWrites':'OWNED_TEMPORARY_DIRECTORY_ONLY',
              'productAcceptance':'HOLD','verifiedFinish':'HOLD'}

def main():
    if sys.argv[1:] not in (['--self-test'],['--run']):print('USAGE: PACKAGE.pyz --self-test | --run');return 2
    self_test=sys.argv[1]=='--self-test'
    if not self_test and platform.system()!='Darwin':print('STATE=HOLD_MAC_REQUIRED');return 2
    try:
        result=run(Path(sys.argv[0]),Path.home(),self_test=self_test)
        if not self_test:safe.save(Path.home(),result)
        print('STATE='+result['state']);print('TESTS='+str(result['tests']['tests']))
        return 0 if result['state'].startswith('PASS_') else 2
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,subprocess.SubprocessError) as exc:
        print('STATE=HOLD_NATIVE_ADAPTER_PROBE; REASON='+type(exc).__name__);return 2

if __name__=='__main__':raise SystemExit(main())
