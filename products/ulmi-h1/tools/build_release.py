#!/usr/bin/env python3
"""Deterministic UTF-8 H1 deliverable (technical candidate; no human acceptance)."""
import hashlib, io, json, sys, zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
INCLUDE=('PRODUCT/','TESTS/','ORIGINALS/V22_IMMUTABLE_SOURCE.json','ORIGINALS/PILOT_ABC_IMMUTABLE_SOURCE.json','RESEARCH_ARCHIVE/canonical_sources/','FROZEN_HANDOFF/V22_12_EXACT_ACCEPTANCE_LEDGER.json','EVIDENCE/OWNER_V5_SAFARI_UAT_RAW.json','START_H1.sh','README_H1_EMIR01_R2.md','README_GITHUB_H1.md','tools/verify_contracts.py','tools/build_release.py','tools/browser_h1_e2e.py')
def included(p):
    r=p.relative_to(R).as_posix()
    return any(r==s or r.startswith(s) for s in INCLUDE)
def make():
    b=io.BytesIO();paths=sorted(p for p in R.rglob('*') if p.is_file() and included(p))
    with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in paths:
            name=p.relative_to(R).as_posix()
            info=zipfile.ZipInfo('ULMI_H1/'+name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return b.getvalue(),paths
one,paths=make();two,_=make();assert one==two
with zipfile.ZipFile(io.BytesIO(one)) as z:
    assert z.testzip() is None
output=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/ulmi-h1-tech-candidate.zip')
output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(one)
receipt={'state':'PASS_SCOPED_DETERMINISTIC_ARTIFACT','file_count':len(paths),'zip_sha256':hashlib.sha256(one).hexdigest(),'size_bytes':len(one),'two_builds_byte_equal':True,'original_formal_12':'HOLD','actual_qwen':'NOT_TESTED','browser_uat':'SEPARATE','owner_final':'NOT_ISSUED'}
receipt_path=output.with_suffix('.receipt.json');receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,sort_keys=True))
