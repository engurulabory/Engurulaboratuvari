#!/usr/bin/env python3
"""Real regression: stable inode and receipt readback under unsafe path replacement.

Modes: before (original V7/H1-only) and after (isolated patched version).
No local Mac, keys, owner grants or production files are involved.
"""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

product = Path(sys.argv[1]).resolve()
mode = sys.argv[2]
assert mode in ('before','after')

def child_script(path):
    return f'''
import sys,os,json
from pathlib import Path
sys.path.insert(0,{str(path)!r})
import server
server.prepare()
plan=server.make_scaffold('python')
receipt=server.execute(plan['task_id'])
assert receipt['status']=='PASS_SCOPED', receipt
assert server.verify_written_task(plan['task_id'])['match']
assert server.execute(plan['task_id'])['already_executed'] is True
name=plan['path']; target=server.WORKSPACE/name
if {mode!r} == 'before':
    # Deterministic context switch exactly between the legacy is_symlink
    # check and its later path.stat/read_bytes: replace with a real FIFO.
    old=Path.is_symlink
    def attacked(self):
        if self == target:
            target.unlink()
            os.mkfifo(target)
            return False
        return old(self)
    Path.is_symlink=attacked
    server.verify_written_task(plan['task_id'])  # RED: blocks in Path.read_bytes()
    raise AssertionError('Legacy read unexpectedly returned')
else:
    # Live regular readback remains valid and the same task cannot reexecute.
    assert server.verify_written_task(plan['task_id'])['match']
    # Switch to a real FIFO immediately before the new fd open.
    old_open=server.os.open
    hit={{'value':False}}
    def attacked_open(path, flags, *args, **kwargs):
        if path==name and 'dir_fd' in kwargs and not hit['value']:
            hit['value']=True
            target.unlink()
            os.mkfifo(target)
        return old_open(path, flags, *args, **kwargs)
    server.os.open=attacked_open
    result=server.verify_written_task(plan['task_id'])
    assert hit['value'] is True, 'No race injected'
    assert result['status']=='HOLD_INTEGRITY',result
    result2=server.execute(plan['task_id'])
    assert result2['status']=='HOLD_INTEGRITY' and result2['already_executed'], result2
    # Special file remains unmodified; never delete/re-execute automatically.
    assert target.is_fifo()
    print('ATOMIC_READER_REPLAY_FIFO=PASS')
    # Symlink swap must reject without reading target.
    target.unlink()
    outside=server.WORKSPACE.parent/'outside_private.txt'
    outside.write_text('do not read this')
    target.symlink_to(outside)
    result3=server.verify_written_task(plan['task_id'])
    assert result3['status']=='HOLD_INTEGRITY', result3
    assert outside.read_text()=='do not read this'
    print('ATOMIC_READER_SYMLINK_HOLD=PASS')
    # Replaced regular bytes must not pass the stored receipt SHA.
    target.unlink()
    target.write_text('wrong')
    result4=server.verify_written_task(plan['task_id'])
    assert result4['status']=='HOLD_INTEGRITY',result4
    print('ATOMIC_READER_SHA_TAMPER_HOLD=PASS')
'''

with tempfile.TemporaryDirectory(prefix='ulmi_h1_readback_'+mode+'_') as tmp:
    env={**os.environ,'ENGURU_H1_STATE_HOME':str(Path(tmp)/'state')}
    try:
        done=subprocess.run([sys.executable,'-I','-B','-c',child_script(product)],env=env,capture_output=True,text=True,timeout=6 if mode=='after' else 1.2)
    except subprocess.TimeoutExpired:
        if mode=='before':
            print('BASELINE_RED_REAL_FIFO_WAIT=OBSERVED')
            sys.exit(0)
        raise
    if mode=='before':
        print(done.stdout,done.stderr)
        raise SystemExit('BASELINE_RED_NOT_REPRODUCED')
    print(done.stdout,done.stderr)
    if done.returncode != 0:
        raise SystemExit('PATCH_GREEN_FAILED')
    print('AFTER_GREEN=PASS')
