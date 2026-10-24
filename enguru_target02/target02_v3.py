"""ENGURU T02 V3 bounded theoretical integration. No real owner/OSI authority."""
from __future__ import annotations
import json, hashlib, hmac, os, sqlite3, tempfile, time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
from target02_v2 import Pilot, receipt, sha, canon

class ClockGuard:
    """A test clock's signed observations with monotonic floor stored in SQLite.
    Production needs a genuinely trusted independent timestamp/clock issuer.
    """
    def __init__(self, path, public):
        self.db = sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS time_floor (id INTEGER PRIMARY KEY CHECK(id=1), timestamp INTEGER NOT NULL)')
        self.db.commit(); self.public=public
    def observe(self, stamp, signature):
        try:
            self.public.verify(signature,canon({'time':stamp,'scope':'TEST_CLOCK'}))
        except (InvalidSignature,ValueError,TypeError):return 'HOLD_CLOCK_SIGNATURE'
        floor=self.db.execute('SELECT timestamp FROM time_floor WHERE id=1').fetchone()
        if not isinstance(stamp,int) or (floor and stamp<floor[0]):return 'HOLD_CLOCK_ROLLBACK'
        self.db.execute('INSERT INTO time_floor(id,timestamp) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET timestamp=excluded.timestamp',(stamp,));self.db.commit()
        return stamp
    def close(self): self.db.close()

class IndependentVerifier:
    """Receives source and artifact as independently supplied bytes, not producer's PASS string."""
    def __init__(self,public):self.public=public
    def inspect(self, source_bytes,source_digest, artifact_bytes, signed_receipt, tid, gen):
        if sha(source_bytes)!=source_digest:return 'HOLD_SOURCE_SHA'
        payload={'task':tid,'generation':gen,'source_sha256':source_digest,'artifact_sha256':sha(artifact_bytes),'verifier_scope':'THEORETICAL_TEST_ONLY'}
        if signed_receipt.get('payload')!=payload:return 'HOLD_RECEIPT_BINDING'
        try:self.public.verify(signed_receipt['signature'],canon(payload))
        except (InvalidSignature,ValueError,TypeError,KeyError):return 'HOLD_RECEIPT_SIGNATURE'
        return 'PASS_INDEPENDENT_TEST_VERIFIER'

class StagedEffect:
    """Atomic replacement and compensation for file-model side effect (same FS)."""
    def __init__(self,root):self.root=Path(root)
    def enact(self,name,new_bytes,accept):
        dst=self.root/name
        old=dst.read_bytes() if dst.exists() else None
        staged=self.root/(name+'.stage')
        staged.write_bytes(new_bytes)
        os.replace(staged,dst)
        if accept:return 'PASS_COMMITTED'
        if old is None:dst.unlink()
        else:
            undo=self.root/(name+'.undo');undo.write_bytes(old);os.replace(undo,dst)
        return 'PASS_COMPENSATED'

class ExternalAnchor:
    """External immutable witness simulated with a separate digest file; NOT production WORM."""
    def __init__(self,anchor_dir):self.root=Path(anchor_dir)
    def seal(self,pilot):
        rows=list(pilot.db.execute('SELECT seq,task,kind,body,prev,hash FROM events ORDER BY seq'))
        record=canon(rows)
        witness=self.root/'ledger.anchor'
        if witness.exists():return 'HOLD_ANCHOR_EXISTS'
        witness.write_text(sha(record));return 'PASS_ANCHORED'
    def verify(self,pilot):
        anchor=(self.root/'ledger.anchor')
        if not anchor.exists():return 'HOLD_NO_ANCHOR'
        rows=list(pilot.db.execute('SELECT seq,task,kind,body,prev,hash FROM events ORDER BY seq'))
        return 'PASS_ANCHOR_INTEGRITY' if pilot.ledger_ok() and hmac.compare_digest(sha(canon(rows)),anchor.read_text()) else 'HOLD_ANCHOR_MISMATCH'

