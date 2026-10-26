"""Read-only native repeat test and existing MK inventory for a verified zipapp.

Only new receipts and an owned temporary test directory are written.
Native project source is executed only through the reviewed, pinned Core verify path.
"""
from __future__ import annotations
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import sys
import tempfile
import uuid
import zipfile

V2_NAME='ENGURU_PILIVE_SOURCE_V2_20261025T145700544425Z_6a6ea0b04143.json'
V3_NAME='ENGURU_PILIVE_SOURCE_LINK_V3_20261025T152600420363Z_f313fd930933.json'
RECEIPT_PINS={V2_NAME:'0dac03bf15579f28bccd3da5fc3daa36fb81c5d368b209216a0c32769d6327a8',
 V3_NAME:'bd64da51f2b708d55c358cf4307f2e746d8ddd33f5814690ed0ff3791652e1ed',
 'ENGURU_PILIVE_KAS_NATIVE_V1_20261025T155028653442Z_17e040e91952.json':'8485dbab50bd10e626db07ff6245feabe07d35f09faa7287b4f9809c026b22a8'}
CORE_PINS={
 'tools/enguru_progress.py':'f3e2610c6e325f6fd620baa84ec412437a015109dde88ac38cab7f08b2a365b4',
 'tools/enguru_progress_adapters.py':'2508089ed161070abe1d520325ff610fd6165c8a726db3ea2a456d772b6faa92',
 'tools/enguru_progress_intelligence.py':'0e3ffb67091ef2c147287448a0855f205992083d541b1d7019e3305d92b0f8b0',
 'governance/plive-p02-user-screen/PLIVE_P02_WORK_CONTRACT_V1.json':'1dc9b0bae00a13672a142fb91f6b1fe603f151bcebaa64482e297029deda7512',
 'governance/plive-p02-user-screen/STATE_V1.json':'ad29d034c8a97be75d69d972fca1c6e7ee207e7f7f1339e79b74e1ce6c40f432',
 'governance/plive-p02-user-screen/WORKLIST_V1.json':'4021dc7486363bc7baf503860969ea23324eabcbd4e3551930a20d79784532d2',
 'governance/progress-core/ENGURU_PROGRESS_CORE_PROJECT_REGISTRY_V1.json':'515748a88acffdd60be6afd4c837a2581a48a3bbeccd74c4a413ae3f986c4a80',
 'governance/progress-core/ENGURU_PROGRESS_CORE_EVIDENCE_POLICY_V1.json':'a3a7f1b2bd100890a6afa1e52be9bf7f87bd02724fcf0c50e522632b24a384ed'}
MUSCLE_PATHS=[
 'tools/enguru_muhendislik_kasi.py','tools/enguru_mk_five_minute_watch.py','tools/enguru_mk_acceptance_v3.py',
 'tools/pilive_learning_adapter_v1.py',
 'governance/enguru-suzgeci/ENGURU_OSI_MUHENDISLIK_KASI_CANLI_KAYIT_V1.md',
 'governance/enguru-suzgeci/learning/ENGURU_MK_KALICI_AMAC_HEDEF_KABUL_V3.md',
 'governance/enguru-suzgeci/learning/ENGURU_MK_5MIN_README.md']

def digest(raw):return hashlib.sha256(raw).hexdigest()

