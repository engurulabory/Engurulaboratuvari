
"""ENGURU Target 08: bounded engineering pipeline theoretical model."""
import hashlib, tempfile
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def pipeline(src,expected,requirements,dependencies,break_stage=None):
 if sha(src)!=expected:return {'state':'HOLD_SOURCE'}
 if not requirements or len(set(requirements))!=len(requirements):return {'state':'HOLD_REQUIREMENTS'}
 if any(d not in requirements for d in dependencies):return {'state':'HOLD_DEPENDENCY'}
 with tempfile.TemporaryDirectory() as td:
  d=Path(td)
  stages=['plan','build','test','verify','package']
  rec=[]
  for s in stages:
   if s==break_stage:return {'state':'HOLD_STAGE','stage':s,'completed':tuple(rec)}
   b=(s+'|'+expected+'|'+','.join(requirements)).encode()
   path=d/(s+'.receipt');path.write_bytes(b)
   if sha(path.read_bytes())!=sha(b):return {'state':'HOLD_RECEIPT'}
   rec.append((s,sha(b)))
  payload=('bundle|'+expected+'|'+rec[-1][1]).encode()
  return {'state':'PASS_THEORETICAL_BUILD','artifact_sha256':sha(payload),'receipts':tuple(rec)}
def run():
 src=b'source-v1';h=sha(src);req=('r1','r2');deps=('r1',)
 baseline=pipeline(src,h,req,deps)
 c={
 '01_source_pin':baseline['state']=='PASS_THEORETICAL_BUILD',
 '02_source_drift':pipeline(src+b'X',h,req,deps)['state']=='HOLD_SOURCE',
 '03_duplicate_requirement':pipeline(src,h,('r1','r1'),deps)['state']=='HOLD_REQUIREMENTS',
 '04_missing_dependency':pipeline(src,h,req,('bad',))['state']=='HOLD_DEPENDENCY',
 '05_five_receipts':len(baseline['receipts'])==5,
 '06_deterministic_package':pipeline(src,h,req,deps)['artifact_sha256']==baseline['artifact_sha256'],
 '07_abort_build':pipeline(src,h,req,deps,'build')['state']=='HOLD_STAGE',
 '08_abort_verify':pipeline(src,h,req,deps,'verify')['state']=='HOLD_STAGE',
 '09_stage_order':tuple(x[0] for x in baseline['receipts'])==('plan','build','test','verify','package'),
 '10_no_owner_claim':'owner_pass' not in baseline and 'osi_installed' not in baseline
 }
 return c
if __name__=='__main__':
 for n in range(1,4):
  c=run();print('ROUND',n,sum(c.values()),'/',len(c))
  if not all(c.values()):raise SystemExit(1)
 print('STATE=PASS_BOUNDED_THEORETICAL_ENGINEERING_V1')