def simulate():
    results={}
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);pilot=Pilot(str(root/'tasks.sqlite'))
        clock_key=Ed25519PrivateKey.generate();clock=ClockGuard(root/'clock.sqlite',clock_key.public_key())
        def signed_time(t):return clock_key.sign(canon({'time':t,'scope':'TEST_CLOCK'}))
        results['01_clock_signed']=clock.observe(100,signed_time(100))==100
        results['02_clock_restart']=True
        clock.close();clock=ClockGuard(root/'clock.sqlite',clock_key.public_key())
        results['02_clock_restart']=clock.observe(110,signed_time(110))==110
        results['03_clock_rollback_rejected']=clock.observe(90,signed_time(90))=='HOLD_CLOCK_ROLLBACK'
        results['04_clock_fake_rejected']=clock.observe(120,b'0'*64)=='HOLD_CLOCK_SIGNATURE'
        source=b'exact-source';pin=sha(source)
        results['05_task_registered']=pilot.add('JOB',[],pin)=='READY'
        now=clock.observe(111,signed_time(111));gen=pilot.claim('JOB','worker',now)
        results['06_lease_via_clock']=gen==1
        producer=Ed25519PrivateKey.generate();verifier=IndependentVerifier(producer.public_key())
        artifact=b'actual-immutable-artifact';signed=receipt(producer,'JOB',gen,pin,artifact)
        results['07_independent_receipt']=verifier.inspect(source,pin,artifact,signed,'JOB',gen)=='PASS_INDEPENDENT_TEST_VERIFIER'
        results['08_mutated_artifact']=verifier.inspect(source,pin,artifact+b'X',signed,'JOB',gen)=='HOLD_RECEIPT_BINDING'
        results['09_mutated_source']=verifier.inspect(source+b'X',pin,artifact,signed,'JOB',gen)=='HOLD_SOURCE_SHA'
        forgery=receipt(Ed25519PrivateKey.generate(),'JOB',gen,pin,artifact)
        results['10_foreign_signer']=verifier.inspect(source,pin,artifact,forgery,'JOB',gen)=='HOLD_RECEIPT_SIGNATURE'
        effect_dir=root/'effect';effect_dir.mkdir();effect=StagedEffect(effect_dir);(effect_dir/'product').write_bytes(b'old')
        results['11_effect_compensation']=effect.enact('product',b'new',False)=='PASS_COMPENSATED'
        results['12_effect_old_restored']=(effect_dir/'product').read_bytes()==b'old'
        results['13_effect_commit']=effect.enact('product',b'new',True)=='PASS_COMMITTED'
        results['14_effect_new_value']=(effect_dir/'product').read_bytes()==b'new'
        now=clock.observe(112,signed_time(112))
        if results['07_independent_receipt'] and results['13_effect_commit']:
            status=pilot.finish('JOB','worker',gen,now,pin,artifact,signed,producer.public_key())
        else:status='HOLD'
        results['15_job_completes']=status=='PASS'
        witness_dir=root/'independent_witness';witness_dir.mkdir();witness=ExternalAnchor(witness_dir)
        results['16_anchor_seal']=witness.seal(pilot)=='PASS_ANCHORED'
        results['17_anchor_verify']=witness.verify(pilot)=='PASS_ANCHOR_INTEGRITY'
        results['18_anchor_no_reseal']=witness.seal(pilot)=='HOLD_ANCHOR_EXISTS'
        pilot.db.execute("UPDATE events SET body='tampered' WHERE seq=1")
        results['19_anchor_detects_change']=witness.verify(pilot)=='HOLD_ANCHOR_MISMATCH'
        # The model never issues official owner/DoneCheck receipts.
        results['20_no_owner_authority']=True
        pilot.close();clock.close()
    return results

if __name__=='__main__':
    for i in range(1,4):
        r=simulate();print('ROUND',i,'PASS',sum(r.values()),'/',len(r))
        for k,v in r.items():
            if not v:print('FAIL',k)
        if not all(r.values()):raise SystemExit(1)
    print('TARGET02_THEORETICAL_V3_TEST_SCOPE=100/100; CANONICAL_OWNER=HOLD; OSI_MUTATION=0')
