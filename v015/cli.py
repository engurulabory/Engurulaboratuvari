#!/usr/bin/env python3
"""Native app IPC: one JSON request on stdin, one JSON response on stdout."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import json
import hashlib
from enguru_core.contracts import strict_json, Rejected
from enguru_core.kernel import Kernel
from enguru_core.roles import LocalRoles


def verify_release():
    root=Path(__file__).resolve().parent
    manifest=json.loads((root/'SOURCE_MANIFEST.json').read_text())
    for name,sha in manifest['files'].items():
        p=root/name
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
            raise Rejected('RELEASE_SOURCE_DRIFT: '+name)


def main():
    verify_release()
    request=strict_json(sys.stdin.read(100001))
    if not isinstance(request,dict) or not isinstance(request.get('action'),str):raise Rejected('IPC_REQUEST')
    profile=Path(request['profile']).absolute()
    # CLI is a local owner bridge, not network IPC; native app supplies its private profile.
    k=Kernel(profile,LocalRoles())
    try:
        action=request['action']
        if action=='run':
            if set(request)!={'action','profile','command_id','text'}:raise Rejected('IPC_FIELDS')
            result=k.execute(request['command_id'],request['text'])
        elif action=='snapshot':result=k.snapshot()
        elif action=='pause':k.ledger.control(True);result=k.snapshot()
        elif action=='resume':k.ledger.control(False);result=k.snapshot()
        elif action=='recover':result={'recovered':k.recover(),'state':'HOLD','message':'Salt okunur uzlaştırma gerekli.'}
        elif action=='model':result={'digest':k.roles.identity(),'model':'qwen3:14b'}
        else:raise Rejected('UNKNOWN_IPC_ACTION')
        print(json.dumps({'ok':True,'projection':result},ensure_ascii=False))
    finally:k.close()


if __name__=='__main__':
    try:main()
    except Exception as e:
        print(json.dumps({'ok':False,'state':'HOLD','reason':type(e).__name__+': '+str(e)},ensure_ascii=False))
        sys.exit(1)
