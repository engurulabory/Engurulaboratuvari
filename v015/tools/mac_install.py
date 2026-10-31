#!/usr/bin/env python3
"""One isolated app build/start. No old app discovery/mutation, no downloads.

The owner starts this exact action through the supplied launcher. Installation
only creates a new app below this extracted release, never /Applications.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from validate import validate,ROOT


def main():
    if sys.argv[1:]!=['--owner-start-isolated']:raise RuntimeError('EXACT_OWNER_START_REQUIRED')
    if platform.system()!='Darwin' or platform.machine()!='arm64':raise RuntimeError('MAC_ARM64_REQUIRED')
    # The launcher already created a unique directory under AudiV13.
    expected=Path.home()/'Desktop'/'AudiV13'
    if expected not in ROOT.parents or any(p.is_symlink() for p in (ROOT,*ROOT.parents)):
        raise RuntimeError('ISOLATED_AUDIV13_ROOT_REQUIRED')
    validate()
    receipt={'schema':'enguru.v015.mac-install/v1','started':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':str(ROOT),'old_ulak':'UNTOUCHED','pilive':'UNTOUCHED','downloads':0,
        'compile':'NOT_TESTED','install':'NOT_PERFORMED','field':'NOT_TESTED','verified_finish':'HOLD'}
    report=ROOT/'MAC_INSTALL_RECEIPT.json'
    if report.exists():raise RuntimeError('EXISTING_INSTALL_RECEIPT_HOLD')
    def save():
        temp=ROOT/'.mac_receipt.tmp'
        with open(temp,'x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
        os.replace(temp,report)
    try:
        checks=subprocess.run([sys.executable,'-I','-B',str(ROOT/'tools/run_checks.py')],capture_output=True,text=True,timeout=180)
        (ROOT/'MAC_SELF_TEST.log').write_text(checks.stdout+'\n'+checks.stderr)
        receipt['self_test_exit']=checks.returncode
        if checks.returncode!=0:raise RuntimeError('MAC_SELF_TEST_HOLD')
        # Existing toolchain only: no xcode-select --install, pip, model pull.
        check=subprocess.run(['/usr/bin/xcrun','--find','swiftc'],capture_output=True,text=True,timeout=15)
        if check.returncode!=0:raise RuntimeError('EXISTING_XCODE_TOOLCHAIN_REQUIRED')
        app=ROOT/'ENGURU Ulak V015.app'
        if app.exists():raise RuntimeError('APP_ALREADY_EXISTS_HOLD')
        resources=app/'Contents'/'Resources';binary=app/'Contents'/'MacOS'/'Ulak'
        resources.mkdir(parents=True,mode=0o700);binary.parent.mkdir(mode=0o700)
        build=subprocess.run([check.stdout.strip(),'-O','-parse-as-library',str(ROOT/'native/Ulak.swift'),
            '-o',str(binary)],capture_output=True,text=True,timeout=240)
        (ROOT/'MAC_SWIFT_BUILD.log').write_text(build.stdout+'\n'+build.stderr)
        receipt['compile_exit']=build.returncode
        receipt['compile']='PASS' if build.returncode==0 else 'HOLD'
        if build.returncode!=0:raise RuntimeError('SWIFT_BUILD_HOLD_SEE_LOG')
        product=resources/'Product';product.mkdir(mode=0o700)
        manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
        for n in list(manifest['files'])+['SOURCE_MANIFEST.json']:
            target=product/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,target)
        profile=ROOT/'profile';profile.mkdir(mode=0o700)
        (resources/'runtime.json').write_text(json.dumps({'python':sys.executable,'profile':str(profile)}))
        plist={'CFBundleIdentifier':'com.engurumaya.ulak.v015.isolated','CFBundleName':'ENGURU Ulak V015',
               'CFBundleExecutable':'Ulak','CFBundlePackageType':'APPL','CFBundleVersion':'15.1',
               'LSMinimumSystemVersion':'13.0','NSHighResolutionCapable':True}
        (app/'Contents/Info.plist').write_bytes(plistlib.dumps(plist))
        receipt['app_sha256']=hashlib.sha256(binary.read_bytes()).hexdigest();receipt['install']='PASS_ISOLATED_APP_CREATED'
        # Local live model pilot; no generated code executes. Keep failures as HOLD.
        req={'action':'run','profile':str(profile),'command_id':'mac-field-unique-jobs-v015',
             'text':'unique_jobs fonksiyonunu sıra koruyacak şekilde düzelt ve gerçek testlerini çalıştır'}
        field=subprocess.run([sys.executable,'-I','-B',str(ROOT/'cli.py')],input=json.dumps(req),capture_output=True,text=True,timeout=700)
        (ROOT/'MAC_FIELD_RESULT.json').write_text(field.stdout or json.dumps({'state':'HOLD','reason':field.stderr[-2000:]}))
        receipt['field_exit']=field.returncode;receipt['field']='RECEIPT_REVIEW_REQUIRED'
        receipt['field_result_sha256']=hashlib.sha256((ROOT/'MAC_FIELD_RESULT.json').read_bytes()).hexdigest()
        save()
        subprocess.run(['/usr/bin/open',str(app)],check=True)
        print('MAC_RECEIPT='+str(report));print('FIELD_REVIEW=HOLD_OWNER_AND_INDEPENDENT_REVIEW')
    except Exception as e:
        receipt['error']=type(e).__name__+': '+str(e);save();print('STATE=HOLD');print('MAC_RECEIPT='+str(report));raise


if __name__=='__main__':main()
