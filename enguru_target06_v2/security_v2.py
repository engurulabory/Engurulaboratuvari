import hashlib, json, sqlite3, tempfile, threading
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

def h(v): return hashlib.sha256(v).hexdigest()
def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
class Ledger:
 def __init__(self,db,anchor):
  self.db=sqlite3.connect(db,isolation_level=None,timeout=5,check_same_thread=False)
  self.db.execute('PRAGMA journal_mode=WAL')
  self.db.execute('CREATE TABLE IF NOT EXISTS receipts(nonce TEXT PRIMARY KEY, payload BLOB, digest TEXT, previous TEXT)')
  self.anchor=Path(anchor)
 def accept(self,payload,signature,keys,now,source,expected_head):
  p=json.loads(payload)
  if p.get('head')!=expected_head or source!=p.get('source_sha') or h(p['source_bytes'].encode())!=source:return 'HOLD_SOURCE'
  policy=keys.get(p.get('key_id'))
  if not policy or not (policy['start']<=now<policy['end']) or policy['revoked']:return 'HOLD_KEY'
  if p.get('scope')!='THEORETICAL_MACHINE_VERIFY':return 'HOLD_SCOPE'
  try:policy['public'].verify(signature,payload)
  except InvalidSignature:return 'HOLD_SIGNATURE'
  self.db.execute('BEGIN IMMEDIATE')
  try:
   prior=self.db.execute('SELECT digest FROM receipts ORDER BY rowid DESC LIMIT 1').fetchone()
   previous=prior[0] if prior else '0'*64
   digest=h(previous.encode()+payload+signature)
   self.db.execute('INSERT INTO receipts VALUES(?,?,?,?)',(p['nonce'],payload,digest,previous))
   self.db.execute('COMMIT')
   return 'PASS'
  except sqlite3.IntegrityError:
   self.db.execute('ROLLBACK');return 'HOLD_REPLAY'
 def witness(self):
  records=self.db.execute('SELECT digest,previous,payload FROM receipts ORDER BY rowid').fetchall()
  last='0'*64
  for digest,previous,payload in records:
   if previous!=last:return 'HOLD_CHAIN'
   last=digest
  self.anchor.write_text(last)
  return last
 def verify_anchor(self):
  records=self.db.execute('SELECT digest,previous,payload FROM receipts ORDER BY rowid').fetchall()
  if not self.anchor.exists():return 'HOLD_NO_WITNESS'
  prev='0'*64
  for digest,previous,payload in records:
   if previous!=prev:return 'HOLD_CHAIN'
   prev=digest
  return 'PASS' if self.anchor.read_text()==prev else 'HOLD_WITNESS'
 def close(self):self.db.close()

def run():
 checks={}
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);ledger=Ledger(root/'db',root/'witness');k1=Ed25519PrivateKey.generate();k2=Ed25519PrivateKey.generate();now=100
  keys={'k1':{'public':k1.public_key(),'start':0,'end':200,'revoked':False},'k2':{'public':k2.public_key(),'start':80,'end':300,'revoked':False}}
  source='canonical bytes';sha=h(source.encode());head='a'*40
  def make(key='k1',nonce='n1',scope='THEORETICAL_MACHINE_VERIFY',src=source,commit=head):
   p=canonical({'nonce':nonce,'key_id':key,'scope':scope,'source_bytes':src,'source_sha':h(src.encode()),'head':commit})
   return p,(k1 if key=='k1' else k2).sign(p)
  payload,sig=make()
  checks['01_real_signature_and_canonical_source']=ledger.accept(payload,sig,keys,now,sha,head)=='PASS'
  checks['02_replay_atomic']=ledger.accept(payload,sig,keys,now,sha,head)=='HOLD_REPLAY'
  checks['03_source_pin']=ledger.accept(*make(nonce='n2',src='mutated'),keys,now,sha,head)=='HOLD_SOURCE'
  checks['04_wrong_head']=ledger.accept(*make(nonce='n3',commit='b'*40),keys,now,sha,head)=='HOLD_SOURCE'
  checks['05_scope']=ledger.accept(*make(nonce='n4',scope='OWNER_APPROVED'),keys,now,sha,head)=='HOLD_SCOPE'
  forged,fs=make(nonce='n5');fs=k2.sign(forged)
  checks['06_wrong_key']=ledger.accept(forged,fs,keys,now,sha,head)=='HOLD_SIGNATURE'
  checks['07_witness_created']=len(ledger.witness())==64
  checks['08_anchor_valid']=ledger.verify_anchor()=='PASS'
  ledger.anchor.write_text('0'*64)
  checks['09_anchor_tamper']=ledger.verify_anchor()=='HOLD_WITNESS'
  ledger.witness()
  keys['k1']['revoked']=True
  checks['10_revoke']=ledger.accept(*make(nonce='n6'),keys,now,sha,head)=='HOLD_KEY'
  checks['11_rotate']=ledger.accept(*make(key='k2',nonce='n7'),keys,now,sha,head)=='PASS'
  checks['12_expired']=ledger.accept(*make(key='k2',nonce='n8'),keys,301,sha,head)=='HOLD_KEY'
  checks['13_not_before']=ledger.accept(*make(key='k2',nonce='n9'),keys,79,sha,head)=='HOLD_KEY'
  checks['14_new_anchor']=len(ledger.witness())==64 and ledger.verify_anchor()=='PASS'
  ledger.close()
  reopened=Ledger(root/'db',root/'witness')
  checks['15_restart_anchor']=reopened.verify_anchor()=='PASS'
  checks['16_restart_replay']=reopened.accept(*make(key='k2',nonce='n7'),keys,now,sha,head)=='HOLD_REPLAY'
  checks['17_no_owner_grant']=all(json.loads(x[0])['scope']=='THEORETICAL_MACHINE_VERIFY' for x in reopened.db.execute('SELECT payload FROM receipts'))
  checks['18_two_valid_records']=reopened.db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0]==2
  reopened.close()
 return checks
if __name__=='__main__':
 for n in range(1,4):
  c=run();print('ROUND',n,'PASS',sum(c.values()),'TOTAL',len(c));
  if not all(c.values()):print('FAILED',[k for k,v in c.items() if not v]);raise SystemExit(1)
 print('STATE=PASS_BOUNDED_THEORETICAL_V2')
