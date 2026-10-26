#!/usr/bin/env python3
"""V6.9 common Pilot functional contract, review-stage; test authority only."""
import hashlib,json,sqlite3,sys,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
def digest(data):return hashlib.sha256(data).hexdigest()
def stable(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def manifest():return json.loads((HERE/'source_manifest.json').read_text())
class Pilot:
 def __init__(self,path):
  self.db=sqlite3.connect(path,isolation_level=None,timeout=10)
  self.db.execute('CREATE TABLE IF NOT EXISTS task(id TEXT PRIMARY KEY,goal INTEGER,source TEXT,state TEXT,proof TEXT)')
  self.db.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,task TEXT,kind TEXT,body TEXT,previous TEXT,digest TEXT)')
 def add(self,task,goal,source):
  records=manifest()
  if not (1<=goal<=len(records)) or records[goal-1]['source_sha256']!=source:return 'HOLD_SOURCE'
  self.db.execute('BEGIN IMMEDIATE')
  try:
   if self.db.execute("SELECT 1 FROM task WHERE state='ACTIVE'").fetchone():self.db.execute('ROLLBACK');return 'HOLD_ACTIVE'
   if self.db.execute('SELECT 1 FROM task WHERE id=?',(task,)).fetchone():self.db.execute('ROLLBACK');return 'HOLD_DUPLICATE'
   self.db.execute("INSERT INTO task VALUES (?,?,?,'ACTIVE',NULL)",(task,goal,source))
   self.event(task,'START',{'goal':goal,'source':source})
   self.db.execute('COMMIT');return 'ACTIVE'
  except BaseException:self.db.execute('ROLLBACK');raise
 def event(self,task,kind,body):
  last=self.db.execute('SELECT digest FROM events ORDER BY seq DESC LIMIT 1').fetchone()
  prev=last[0] if last else 'GENESIS'
  seq=self.db.execute('SELECT COALESCE(MAX(seq),0)+1 FROM events').fetchone()[0]
  blob={'seq':seq,'task':task,'kind':kind,'body':body,'previous':prev}
  self.db.execute('INSERT INTO events VALUES (?,?,?,?,?,?)',(seq,task,kind,stable(body).decode(),prev,digest(stable(blob))))
 def finish(self,task,proof_bytes,expected_hash):
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.db.execute('SELECT state,source FROM task WHERE id=?',(task,)).fetchone()
   if not row or row[0]!='ACTIVE':self.db.execute('ROLLBACK');return 'HOLD_STATE'
   if digest(proof_bytes)!=expected_hash:self.db.execute('ROLLBACK');return 'HOLD_PROOF'
   self.db.execute("UPDATE task SET state='TEST_FINISHED',proof=? WHERE id=?",(expected_hash,task))
   self.event(task,'TEST_FINISH',{'proof_sha256':expected_hash,'source_sha256':row[1],'scope':'THEORETICAL_ONLY'})
   self.db.execute('COMMIT');return 'PASS_TEST_ONLY'
  except BaseException:self.db.execute('ROLLBACK');raise
 def finish_signed(self,task,goal,source,artifact,generation,receipt,signature,public_key_bytes):
  """Atomic test-only verified finish; fail-closed and isolated from owner approval."""
  from signed_verifier import verify
  self.db.execute('BEGIN IMMEDIATE')
  try:
   row=self.db.execute('SELECT goal,source,state FROM task WHERE id=?',(task,)).fetchone()
   if row!=(goal,source,'ACTIVE'):
    self.db.execute('ROLLBACK');return 'HOLD_TASK'
   verdict=verify(public_key_bytes,task,goal,source,artifact,generation,receipt,signature)
   if verdict!='PASS_TEST_VERIFIER':
    self.db.execute('ROLLBACK');return verdict
   evidence=digest(artifact)
   self.db.execute("UPDATE task SET state='TEST_FINISHED',proof=? WHERE id=?",(evidence,task))
   self.event(task,'SIGNED_TEST_FINISH',{'source_sha256':source,'artifact_sha256':evidence,'generation':generation,'receipt_sha256':digest(stable(receipt)),'signature_sha256':digest(signature),'scope':'TEST_ONLY_VERIFIER'})
   self.db.execute('COMMIT');return 'PASS_SIGNED_TEST_ONLY'
  except BaseException:self.db.execute('ROLLBACK');raise
 def verify(self):
  prev='GENESIS'
  for seq,task,kind,body,previous,value in self.db.execute('SELECT * FROM events ORDER BY seq'):
   try:d=json.loads(body)
   except (ValueError,TypeError):return 'HOLD_LEDGER'
   blob={'seq':seq,'task':task,'kind':kind,'body':d,'previous':previous}
   if previous!=prev or digest(stable(blob))!=value:return 'HOLD_LEDGER'
   prev=value
  return 'PASS_LEDGER'
 def close(self):self.db.close()
def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['list']);a=p.parse_args()
 if a.command=='list':
  print(json.dumps([{'goal':i+1,'source':v['source_sha256']} for i,v in enumerate(manifest())],indent=2))
if __name__=='__main__':main()
