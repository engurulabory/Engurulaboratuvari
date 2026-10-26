"""Build and open an isolated read-only candidate only on explicit --build-and-open.

No /Applications install, canonical write, acceptance promotion or old app mutation.
The whole source package is SHA-locked by the user Terminal handoff.
"""
from datetime import datetime, timezone
import hashlib
import base64
import json
import os
from pathlib import Path
import platform
import plistlib
import re
import shutil
import subprocess
import sys
import time
import uuid
from tools import pilive_native_learning_probe_v1 as safe

READER_FILES=['tools/pilive_native_learning_probe_v1.py','tools/pilive_portfolio_probe_v1.py',
              'tools/pilive_core_snapshot_adapter_v1.py','tools/pilive_screen_wire_v1.py',
              'tools/pilive_live_reader_v1.py']

class NativeCommandHold(ValueError):
    def __init__(self, argv, result):
        super().__init__('HOLD_COMMAND_'+Path(argv[0]).name)
        self.diagnostic={'argv':argv,'returncode':result.returncode,'outputTail':(result.stdout+result.stderr)[-6000:],'visibility':'PRIVATE_RECEIPT_ONLY'}

def run_command(argv, timeout=240):
    result=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
    output=result.stdout+result.stderr
    if result.returncode:raise NativeCommandHold(argv,result)
    return {'argv':argv,'returncode':0,'outputSha256':safe.digest(output.encode()),'output':output,'stdout':result.stdout}

def reader_resources(source, destination):
    destination.mkdir(parents=True)
    pins={}
    for relative in READER_FILES:
        raw=safe.read_file(source,relative);target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);pins[relative]=safe.digest(raw)
    raw=safe.read_file(source,'tools/pilive_reader_entry_v1.py');(destination/'launch_reader.py').write_bytes(raw);pins['launch_reader.py']=safe.digest(raw)
    raw=json.dumps(pins,sort_keys=True,separators=(',',':')).encode();(destination/'READER_MANIFEST.json').write_bytes(raw)
    return safe.digest(raw)

def validate_frame(frame, expected_binary_sha):
    if frame.get('schema')!='enguru.pilive.visible-frame/v1' or frame.get('windowVisible') is not True:raise ValueError('HOLD_VISIBLE_WINDOW')
    packet=json.loads(base64.b64decode(frame['readerPacketBase64'],validate=True));identity=packet['identity'];observation=packet['observation'];snapshot=observation['snapshot']
    from tools.pilive_live_reader_v1 import packet as export_packet
    if packet!=export_packet(observation):raise ValueError('HOLD_FRAME_WIRE_BINDING')
    if frame['projectionDigest']!=snapshot['projectionDigest'] or frame['sourceRevision']!=snapshot['sourceRevision']:raise ValueError('HOLD_FRAME_SOURCE')
    if frame['projectIds']!=[r['projectId'] for r in snapshot['projects']] or frame['qualifiedCounters']!=snapshot['factCoverage']['qualifiedCounters']:raise ValueError('HOLD_FRAME_PROJECT_SET')
    for field in ('sourceReadAt','adapterBuiltAt'):
        if frame[field]!=snapshot[field]:raise ValueError('HOLD_FRAME_TIME')
    if not datetime.fromisoformat(frame['sourceReadAt'])<=datetime.fromisoformat(frame['adapterBuiltAt'])<=datetime.fromisoformat(frame['uiRenderedAt'].replace('Z','+00:00')):raise ValueError('HOLD_FRAME_TIME_ORDER')
    if frame.get('humanAcceptance')!='NOT_ASSESSED' or frame.get('verifiedFinish')!='HOLD':raise ValueError('HOLD_ACCEPTANCE_BOUNDARY')
    if not re.fullmatch('[a-f0-9]{64}',expected_binary_sha):raise ValueError('HOLD_BINARY_ID')
    return {'state':'PASS_SOURCE_TO_VISIBLE_FRAME_ONLY','productAcceptance':'HOLD','humanAcceptance':'NOT_ASSESSED','verifiedFinish':'HOLD'}

