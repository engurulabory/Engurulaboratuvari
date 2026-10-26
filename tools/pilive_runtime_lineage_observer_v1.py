"""Bounded existing MK runtime and historical PiLive lineage observation.

No native module import, runtime activation, SQLite connection, Keychain, network,
app launch or canonical/muscle write. Only a new receipt and its copy are saved.
"""
from __future__ import annotations
import ast
from datetime import datetime,timezone
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import re
import stat
import subprocess
import sys
import zipfile
from tools import pilive_native_learning_probe_v1 as safe

PYTHON_PINS={
 'projection_v6.py':'d9efb5a7ec6c045f697396d566868d09dbec590f45d54c67339dec8ef626118c',
 'snapshot_v52.py':'87dc579efb7f7a60541bc8439f9fc74e06983a10b7f829640d9403ac193c6edf'}
V31_BINARY='32d533bed479434f77f848fd030c4330a2a33447e8e28d281f215bcb7b6db466'
LABEL=re.compile(r'com\.enguru\.mk\.bridge[.A-Za-z0-9_-]*\Z')
HASH=re.compile(r'[a-f0-9]{64}\Z')
ROOT='Enguru/Runtime/MacEngineer'

def constants(raw):
    tree=ast.parse(raw.decode('utf-8'));result={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in {'TASK','TASK_ID','LABEL','RUNTIME','BRANCH','ROOT'}:
                    try:value=ast.literal_eval(node.value)
                    except (ValueError,TypeError):continue
                    if isinstance(value,str) and len(value)<=300:result[target.id]=value
    return result

def zip_sources(raw):
    if len(raw)>32*1024*1024:raise ValueError('ZIP_SIZE_LIMIT')
    rows=[]
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if len(z.infolist())>500:raise ValueError('ZIP_MEMBER_LIMIT')
        budget=0
        for info in sorted(z.infolist(),key=lambda x:x.filename):
            p=Path(info.filename)
            if p.is_absolute() or '..' in p.parts or stat.S_ISLNK(info.external_attr>>16):raise ValueError('ZIP_PATH_SCOPE')
            if p.suffix=='.py' and 'enguru_mk' in p.name:
                budget+=info.file_size
                if info.file_size>1024*1024 or budget>5*1024*1024:raise ValueError('ZIP_SOURCE_LIMIT')
                body=z.read(info)
                rows.append({'member':info.filename,'sha256':safe.digest(body),'bytes':len(body),'scopeConstants':constants(body)})
    return rows

def runtime_record(home,rawpath,expected_sha=None):
    home=Path(home);base=home/ROOT;p=Path(rawpath)
    if not p.is_absolute():raise ValueError('RUNTIME_PATH_ABSOLUTE')
    try:relative=p.relative_to(base)
    except ValueError as exc:raise ValueError('RUNTIME_PATH_SCOPE') from exc
    if p.suffix not in {'.zip','.pyz'}:raise ValueError('RUNTIME_ARCHIVE_TYPE')
    raw=safe.read_file(base,str(relative),32*1024*1024);actual=safe.digest(raw)
    return {'path':str(p),'sha256':actual,'bytes':len(raw),'sourceInventory':zip_sources(raw),
      'installedPinState':'PASS_PIN_MATCH' if isinstance(expected_sha,str) and HASH.fullmatch(expected_sha) and expected_sha==actual else 'HOLD_PIN_UNVERIFIED'}

def read_launch_agents(home):
    folder=Path(home)/'Library/LaunchAgents';fd=safe.directory_fd(folder)
    try:
        names=sorted(os.listdir(fd))
        if len(names)>1000:raise ValueError('LAUNCHAGENT_NAME_LIMIT')
        return [n for n in names if n.endswith('.plist') and LABEL.fullmatch(n[:-6])]
    finally:os.close(fd)

def agent_record(home,name):
    folder=Path(home)/'Library/LaunchAgents'
    data=plistlib.loads(safe.read_file(folder,name));label=data.get('Label')
    if not isinstance(label,str) or not LABEL.fullmatch(label) or name!=label+'.plist':raise ValueError('LAUNCHAGENT_LABEL')
    args=data.get('ProgramArguments',[])
    if not isinstance(args,list) or not all(isinstance(v,str) for v in args):raise ValueError('LAUNCHAGENT_ARGUMENTS')
    env=data.get('EnvironmentVariables',{})
    pin=env.get('ENGURU_MK_INSTALLED_SHA256') if isinstance(env,dict) else None
    if pin is not None and (not isinstance(pin,str) or not HASH.fullmatch(pin)):pin=None
    archives=[v for v in args if Path(v).suffix in {'.zip','.pyz'}]
    result={'label':label,'plistSha256':safe.digest(safe.read_file(folder,name)),
      'runtimeArguments':archives,'otherArgumentCount':len(args)-len(archives),
      'installedSha256':pin,'nonAllowlistedEnvironmentValuesExported':False,'runtimes':[]}
    for path in archives:
        try:result['runtimes'].append(runtime_record(home,path,pin))
        except (OSError,ValueError,UnicodeError,SyntaxError,zipfile.BadZipFile) as exc:result['runtimes'].append({'path':path,'state':'HOLD_RUNTIME_REVIEW','reason':type(exc).__name__})
    # Parse only three public status fields; full launchctl output can contain env data.
    p=subprocess.run(['/bin/launchctl','print',f'gui/{os.getuid()}/{label}'],capture_output=True,text=True,timeout=10)
    fields={}
    for key in ['state','pid','last exit code']:
        match=re.search(r'^\s*'+re.escape(key)+r'\s*=\s*([A-Za-z0-9_-]+)\s*$',p.stdout,re.M)
        if match:fields[key]=match.group(1)
    result['launchd']={'returncode':p.returncode,'fields':fields}
    return result

def bounded_names(root,depth_limit=5,entry_limit=2000):
    queue=[(safe.directory_fd(root),(),0)];count=0
    try:
        while queue:
            fd,prefix,depth=queue.pop()
            try:
                for name in sorted(os.listdir(fd)):
                    count+=1
                    if count>entry_limit:raise ValueError('SEARCH_ENTRY_LIMIT')
                    st=os.stat(name,dir_fd=fd,follow_symlinks=False);parts=prefix+(name,)
                    if stat.S_ISREG(st.st_mode):yield '/'.join(parts)
                    elif stat.S_ISDIR(st.st_mode) and name not in {'.git','node_modules','.build','MacOS','Frameworks'}:
                        if depth<depth_limit:
                            child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);queue.append((child,parts,depth+1))
                        else:raise ValueError('SEARCH_DEPTH_LIMIT')
            finally:os.close(fd)
    finally:
        for fd,_,_ in queue:os.close(fd)

