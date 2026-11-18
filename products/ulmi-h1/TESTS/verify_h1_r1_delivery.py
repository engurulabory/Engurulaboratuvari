#!/usr/bin/env python3
"""Pure read-only SHA validator for a delivered ULMI H1 R1 ZIP; no Mac, execution or ledger changes."""
import argparse,hashlib,json,stat,sys,zipfile
from pathlib import PurePosixPath
p=argparse.ArgumentParser();p.add_argument('archive');a=p.parse_args()
with zipfile.ZipFile(a.archive) as z:
    names=z.namelist()
    assert len(names)==len(set(names)), 'duplicate zip member'
    assert 'DELIVERY_H1_ONLY_MANIFEST.json' in names, 'missing current manifest'
    m=json.loads(z.read('DELIVERY_H1_ONLY_MANIFEST.json'))
    files=m['files']
    assert sorted(names)==sorted(list(files)+['DELIVERY_H1_ONLY_MANIFEST.json'])
    for name in names:
        pp=PurePosixPath(name)
        assert not pp.is_absolute() and '..' not in pp.parts and '\\' not in name, ('unsafe path',name)
        info=z.getinfo(name)
        assert not stat.S_ISLNK(info.external_attr>>16), ('symlink',name)
        assert not name.endswith('/'), ('directory entry',name)
        if name in files:
            raw=z.read(name)
            assert hashlib.sha256(raw).hexdigest()==files[name]['sha256'],('SHA mismatch',name)
            assert len(raw)==files[name]['bytes'],('length mismatch',name)
    assert m['product_scope']=='H1_ONLY'
    assert m['formal_v22']=='0/12_HOLD'
    assert m['html_owner_uat']=='NOT_EXECUTED_R1'
    assert hashlib.sha256(z.read('PRODUCT/server.py')).hexdigest()==m['server_sha256']
    print(json.dumps({'scope':m['product_scope'],'files':len(files),'verified_files':len(files),'formal_v22':m['formal_v22'],'owner_uat':m['html_owner_uat'],'status':'PASS_SCOPED_ARCHIVE_SHA'},ensure_ascii=False))
