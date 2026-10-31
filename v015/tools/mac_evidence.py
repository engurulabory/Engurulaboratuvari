"""Explicit receipt allowlist; never include authority.key or user databases."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]

def collect():
    names=['MAC_INSTALL_RECEIPT.json','MAC_FIELD_RESULT.json','MAC_SWIFT_BUILD.log','MAC_SELF_TEST.log','MAC_TOOLCHAIN.json','MAC_TOOLCHAIN_PROBE.swift',
           'SOURCE_MANIFEST.json','evidence/V015_TEST_RECEIPT.json','evidence/V015_TEST_LOG.txt']
    jobs=ROOT/'profile'/'jobs'
    if jobs.is_dir() and not jobs.is_symlink():
        for d in jobs.iterdir():
            if d.is_dir() and not d.is_symlink():
                for name in ['operation.json','unique_jobs.py','unique_jobs.before.py','test_unique_jobs.py']:
                    names.append(str((d/name).relative_to(ROOT)))
    data={}
    for name in names:
        p=ROOT/name
        if p.is_file() and not p.is_symlink() and not any(x.is_symlink() for x in p.parents):
            b=p.read_bytes()
            if len(b)>3000000:raise RuntimeError('EVIDENCE_SIZE')
            data[name]=b
    data['EVIDENCE_MANIFEST.json']=(json.dumps({'schema':'enguru.v015.mac-evidence/v1',
        'sha256':{k:hashlib.sha256(v).hexdigest() for k,v in data.items()},
        'private_key_included':False,'product_verified_finish':'HOLD'},indent=2)+'\n').encode()
    output=ROOT/'MAC_EVIDENCE_V015.zip'
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
            for n,b in data.items():z.writestr(n,b)
    return output

if __name__=='__main__':print(collect())