def lineage_inventory(home):
    home=Path(home);roots=[home/'Desktop/AudiV13/ENGURU_PLIVE_V31_IZOLE_ADAY_20261018T213128803170Z',Path('/Applications/ENGURU-PLive-V31.app/Contents/Resources')]
    candidates=[];matches=[];searches=[]
    for root in roots:
        examined=0
        try:
            for relative in bounded_names(root):
                if Path(relative).suffix not in {'.py','.swift','.sh'}:continue
                raw=safe.read_file(root,relative);h=safe.digest(raw);examined+=1
                candidates.append({'path':str(root/relative),'sha256':h,'bytes':len(raw)})
                for name,pin in PYTHON_PINS.items():
                    if h==pin:matches.append({'pinName':name,'path':str(root/relative),'sha256':h,'contentUtf8':raw.decode('utf-8')})
            searches.append({'root':str(root),'filesExamined':examined,'depthLimit':5,'entryLimit':2000,'scope':'BOUNDED_ONLY'})
        except (OSError,ValueError) as exc:searches.append({'root':str(root),'filesExamined':examined,'state':'HOLD_SEARCH_SCOPE','reason':type(exc).__name__})
    # Historical package pin names provide this additional bounded top-level namespace.
    temp=Path('/private/tmp');examined=0
    try:
        fd=safe.directory_fd(temp)
        try:
            names=sorted(os.listdir(fd))
            if len(names)>5000:raise ValueError('TEMP_NAME_LIMIT')
            for name in names:
                if not re.search(r'(plive|pilive|p02|projection|snapshot)',name,re.I) or not name.endswith(('.py','.swift')):continue
                st=os.stat(name,dir_fd=fd,follow_symlinks=False)
                if not stat.S_ISREG(st.st_mode) or st.st_uid!=os.getuid():continue
                examined+=1
                if examined>100:raise ValueError('TEMP_SOURCE_LIMIT')
                raw=safe.read_file(temp,name);h=safe.digest(raw)
                candidates.append({'path':str(temp/name),'sha256':h,'bytes':len(raw)})
                for key,pin in PYTHON_PINS.items():
                    if h==pin:matches.append({'pinName':key,'path':str(temp/name),'sha256':h,'contentUtf8':raw.decode('utf-8')})
        finally:os.close(fd)
        searches.append({'root':str(temp),'filesExamined':examined,'scope':'OWNER_UID_NAME_FILTER_TOP_LEVEL_ONLY'})
    except (OSError,ValueError) as exc:searches.append({'root':str(temp),'filesExamined':examined,'state':'HOLD_SEARCH_SCOPE','reason':type(exc).__name__})
    return {'searches':searches,'candidates':candidates,'matchedPythonPins':matches,
      'swiftBinaryBuildBinding':'HOLD_EXACT_BUILD_EVIDENCE_REQUIRED','globalAbsence':'NOT_CLAIMED'}