def build_and_open(source, home):
    if platform.system()!='Darwin':raise ValueError('HOLD_MAC_REQUIRED')
    source=Path(source).resolve();home=Path(home)
    audi=home/'Desktop/AudiV13';fd=safe.directory_fd(audi);os.close(fd)
    session=audi/('ENGURU_PILIVE_V4_CANDIDATE_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+uuid.uuid4().hex[:8]);session.mkdir(mode=0o700)
    recipe=[];receipt={'schema':'enguru.pilive.native-ui-candidate/v1','state':'HOLD_BUILD_OR_FIELD','canonicalWrites':0,'nativeMuscleWrites':0,'installedAppWrites':0,'appLaunches':0,'productAcceptance':'HOLD','humanAcceptance':'NOT_ASSESSED','verifiedFinish':'HOLD'}
    try:
        # Preserve exact delivered sources in the unique session before compilation.
        shutil.copytree(source,session/'source',ignore=shutil.ignore_patterns('__pycache__','.build','.git'))
        source=session/'source';manifest=json.loads((source/'MANIFEST.json').read_text());receipt['packageSourceCommit']=manifest['sourceCommit'];receipt['packageManifestSha256']=safe.digest((source/'MANIFEST.json').read_bytes())
        receipt['sourcePins']=manifest['files']
        for path,pin in manifest['files'].items():
            if safe.digest(safe.read_file(source,path))!=pin:raise ValueError('HOLD_DELIVERED_SOURCE_DRIFT')
        package=source/'swift/PiLivePresentation'
        version=run_command(['/usr/bin/xcrun','swift','--version']);receipt['buildToolchain']=version['output'].strip()
        print('STEP=NATIVE_SWIFT_TESTS',flush=True)
        tests=run_command(['/usr/bin/xcrun','swift','test','--package-path',str(package)],timeout=600);recipe.append({k:v for k,v in tests.items() if k not in ('output','stdout')})
        counts=[int(x) for x in re.findall(r'Executed (\d+) tests, with 0 failures',tests['output'])]
        if not counts or max(counts)==0:raise ValueError('HOLD_NATIVE_TEST_COUNT')
        receipt['nativeSwiftTests']=max(counts)
        print('STEP=BUILD_RELEASE_CANDIDATE',flush=True)
        build=run_command(['/usr/bin/xcrun','swift','build','--package-path',str(package),'-c','release'],timeout=600);recipe.append({k:v for k,v in build.items() if k not in ('output','stdout')})
        binary_folder=run_command(['/usr/bin/xcrun','swift','build','--package-path',str(package),'-c','release','--show-bin-path'])['stdout'].strip()
        app=session/'ENGURU-PiLive-V4-READONLY.app';macos=app/'Contents/MacOS';macos.mkdir(parents=True);resources=app/'Contents/Resources';resources.mkdir()
        shutil.copyfile(Path(binary_folder)/'PiLive',macos/'PiLive');(macos/'PiLive').chmod(0o755)
        reader_pin=reader_resources(source,resources/'reader')
        info={'CFBundleIdentifier':'local.enguru.pilive.v4.candidate.'+uuid.uuid4().hex,'CFBundleName':'ENGURU PiLive V4','CFBundleExecutable':'PiLive','CFBundlePackageType':'APPL','CFBundleVersion':'1','CFBundleShortVersionString':'4.0','LSMinimumSystemVersion':'13.0','NSHighResolutionCapable':True,'PythonExecutable':sys.executable,'ReaderManifestSHA256':reader_pin,'SessionDirectory':str(session)}
        (app/'Contents/Info.plist').write_bytes(plistlib.dumps(info))
        unsigned_sha=safe.digest((macos/'PiLive').read_bytes())
        sign=run_command(['/usr/bin/codesign','--force','--sign','-','--timestamp=none',str(app)]);recipe.append({k:v for k,v in sign.items() if k not in ('output','stdout')})
        verify=run_command(['/usr/bin/codesign','--verify','--strict',str(app)]);recipe.append({k:v for k,v in verify.items() if k not in ('output','stdout')})
        receipt.update(buildRecipe=recipe,readerManifestSha256=reader_pin,preSigningBinarySha256=unsigned_sha,binarySha256=safe.digest((macos/'PiLive').read_bytes()),signature='ADHOC_ONLY_NOT_OWNER_AUTHORITY',signatureVerification='PASS_STRICT_LOCAL_CANDIDATE',appPath=str(app))
        print('STEP=OPEN_ISOLATED_CANDIDATE',flush=True)
        run_command(['/usr/bin/open','-n',str(app)]);receipt['appLaunches']=1
        end=time.monotonic()+120;frame_path=session/'VISIBLE_FRAME.json'
        while time.monotonic()<end and not frame_path.exists():time.sleep(0.5)
        if not frame_path.exists():raise ValueError('HOLD_VISIBLE_FRAME_NOT_OBSERVED')
        raw=safe.read_file(session,'VISIBLE_FRAME.json',4*1024*1024);frame=json.loads(raw)
        verdict=validate_frame(frame,receipt['binarySha256']);receipt.update(verdict);receipt['visibleFrame']=frame;receipt['visibleFrameSha256']=safe.digest(raw)
        if safe.digest((macos/'PiLive').read_bytes())!=receipt['binarySha256']:raise ValueError('HOLD_BINARY_DRIFT')
    except Exception as exc:
        if isinstance(exc,NativeCommandHold):receipt['privateDiagnostic']=exc.diagnostic
        failure=session/'READER_FAILURE.json'
        if failure.exists():
            try:receipt['privateReaderFailure']=json.loads(safe.read_file(session,'READER_FAILURE.json',4*1024*1024))
            except (OSError,ValueError):pass
        receipt['state']='HOLD_BUILD_OR_FIELD';receipt['reason']=str(exc) if re.fullmatch('HOLD_[A-Z_a-z0-9]+',str(exc)) else type(exc).__name__
    safe.save(home,receipt)
    print('STATE='+receipt['state']);print('APP_LAUNCHES='+str(receipt['appLaunches']));print('PRODUCT_ACCEPTANCE=HOLD; VERIFIED_FINISH=HOLD')
    return 0 if receipt['state']=='PASS_SOURCE_TO_VISIBLE_FRAME_ONLY' else 2
