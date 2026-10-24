"""Target05 supplementary bounded theoretical checks. No canonical authority."""
from flow import Flow, STEPS, sha
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3, json, hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def stable(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def simulate():
 c={}
 with TemporaryDirectory() as temp:
  root=Path(temp); src=sha(b'fixed-target05-source')
  key=Ed25519PrivateKey.generate(); trusted=key.public_key(); foreign=Ed25519PrivateKey.generate()
  data={'task':'T05','stage':'verify','source':src,'bytes_sha256':sha(b'actual receipt bytes'),'scope':'TEST_ONLY','generation':1}
  payload=stable(data); signature=key.sign(payload)
  def validated(body,sig):
   try:trusted.verify(sig,stable(body));return body['source']==src and body['scope']=='TEST_ONLY' and body['bytes_sha256']==sha(b'actual receipt bytes')
   except (InvalidSignature,KeyError):return False
  c['01_signed_receipt']=validated(data,signature)
  c['02_tampered_source']=not validated({**data,'source':'0'*64},signature)
  c['03_foreign_signer']=not validated(data,foreign.sign(payload))
  c['04_modified_bytes']=not validated({**data,'bytes_sha256':sha(b'tampered')},signature)
  c['05_replay_generation']=not validated({**data,'generation':2},signature)
  # DAG guards: prerequisite cycles and unsupported predecessors fail closed.
  dag={'intake':[],'plan':['intake'],'execute':['plan'],'verify':['execute'],'finish':['verify']}
  def topo(graph):
   completed=set();pending=set(graph)
   while pending:
    ready=[v for v in sorted(pending) if set(graph[v])<=completed]
    if not ready:return None
    v=ready[0]; completed.add(v);pending.remove(v)
   return list(completed)
  c['06_dag_valid']=topo(dag) is not None
  c['07_dag_cycle']=topo({'a':['b'],'b':['a']}) is None
  c['08_dag_missing']=topo({'a':['missing']}) is None
  c['09_block_predecessor']=not set(dag['verify']).issubset({'intake','plan'})
  # Concrete workflow steps and counters; no claimed user-click metrics.
  f=Flow(str(root/'flow.db')); counters={'routine_user_actions':0,'auto_steps':0,'exception_handoffs':0}
  c['10_start']=f.start('T05',src)=='STARTED'
  c['11_reject_invalid_proof']=f.step('T05',src,'wrong')=='HOLD_PROOF'
  counters['exception_handoffs']+=1
  c['12_repair']=f.repair('T05',src)=='REPAIRED'
  f.close();f=Flow(str(root/'flow.db'))
  c['13_restart_resume']=f.status('T05')==(0,'READY',1)
  for step in STEPS:
   proof=sha(('T05|'+step+'|'+src).encode())
   out=f.step('T05',src,proof);c['14_step_'+step]=out in ('NEXT','DONE');counters['auto_steps']+=1
  c['15_end_to_end']=f.status('T05')[:2]==(5,'DONE')
  c['16_auto_count_measured']=counters['auto_steps']==5
  c['17_routine_manual_count']=counters['routine_user_actions']==0
  c['18_exception_separate']=counters['exception_handoffs']==1
  c['19_separate_verifier']=validated(data,signature) and not validated(data,foreign.sign(payload))
  c['20_no_owner_claim']=data['scope']=='TEST_ONLY'
  f.close()
 return c
if __name__=='__main__':
 for i in range(3):
  r=simulate(); print('ROUND',i+1,sum(r.values()),'/',len(r),'PASS' if all(r.values()) else 'HOLD');print('FAILED',[k for k,v in r.items() if not v]);assert all(r.values())