def observe(home):
    home=Path(home);agents=[];errors=[]
    try:names=read_launch_agents(home)
    except (OSError,ValueError) as exc:names=[];errors.append({'scope':'LAUNCHAGENT_NAMES','reason':type(exc).__name__})
    for name in names:
        try:agents.append(agent_record(home,name))
        except (OSError,ValueError,TypeError,subprocess.SubprocessError) as exc:errors.append({'scope':name,'reason':type(exc).__name__})
    database=home/ROOT/'state/mk-bridge/bridge.sqlite';db={}
    try:
        parent=safe.directory_fd(database.parent)
        try:
            st=os.stat(database.name,dir_fd=parent,follow_symlinks=False)
            db={'state':'SQLITE_FILE_METADATA_OBSERVED' if stat.S_ISREG(st.st_mode) else 'HOLD_FILE_TYPE','bytes':st.st_size,'modifiedNs':st.st_mtime_ns,'connectionsOpened':0}
        finally:os.close(parent)
    except OSError as exc:db={'state':'HOLD_EXACT_SQLITE_PATH','reason':type(exc).__name__,'connectionsOpened':0}
    bundle=Path('/Applications/ENGURU-PLive-V31.app');binary={}
    try:
        raw=safe.read_file(bundle,'Contents/MacOS/PLive',128*1024*1024);h=safe.digest(raw)
        binary={'sha256':h,'bytes':len(raw),'historicalBinaryMatch':h==V31_BINARY,
          'buildBinding':'HOLD_EXACT_SOURCE_BUILD_MANIFEST'}
        info=plistlib.loads(safe.read_file(bundle,'Contents/Info.plist'))
        binary['bundleIdentity']={k:info.get(k) for k in ['CFBundleIdentifier','CFBundleVersion','CFBundleExecutable']}
        p=subprocess.run(['/usr/bin/strings',str(bundle/'Contents/MacOS/PLive')],capture_output=True,text=True,timeout=10)
        binary['sourceNameStrings']=[line[:300] for line in p.stdout.splitlines() if re.search(r'(plive|pilive|p02|snapshot|projection).*\.(swift|py)',line,re.I)][:80]
    except (OSError,ValueError,subprocess.SubprocessError) as exc:binary={'state':'HOLD_BINARY_IDENTITY','reason':type(exc).__name__}
    return {'schema':'enguru.pilive.runtime-lineage-observation/v1','observedAtUtc':datetime.now(timezone.utc).isoformat(),
      'agents':agents,'existingLedgerMetadata':db,'lineage':lineage_inventory(home),'priorReceiptPairs':safe.receipt_pairs(home),
      'installedBinary':binary,'atomicity':'PER_FILE_FSTAT_BRACKET_ONLY; MULTI_FILE_CAPTURE_NOT_ATOMIC',
      'errors':errors,'state':'OBSERVED_REQUIRES_SOURCE_REVIEW','canonicalWrites':0,'nativeMuscleWrites':0,
      'keychainReads':0,'networkRequests':0,'appLaunches':0,'runtimeActivations':0,'sqliteConnections':0,'verifiedFinish':'HOLD'}

def main():
    if sys.argv[1:]!=['--run']:print('USAGE: python3 -B PACKAGE.pyz --run');return 2
    if sys.platform!='darwin':print('STATE=HOLD_MAC_REQUIRED');return 2
    try:
        with zipfile.ZipFile(sys.argv[0]) as z:
            raw=z.read('MANIFEST.json');manifest=json.loads(raw)
            for name,pin in manifest['files'].items():
                if safe.digest(z.read(name))!=pin:raise ValueError('PACKAGE_SOURCE_SHA')
            source=manifest['sourceCommit'];manifest_sha=safe.digest(raw)
        result=observe(Path.home())
        result['observerSourceCommit']=source;result['packageManifestSha256']=manifest_sha
        safe.save(Path.home(),result)
        print('STATE='+result['state']);print('MK_AGENTS_OBSERVED='+str(len(result['agents'])))
        print('CANONICAL_WRITES=0; NATIVE_MUSCLE_WRITES=0; SQLITE_CONNECTIONS=0')
        return 0
    except (OSError,ValueError,TypeError,KeyError,zipfile.BadZipFile,subprocess.SubprocessError) as exc:
        print('STATE=HOLD_RUNTIME_LINEAGE; REASON='+type(exc).__name__);return 2

if __name__=='__main__':raise SystemExit(main())
