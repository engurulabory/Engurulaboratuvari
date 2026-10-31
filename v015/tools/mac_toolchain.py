"""Explicit existing SDK/toolchain selection; never changes developer settings."""
import json
from pathlib import Path
import subprocess

TARGET='arm64-apple-macosx13.0'


def prepare(root):
    root=Path(root);diagnostics={'target':TARGET,'commands':[],'state':'HOLD'}
    def command(args,timeout=20):
        result=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
        diagnostics['commands'].append({'argv':args,'exit':result.returncode,
                                        'stdout':result.stdout,'stderr':result.stderr})
        if result.returncode!=0:raise RuntimeError('EXISTING_TOOLCHAIN_COMMAND_HOLD')
        return result.stdout.strip()
    try:
        compiler=command(['/usr/bin/xcrun','--sdk','macosx','--find','swiftc'])
        sdk=command(['/usr/bin/xcrun','--sdk','macosx','--show-sdk-path'])
        version=command(['/usr/bin/xcrun','--sdk','macosx','--show-sdk-version'])
        compiler_version=command([compiler,'--version'])
        if not Path(compiler).is_file() or not Path(sdk).is_dir():
            raise RuntimeError('EXISTING_COMPILER_AND_SDK_REQUIRED')
        flags=['-sdk',sdk,'-target',TARGET,'-swift-version','5']
        probe=root/'MAC_TOOLCHAIN_PROBE.swift'
        with probe.open('x') as f:f.write('import Foundation\nimport SwiftUI\n')
        command([compiler,*flags,'-typecheck',str(probe)],timeout=90)
        diagnostics.update(state='PASS_SCOPED_IMPORT_TYPECHECK',compiler=compiler,sdk=sdk,
                           sdk_version=version,compiler_version=compiler_version,flags=flags)
        return compiler,flags
    except Exception as e:
        diagnostics['error']=type(e).__name__+': '+str(e)
        raise
    finally:
        with (root/'MAC_TOOLCHAIN.json').open('x') as f:json.dump(diagnostics,f,ensure_ascii=False,indent=2)
