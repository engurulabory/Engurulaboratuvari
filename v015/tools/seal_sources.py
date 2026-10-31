"""Release source manifest, excluding receipts/runtime output to avoid self-hash cycles."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'evidence','test-temporary','__pycache__','profile','build'}

def seal():
    files={}
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if any(x in EXCLUDED or x.endswith('.app') for x in rel.parts):continue
        if p.is_file() and p.name not in {'SOURCE_MANIFEST.json','MAC_INSTALL_RECEIPT.json','MAC_FIELD_RESULT.json','MAC_SWIFT_BUILD.log','MAC_TOOLCHAIN.json','MAC_TOOLCHAIN_PROBE.swift'}:
            if p.is_symlink():raise RuntimeError('SYMLINK_SOURCE')
            files[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
    (ROOT/'SOURCE_MANIFEST.json').write_text(json.dumps({'schema':'enguru.v015.release-source/v1','files':files},ensure_ascii=False,indent=2)+'\n')
    return files

if __name__=='__main__':print('SEALED_SOURCE_FILES',len(seal()))
