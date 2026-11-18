#!/usr/bin/env python3
"""Negative gates: actual byte tampering must reject unverified V22 evidence.

Runs in disposable local working copy. Restores each file in finally.
"""
from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parents[1]
run=R/'TESTS/verify_v22_attested_progress.py'

def call():
    return subprocess.run([sys.executable,str(run)],cwd=R,capture_output=True,text=True,timeout=10)

base=call()
assert base.returncode==0,(base.stdout,base.stderr)
print('PASS_BASELINE_17_PROOF_FAMILIES')

def scenario(name,file,transform):
    original=file.read_bytes()
    try:
        patched=transform(original)
        assert patched!=original, name
        file.write_bytes(patched)
        result=call()
        assert result.returncode!=0,(name,result.stdout,result.stderr)
        print('PASS_ADVERSARIAL_'+name, 'DENIED', result.returncode)
    finally:
        file.write_bytes(original)

scenario('IMMUTABLE_V22_SHA',R/'ORIGINALS/V22_IMMUTABLE_SOURCE.json',lambda b:b.replace(b'"task_count": 12',b'"task_count": 13'))
scenario('IMMUTABLE_ABC_SHA',R/'ORIGINALS/PILOT_ABC_IMMUTABLE_SOURCE.json',lambda b:b.replace(b'"execution_grant": null',b'"execution_grant": "FAKE"',1))
scenario('W04_LOG_TAMPER',R/'EVIDENCE/W04_FIFO_GREEN_AFTER_PATCH.log',lambda b:b.replace(b'W04_FIFO_NONBLOCK=PASS',b'W04_FIFO_NONBLOCK=FAKE'))
scenario('W04_SOURCE_PATCH_REMOVAL',R/'PRODUCT/chat_bridge.py',lambda b:b.replace(b' | os.O_NONBLOCK',b''))
scenario('V5_SAFARI_FALSE_PASS',R/'EVIDENCE/OWNER_V5_SAFARI_UAT_RAW.json',lambda b:b.replace(b'"status": "PASS"',b'"status": "FAIL"',1))
after=call()
assert after.returncode==0,(after.stdout,after.stderr)
print('PASS_BASELINE_RESTORED')
print('W02_NEGATIVE_ADVERSARIAL 7 / 7')