def directory_fd(path):
    path=Path(path).absolute();fd=os.open(path.anchor,os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=child
        return fd
    except BaseException:os.close(fd);raise

def read_file(root,relative,limit=2*1024*1024):
    p=Path(relative)
    if p.is_absolute() or not p.parts or '..' in p.parts:raise ValueError('PATH_SCOPE')
    fd=directory_fd(root)
    try:
        for part in p.parts[:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=child
        child=os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
        with os.fdopen(child,'rb') as f:
            st=os.fstat(f.fileno())
            if not stat.S_ISREG(st.st_mode) or st.st_size>limit:raise ValueError('FILE_TYPE_OR_SIZE')
            raw=f.read(limit+1);end=os.fstat(f.fileno())
            if len(raw)>limit or (st.st_ino,st.st_mtime_ns,st.st_size)!=(end.st_ino,end.st_mtime_ns,end.st_size):raise ValueError('READ_DRIFT')
            return raw
    finally:os.close(fd)

def receipt_pairs(home):
    results=[];desktop=Path(home)/'Desktop'
    for name,pin in RECEIPT_PINS.items():
        try:
            original=read_file(desktop,'AudiV13/'+name,20*1024*1024);copy=read_file(desktop,name,20*1024*1024)
            results.append({'name':name,'originalSha256':digest(original),'copySha256':digest(copy),
              'state':'PASS_ORIGINAL_COPY_PIN' if digest(original)==digest(copy)==pin else 'HOLD_RECEIPT_COPY'})
        except (OSError,ValueError) as exc:results.append({'name':name,'state':'HOLD_RECEIPT_COPY','reason':type(exc).__name__})
    return results

def native_muscle_inventory(home):
    records=[]
    for relative_root in ['Enguru/Projects/Engurulaboratuvari','Enguru/Projects/enguru-mac-engineer']:
        root=Path(home)/relative_root
        for name in MUSCLE_PATHS:
            try:
                raw=read_file(root,name);text=raw.decode('utf-8');scopes={}
                if name.endswith('.py'):
                    tree=ast.parse(text)
                    for node in tree.body:
                        if isinstance(node,ast.Assign):
                            for target in node.targets:
                                if isinstance(target,ast.Name) and target.id in ['TASK_ID','PILIVE_TASK_ID']:
                                    try:scopes[target.id]=ast.literal_eval(node.value)
                                    except ValueError:scopes[target.id]='DYNAMIC_SOURCE_REVIEW_REQUIRED'
                records.append({'rootLabel':Path(relative_root).name,'path':name,'state':'OBSERVED',
                  'sha256':digest(raw),'bytes':len(raw),'declaredScopes':scopes,'contentUtf8':text})
            except FileNotFoundError:records.append({'rootLabel':Path(relative_root).name,'path':name,'state':'MISSING_IN_EXACT_SCOPE'})
            except (OSError,ValueError,UnicodeError,SyntaxError) as exc:records.append({'rootLabel':Path(relative_root).name,'path':name,'state':'HOLD_SOURCE_READ','reason':type(exc).__name__})
    return records

def core_pin_check(root):
    rows=[]
    for name,pin in CORE_PINS.items():
        try:
            actual=digest(read_file(root,name));rows.append({'path':name,'sha256':actual,'match':actual==pin})
        except (OSError,ValueError) as exc:rows.append({'path':name,'match':False,'reason':type(exc).__name__})
    return rows

def native_core_verify(home,workdir):
    root=Path(home)/'Enguru/Projects/Engurulaboratuvari';before=core_pin_check(root)
    if not all(x['match'] for x in before):return {'state':'HOLD_NATIVE_SOURCE_DRIFT','before':before,'executed':False}
    env=dict(os.environ);env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
    p=subprocess.run([sys.executable,'-B','-S',str(root/'tools/enguru_progress.py'),'plive-p02-user-screen','--verify'],
       cwd=workdir,env=env,capture_output=True,text=True,timeout=45)
    after=core_pin_check(root)
    fields={}
    for line in p.stdout.splitlines():
        parts=line.split(maxsplit=1)
        if len(parts)==2:fields[parts[0]]=parts[1]
    required=['worklist','state','itemSetAgreement','singleActivePackage','singleActiveItem','deterministicProjection','evidenceQualification','progressIntegrity']
    good=p.returncode==0 and fields.get('project')=='plive-p02-user-screen' and all(fields.get(k)=='PASS' for k in required) and before==after
    return {'state':'PASS_NATIVE_CORE_VERIFY_READ_ONLY' if good else 'HOLD_NATIVE_CORE_VERIFY','executed':True,
      'returncode':p.returncode,'fields':fields,'stdout':p.stdout[:32768],'stderr':p.stderr[:32768],'before':before,'after':after,
      'officialAcceptance':'UNCHANGED_HOLD'}

def save(home,receipt):
    raw=(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode();desktop=Path(home)/'Desktop'
    name='ENGURU_PILIVE_KAS_NATIVE_V1_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+uuid.uuid4().hex[:12]+'.json'
    fd=directory_fd(desktop);archive=None
    def write(parent):
        f=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
        with os.fdopen(f,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        f=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=parent)
        with os.fdopen(f,'rb') as stream:
            if stream.read()!=raw:raise ValueError('RECEIPT_READBACK')
    try:
        try:os.mkdir('AudiV13',0o700,dir_fd=fd)
        except FileExistsError:pass
        archive=os.open('AudiV13',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
        write(archive);print('ORIGINAL='+str(desktop/'AudiV13'/name),flush=True)
        write(fd);print('DESKTOP_COPY='+str(desktop/name),flush=True)
        print('RECEIPT_SHA256='+digest(raw));print('COPY_SHA256_MATCH=PASS')
    finally:
        if archive is not None:os.close(archive)
        os.close(fd)

def run_package(archive,*,home=None,allow_non_mac=False,execute_core=True):
    """allow_non_mac is an internal isolated test hook; CLI always requires Darwin."""
    home=Path.home() if home is None else Path(home)
    if platform.system()!='Darwin' and not allow_non_mac:raise ValueError('HOLD_MAC_REQUIRED')
    with zipfile.ZipFile(archive) as z:
        manifest=json.loads(z.read('MANIFEST.json'));payload=manifest['files']
        if not isinstance(payload,dict) or len(payload)>30:raise ValueError('MANIFEST_SCOPE')
        with tempfile.TemporaryDirectory(prefix='enguru-pilive-kas-') as temp:
            temp=Path(temp)
            for name,pin in payload.items():
                rel=Path(name)
                if rel.is_absolute() or '..' in rel.parts or not rel.parts:raise ValueError('MANIFEST_PATH')
                raw=z.read('payload/'+name)
                if digest(raw)!=pin:raise ValueError('PACKAGE_SOURCE_SHA')
                out=temp/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
            tests=[]
            for pattern in ['test_enguru_muhendislik_kasi.py','test_enguru_mk_five_minute_watch.py','test_enguru_mk_contract_v3.py','test_pilive_learning_adapter_v1.py','test_pilive_native_learning_probe_v1.py']:
                p=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p',pattern,'-q'],cwd=temp,capture_output=True,text=True,timeout=45)
                logs=p.stdout+p.stderr;counts=re.findall(r'Ran\s+(\d+)\s+tests?',logs)
                tests.append({'suite':pattern,'returncode':p.returncode,'tests':int(counts[-1]) if counts else 0,
                  'state':'PASS' if p.returncode==0 and counts else 'HOLD','outputSha256':digest(logs.encode()),'failureOutput':logs[:16000] if p.returncode else ''})
            core=native_core_verify(home,temp) if execute_core else {'state':'NOT_EXECUTED_ISOLATED_PACKAGE_TEST','executed':False}
            pairs=receipt_pairs(home);inventory=native_muscle_inventory(home)
            ok=all(t['state']=='PASS' for t in tests) and sum(t['tests'] for t in tests)==137 and core['state']=='PASS_NATIVE_CORE_VERIFY_READ_ONLY' and all(p['state']=='PASS_ORIGINAL_COPY_PIN' for p in pairs)
            return {'schema':'enguru.pilive.native-learning-repeat/v1','observedAtUtc':datetime.now(timezone.utc).isoformat(),
              'platform':platform.system(),'packageSourceCommit':manifest['sourceCommit'],'packageManifestSha256':digest(z.read('MANIFEST.json')),
              'tests':tests,'nativeCore':core,'receiptPairs':pairs,'existingNativeMuscle':inventory,
              'state':'PASS_NATIVE_REPEAT_AND_CORE_ONLY' if ok else 'HOLD_NATIVE_REPEAT_REVIEW',
              'canonicalWrites':0,'appLaunches':0,'keychainReads':0,'networkRequests':0,'nativeMuscleWrites':0,
              'temporaryTestWrites':'OWNED_TEMPORARY_DIRECTORY_ONLY','productAcceptance':'HOLD','verifiedFinish':'HOLD'}

def main():
    try:
        if sys.argv[1:]!=['--run']:print('USAGE: python3 -B PACKAGE.pyz --run');return 2
        if platform.system()!='Darwin':print('STATE=HOLD_MAC_REQUIRED');return 2
        result=run_package(Path(sys.argv[0]));save(Path.home(),result)
        print('STATE='+result['state']);print('NATIVE_CORE='+result['nativeCore']['state'])
        print('TESTS='+str(sum(t['tests'] for t in result['tests'])))
        print('CANONICAL_WRITES=0; APP_LAUNCHES=0; NATIVE_MUSCLE_WRITES=0')
        return 0 if result['state']=='PASS_NATIVE_REPEAT_AND_CORE_ONLY' else 2
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,subprocess.SubprocessError) as exc:
        print('STATE=HOLD_NATIVE_PROBE; REASON='+type(exc).__name__);return 2

if __name__=='__main__':raise SystemExit(main())
