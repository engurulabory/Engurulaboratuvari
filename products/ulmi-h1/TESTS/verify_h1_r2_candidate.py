#!/usr/bin/env python3
"""Read-only R2 SHA and source boundary validation. NOT independent DoneCheck."""
import sys,json,zipfile,hashlib,stat
from pathlib import PurePosixPath
s=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(sys.argv[1]) as z:
 names=z.namelist(); assert len(names)==len(set(names))
 m=json.loads(z.read('DELIVERY_H1_ONLY_MANIFEST.json'))
 assert sorted(names)==sorted(list(m['files'])+['DELIVERY_H1_ONLY_MANIFEST.json'])
 for n in names:
  p=PurePosixPath(n)
  assert not p.is_absolute() and '..' not in p.parts and chr(92) not in n and not n.endswith('/')
  assert not stat.S_ISLNK(z.getinfo(n).external_attr>>16)
  if n in m['files']:
   raw=z.read(n);assert s(raw)==m['files'][n]['sha256'] and len(raw)==m['files'][n]['bytes'],n
 frozen=json.loads(z.read('FILE_MANIFEST_SHA256.json'))
 assert frozen['count']==len(frozen['files'])==309
 for n,h in frozen['files'].items():assert s(z.read(n))==h,n
 v22=s(z.read('ORIGINALS/V22_IMMUTABLE_SOURCE.json'))
 abc=s(z.read('ORIGINALS/PILOT_ABC_IMMUTABLE_SOURCE.json'))
 assert v22==m['original_v22_sha256']=='069c03b0f299e76ef46e26a25eb4284474ae5219353185a88386ee5df9f39304'
 assert abc=='5beb10d407dc550d7f979062fef6bdcfd451791103d5b02fc1c2d05a1786d79b'
 build_files=['server.py','uat_final.js','index.html','app.js','taskboard_template.py','chat_bridge.py','contract_bridge.py']
 sources={p:s(z.read('PRODUCT/'+p)) for p in build_files}
 aggregate=s(json.dumps(sources,sort_keys=True,separators=(',',':')).encode())
 assert aggregate==frozen['build_aggregate_sha256']
 assert m['formal_v22']=='0/12_HOLD' and not m['h2_active_scope']
 assert m['independent_donecheck']=='NOT_EXECUTED' and m['real_qwen']=='NOT_EXECUTED'
 assert m['html_owner_uat']=='NOT_EXECUTED_R2'
 assert b'id="h1-chat"' in z.read('PRODUCT/index.html')
 assert b'/api/desk/project-chat' in z.read('PRODUCT/app.js')
 print(json.dumps({'status':'PASS_SCOPED_SHA_ONLY','verified_files':len(m['files']),
  'current_frozen_manifest_files':len(frozen['files']),'aggregate_sha256':aggregate,
  'formal_v22':m['formal_v22'],'real_qwen':m['real_qwen'],
  'browser_uat':m['html_owner_uat'],'owner_final':'NOT_ISSUED'},ensure_ascii=False))
