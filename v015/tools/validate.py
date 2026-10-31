#!/usr/bin/env python3
"""Source integrity and unchanged acceptance contract validator."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
 'contracts/ENGURU_V015_MIMARI_VE_KABUL_SOZLESMESI_V01.md':'afa7ddebe89c28ab25a5fc4946a590706137d11e58dac996d8b7b389cffb7c42',
 'contracts/ENGURU_V015_75_KOSUL_9_KAPI_ESLEME_V01.json':'b47fefb07edfffc510f83ac4486f21029acb4e577d0fd6bc7062314671cb7f4e',
 'contracts/SOURCES/acceptance_75_LOCKED.json':'a0ea2e161c639b079947301a6001021e43ff198aabca5105ed69586da2789756',
 'contracts/SOURCES/OWNER_34_DECISIONS_SOURCE_MAP_DRAFT.json':'6ca4d1375608ed681f3ae06376a005a1344d82eb0cd7759bc05c24f6588a5589'}

def validate():
    for n,h in PINS.items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
    original=json.loads((ROOT/'contracts/SOURCES/acceptance_75_LOCKED.json').read_text())['controls']
    mapping=json.loads((ROOT/'contracts/ENGURU_V015_75_KOSUL_9_KAPI_ESLEME_V01.json').read_text())['per_criterion']
    assert len(original)==len(mapping)==75
    assert len({r['id'] for r in mapping})==75
    assert len({r['area'] for r in original})==15
    for row in mapping:
        old=next(x for x in original if x['id']==row['id'])
        assert (old['requirement'],old['area'])==(row['requirement_original'],row['area'])
    manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
    for n,h in manifest['files'].items():
        path=ROOT/n
        assert not path.is_symlink() and path.is_file(),n
        assert hashlib.sha256(path.read_bytes()).hexdigest()==h,n
    return {'contract_pins':'PASS','criteria_text_exact':75,'areas':15,'source_files_verified':len(manifest['files'])}

if __name__=='__main__':print(json.dumps(validate(),ensure_ascii=False))
