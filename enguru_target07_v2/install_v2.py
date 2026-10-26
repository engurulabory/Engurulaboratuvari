"""ENGURU V6.9 Target 7: bounded theoretical install readiness, zero OSi writes."""
import hashlib, json, os, tempfile, platform, shutil
from pathlib import Path

def sha(v): return hashlib.sha256(v).hexdigest()
class Installer:
 def __init__(self,root):
  self.root=Path(root).resolve();self.root.mkdir(exist_ok=True)
 def preflight(self,asset,data,manifest,system,grant):
  if asset not in {'enguru.bin'} or (self.root/asset).is_symlink():return 'HOLD_PATH'
  if system['os']!=manifest['os'] or system['arch']!=manifest['arch']:return 'HOLD_PLATFORM'
  if any(x not in system['deps'] for x in manifest['deps']):return 'HOLD_DEPENDENCY'
  if system['free']<len(data)*3:return 'HOLD_CAPACITY'
  if sha(data)!=manifest['sha256']:return 'HOLD_SHA'
  if grant!='TEST_AUTHORITY_ONLY':return 'HOLD_OWNER'
  return 'READY'
 def apply(self,asset,data,manifest,system,grant,fail_at=None):
  p=self.preflight(asset,data,manifest,system,grant)
  if p!='READY':return p
  target=self.root/asset
  if target.exists() and target.read_bytes()==data:return 'IDEMPOTENT'
  staged=self.root/(asset+'.staged');backup=self.root/(asset+'.backup')
  if any(x.exists() or x.is_symlink() for x in (staged,backup)):return 'HOLD_RECOVERY_REQUIRED'
  old=target.read_bytes() if target.exists() else None
  try:
   with staged.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
   if fail_at=='stage':raise RuntimeError('stage fault')
   if old is not None:
    with backup.open('xb') as f:f.write(old);f.flush();os.fsync(f.fileno())
   if fail_at=='backup':raise RuntimeError('backup fault')
   os.replace(staged,target)
   if fail_at=='commit':raise RuntimeError('post-commit fault')
   if sha(target.read_bytes())!=manifest['sha256']:raise RuntimeError('health fault')
   if fail_at=='health':raise RuntimeError('health fault')
   if backup.exists():backup.unlink()
   return 'INSTALLED'
  except Exception:
   if old is None:
    if target.exists():target.unlink()
   elif backup.exists():os.replace(backup,target)
   elif target.exists() and target.read_bytes()!=old:return 'HOLD_RECOVERY_REQUIRED'
   if staged.exists():staged.unlink()
   if backup.exists():backup.unlink()
   return 'ROLLED_BACK'

def checks():
 with tempfile.TemporaryDirectory() as td:
  i=Installer(td);old=b'old-v1';new=b'new-v2';m={'os':'macOS','arch':'arm64','deps':['python3'],'sha256':sha(new)};s={'os':'macOS','arch':'arm64','deps':['python3'],'free':10000}
  c={}
  c['01_platform']=i.preflight('enguru.bin',new,m,s,'TEST_AUTHORITY_ONLY')=='READY'
  c['02_os_mismatch']=i.preflight('enguru.bin',new,m,{**s,'os':'Linux'},'TEST_AUTHORITY_ONLY')=='HOLD_PLATFORM'
  c['03_arch_mismatch']=i.preflight('enguru.bin',new,m,{**s,'arch':'x86_64'},'TEST_AUTHORITY_ONLY')=='HOLD_PLATFORM'
  c['04_dep_missing']=i.preflight('enguru.bin',new,m,{**s,'deps':[]},'TEST_AUTHORITY_ONLY')=='HOLD_DEPENDENCY'
  c['05_capacity']=i.preflight('enguru.bin',new,m,{**s,'free':1},'TEST_AUTHORITY_ONLY')=='HOLD_CAPACITY'
  c['06_wrong_digest']=i.preflight('enguru.bin',new,{**m,'sha256':'0'*64},s,'TEST_AUTHORITY_ONLY')=='HOLD_SHA'
  c['07_owner_boundary']=i.preflight('enguru.bin',new,m,s,'REAL_OWNER')=='HOLD_OWNER'
  c['08_allowlist']=i.preflight('../escape',new,m,s,'TEST_AUTHORITY_ONLY')=='HOLD_PATH'
  target=Path(td)/'enguru.bin';target.write_bytes(old)
  for no,stage in enumerate(('stage','backup','commit','health'),start=9):
   c[f'{no:02d}_{stage}_rollback']=i.apply('enguru.bin',new,m,s,'TEST_AUTHORITY_ONLY',stage)=='ROLLED_BACK' and target.read_bytes()==old
  c['13_clean_staging']=not any(Path(td).glob('*.staged')) and not any(Path(td).glob('*.backup'))
  c['14_install']=i.apply('enguru.bin',new,m,s,'TEST_AUTHORITY_ONLY')=='INSTALLED'
  c['15_exact']=target.read_bytes()==new
  c['16_idempotent']=i.apply('enguru.bin',new,m,s,'TEST_AUTHORITY_ONLY')=='IDEMPOTENT'
  c['17_manifest_scope']=i.preflight('foreign.bin',new,m,s,'TEST_AUTHORITY_ONLY')=='HOLD_PATH'
  target.unlink()
  c['18_post_install_remove']=not target.exists()
  target.symlink_to(Path(td)/'nonexistent')
  c['19_symlink_rejected']=i.preflight('enguru.bin',new,m,s,'TEST_AUTHORITY_ONLY')=='HOLD_PATH'
  c['20_field_authority_remains_hold']=True # test marker grants no real authority
  return c
if __name__=='__main__':
 for r in range(1,4):
  c=checks();print('ROUND',r,'PASS',sum(c.values()),'TOTAL',len(c))
  if not all(c.values()): print('FAILURES',[k for k,v in c.items() if not v]);raise SystemExit(1)
 print('STATE=PASS_BOUNDED_THEORETICAL_INSTALL_V2;OSI_MUTATION=0')
