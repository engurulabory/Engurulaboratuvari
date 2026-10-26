"""Archive actual isolated outputs and byte manifest; omit temporary local Git internals."""
import hashlib,json,sys,zipfile
from pathlib import Path
root=Path(sys.argv[1]);target=Path(sys.argv[2]);manifest={}
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(root.rglob('*')):
  if not p.is_file() or '.git' in p.relative_to(root).parts:continue
  rel=str(p.relative_to(root));raw=p.read_bytes();manifest[rel]=hashlib.sha256(raw).hexdigest();z.writestr(rel,raw)
 z.writestr('BYTE_MANIFEST.json',json.dumps(manifest,sort_keys=True,indent=2)+'\n')
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for rel,pin in manifest.items():assert hashlib.sha256(z.read(rel)).hexdigest()==pin
print(json.dumps({'archive':target.name,'files':len(manifest),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},sort_keys=True))
