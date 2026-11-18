"""ENGÜRÜ Mühendis OSi H1: one catalog bridge over the EXISTING SQLite ledger.

The HFS remains authoritative. This connector accepts an owner-supplied catalog
snapshot; it never asserts that a JSON file has been independently authenticated
against the Saray and never grants an executor new filesystem permissions.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA='enguru.muhendis.h1.worklist-v1'
KINDS={
 'PYTHON_TEST_EXAMPLE':('Python','Güvenilir Python testi; 3 gerçek unittest'),
 'HTML_EXAMPLE':('HTML','Güvenilir HTML örneği; tarayıcı kontrolü ayrı'),
 'PYTHON_STATIC_DIAG':('Teşhis','Python kodunu çalıştırmadan AST teşhisi'),
 'OLLAMA_SINGLE_FILE':('Yerel model','İsteğe bağlı Ollama tek dosya planı; serbest kod çalıştırılmaz'),
}
ID_RE=re.compile(r'^[A-Z0-9][A-Z0-9_-]{2,63}$')

def init(db):
 db.execute('''CREATE TABLE IF NOT EXISTS hfs_work_catalogs (
  catalog_id TEXT PRIMARY KEY, revision INTEGER NOT NULL, content_sha TEXT NOT NULL,
  source_claim TEXT NOT NULL, imported_at TEXT NOT NULL)''')
 db.execute('''CREATE TABLE IF NOT EXISTS hfs_work_items (
  work_id TEXT PRIMARY KEY, catalog_id TEXT NOT NULL, category TEXT NOT NULL,
  title TEXT NOT NULL, description TEXT NOT NULL, kind TEXT NOT NULL,
  input_data TEXT NOT NULL, task_id TEXT UNIQUE, browser_proof TEXT,
  imported_at TEXT NOT NULL)''')

def _validated(doc: Any):
 if not isinstance(doc,dict) or doc.get('schema')!=SCHEMA:
  raise ValueError('İş listesi sözleşmesi geçersiz.')
 cid=doc.get('catalog_id'); revision=doc.get('revision'); claim=doc.get('source_claim'); items=doc.get('items')
 if not isinstance(cid,str) or not ID_RE.fullmatch(cid): raise ValueError('Liste kimliği geçersiz.')
 if type(revision)!=int or not (1<=revision<=99999): raise ValueError('Liste revizyonu geçersiz.')
 if claim not in ('LOCAL_DEMO_NOT_SARAY_ACCEPTED','HFS_MANAGEMENT_OWNER_SUPPLIED'):
  raise ValueError('Kaynak sınırı belirsiz. Onaylı kaynak türünü kullanın.')
 if not isinstance(items,list) or not 1<=len(items)<=60: raise ValueError('İş listesi 1-60 iş içermeli.')
 seen=set(); out=[]
 for raw in items:
  if not isinstance(raw,dict): raise ValueError('İş girdisi nesne olmalı.')
  wid=raw.get('work_id'); title=raw.get('title'); cat=raw.get('category'); desc=raw.get('description'); kind=raw.get('kind'); inp=raw.get('input','')
  if not isinstance(wid,str) or not ID_RE.fullmatch(wid) or wid in seen: raise ValueError('Yinelenen/geçersiz iş kimliği.')
  seen.add(wid)
  if not isinstance(title,str) or not 3<=len(title)<=100: raise ValueError('İş başlığı 3-100 karakter olmalı.')
  if not isinstance(cat,str) or not 2<=len(cat)<=50: raise ValueError('İş türü etiketi geçersiz.')
  if not isinstance(desc,str) or not 4<=len(desc)<=350: raise ValueError('İş açıklaması geçersiz.')
  if kind not in KINDS: raise ValueError('Desteklenmeyen iş yürütme türü: '+str(kind)[:50])
  if not isinstance(inp,str) or len(inp)>4000: raise ValueError('İş girdisi 4000 karakteri geçemez.')
  if kind=='PYTHON_STATIC_DIAG' and not 4<=len(inp.strip())<=4000: raise ValueError('Python teşhis kodu gerekli.')
  if kind=='OLLAMA_SINGLE_FILE' and not 5<=len(inp.strip())<=1200: raise ValueError('Ollama görev metni 5-1200 karakter olmalı.')
  if kind in ('HTML_EXAMPLE','PYTHON_TEST_EXAMPLE') and inp: raise ValueError('Sabit örnekler iş girdisi alamaz.')
  out.append({'work_id':wid,'title':title,'category':cat,'description':desc,'kind':kind,'input':inp})
 return cid,revision,claim,out

def _canonical(doc:dict)->str:
 return hashlib.sha256(json.dumps(doc,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

def import_catalog(doc:dict,srv):
 cid,revision,claim,items=_validated(doc)
 digest=_canonical({'schema':SCHEMA,'catalog_id':cid,'revision':revision,'source_claim':claim,'items':items})
 now=srv.iso_now()
 with srv.DB_LOCK, srv.db_conn() as db:
  db.execute('BEGIN IMMEDIATE')
  old=db.execute('SELECT * FROM hfs_work_catalogs WHERE catalog_id=?',(cid,)).fetchone()
  if old and (revision<old['revision'] or (revision==old['revision'] and digest!=old['content_sha'])):
   raise ValueError('İş listesi revizyonu geriye gitti veya aynı sürümde içerik değişti.')
  previous=db.execute('SELECT * FROM hfs_work_items WHERE catalog_id=?',(cid,)).fetchall()
  by_id={row['work_id']:row for row in previous}
  incoming={entry['work_id']:entry for entry in items}
  if not set(by_id).issubset(incoming): raise ValueError('Eski işler korunmalı; listedeki iş silinemez.')
  for wid,row in by_id.items():
   current=incoming[wid]
   if (row['title'],row['category'],row['description'],row['kind'],row['input_data']) != (current['title'],current['category'],current['description'],current['kind'],current['input']):
    raise ValueError('Mevcut iş değiştirilemez; yeni iş kimliğiyle eklenmeli: '+wid)
  added=0
  for item in items:
   if item['work_id'] in by_id:continue
   taken=db.execute('SELECT catalog_id FROM hfs_work_items WHERE work_id=?',(item['work_id'],)).fetchone()
   if taken: raise ValueError('İş kimliği başka bir listede zaten mevcut: '+item['work_id'])
   db.execute('''INSERT INTO hfs_work_items
    (work_id,catalog_id,category,title,description,kind,input_data,imported_at)
    VALUES(?,?,?,?,?,?,?,?)''',(item['work_id'],cid,item['category'],item['title'],item['description'],item['kind'],item['input'],now))
   added+=1
  db.execute('''INSERT INTO hfs_work_catalogs (catalog_id,revision,content_sha,source_claim,imported_at)
    VALUES(?,?,?,?,?) ON CONFLICT(catalog_id) DO UPDATE SET revision=excluded.revision,content_sha=excluded.content_sha,source_claim=excluded.source_claim,imported_at=excluded.imported_at''',(cid,revision,digest,claim,now))
  db.commit()
 return {'status':'PASS_SCOPED_LOCAL_IMPORT','catalog_id':cid,'revision':revision,'added':added,'total':len(items),
         'source_claim':claim,'content_sha256':digest,'authority':'OWNER_LOCAL_IMPORT_SARAY_INDEPENDENT_AUTHENTICATION_PENDING'}

def seed_if_empty(srv):
 with srv.DB_LOCK,srv.db_conn() as db:
  count=db.execute('SELECT COUNT(*) FROM hfs_work_catalogs').fetchone()[0]
 if count==0:
  f=srv.BASE/'WORKLIST_DEMO_V1.json'
  if f.is_file(): import_catalog(json.loads(f.read_text('utf-8')),srv)

def _row_state(row,srv):
 tid=row['task_id']; receipt=json.loads(row['browser_proof']) if row['browser_proof'] else None
 out=dict(row);out.pop('input_data',None);out['input_preview']=row['input_data'][:90] if row['input_data'] else ''
 out.pop('browser_proof',None);out['browser_proof']=receipt;out['task_status']=None;out['next_action']='İşi seç ve Başlat düğmesine bas.'
 out['state']='NOT_STARTED'
 if tid:
  t=srv.get_task(tid)
  if not t:
   out['state']='HOLD';out['next_action']='İş ve görev kimlikleri uzlaştırılmalı.'
  elif t['status']=='READY':
   out['state']='READY_OWNER';out['next_action']='Planı incele ve owner onayı ver.'
  elif t['status']=='RUNNING':
   out['state']='IN_PROGRESS';out['next_action']='Yürütücünün gerçek sonuç makbuzunu bekle.'
  elif t['status']=='PASS_SCOPED':
   verified=srv.verify_written_task(tid)
   if verified['status']!='PASS_SCOPED_READBACK':
    out['state']='HOLD_INTEGRITY';out['next_action']='SHA/çalışma alanı uzlaştırması gerekir.'
   elif (t['receipt'] or {}).get('functional_test',{}).get('status')=='PASS':
    out['state']='DONE_SCOPED';out['next_action']='Makbuzu görüntüle; ürün kabulü ayrıdır.'
   elif row['kind']=='HTML_EXAMPLE' and receipt:
    # A local DOM observation is not an independently authenticated browser test.
    # This also downgrades prior PASS_SCOPED_BROWSER_CLIENT rows safely on read.
    out['state']='VERIFYING'
    out['next_action']='İstemci gözlemi alındı; bağımsız tarayıcı doğrulaması ve gerekli kabul bekleniyor.'
   elif row['kind']=='HTML_EXAMPLE':
    out['state']='VERIFYING';out['next_action']='Gerçek HTML düğmesinin tarayıcı davranışını sınayıp kanıtla.'
   else:
    out['state']='VERIFYING';out['next_action']='Davranış testi veya bağımsız kanıt gerekli.'
  else:
   out['state']='HOLD';out['next_action']=t.get('error') or t['status']
  if t:out['task_status']=t['status']
 return out

def list_catalog(srv):
 with srv.DB_LOCK,srv.db_conn() as db:
  rows=db.execute('SELECT * FROM hfs_work_items ORDER BY imported_at ASC, rowid ASC LIMIT 200').fetchall()
  cats=db.execute('SELECT * FROM hfs_work_catalogs ORDER BY imported_at ASC').fetchall()
 items=[_row_state(row,srv) for row in rows]
 ongoing=[x for x in items if x['state'] not in ('NOT_STARTED','DONE_SCOPED','DONE_SCOPED_BROWSER')]
 done=[x for x in items if x['state'] in ('DONE_SCOPED','DONE_SCOPED_BROWSER')]
 return {'status':'PASS_SCOPED_LOCAL_WORKLIST','items':items,'work_in_progress':ongoing,'work_done':done,
         'counts':{'listed':len(items),'not_started':sum(x['state']=='NOT_STARTED' for x in items),'in_progress':len(ongoing),'done_scoped':len(done)},
         'catalogs':[dict(x) for x in cats], 'authority_notice':'Yerel owner yüklemesi; Saray kaynak onayı ayrı.'}

def plan_selected(work_id:str,srv):
 if not isinstance(work_id,str) or not ID_RE.fullmatch(work_id):raise ValueError('İş kimliği geçersiz.')
 with srv.DB_LOCK:
  with srv.db_conn() as db:row=db.execute('SELECT * FROM hfs_work_items WHERE work_id=?',(work_id,)).fetchone()
  if not row: raise ValueError('İş listesinde böyle bir iş yok.')
  if row['task_id']:
   task=srv.get_task(row['task_id'])
   if task is None:raise ValueError('Görev kimliği uzlaştırılmalı.')
   return {'status':'ALREADY_PLANNED','work_id':work_id,'task':task,'message':'Var olan görev korunuyor; yeni dosya oluşturulmadı.'}
  kind=row['kind']
  if kind=='HTML_EXAMPLE': plan=srv.make_scaffold('html')
  elif kind=='PYTHON_TEST_EXAMPLE':plan=srv.make_scaffold('python')
  elif kind=='PYTHON_STATIC_DIAG':plan=srv.plan_capability('PY_DIAGNOSTIC_V1',row['input_data'])
  elif kind=='OLLAMA_SINGLE_FILE':plan=srv.generate_local_plan(row['input_data'])
  else:raise ValueError('İş yürütücüsü doğrulanmadı.')
  with srv.db_conn() as db:
   cur=db.execute('UPDATE hfs_work_items SET task_id=? WHERE work_id=? AND task_id IS NULL',(plan['task_id'],work_id))
   if cur.rowcount!=1:raise ValueError('İş zaten başlatılmış; tekrar uzlaştırılmalı.')
   db.commit()
  return {'status':'READY_OWNER','work_id':work_id,'plan':plan,'next_action':'Owner planı onaylayınca mevcut /api/execute çalışacak.'}

def accept_html_browser(work_id:str,task_id:str,observed:str,srv):
 if observed!='Görev tamamlandı':raise ValueError('Tarayıcı davranış kanıtı geçersiz.')
 with srv.DB_LOCK:
  with srv.db_conn() as db:row=db.execute('SELECT * FROM hfs_work_items WHERE work_id=?',(work_id,)).fetchone()
  if not row or row['kind']!='HTML_EXAMPLE' or row['task_id']!=task_id:raise ValueError('İş/Görev/HTML türü eşleşmiyor.')
  srv.trusted_html_fixture_readback(task_id) # only fixture with exact bytes and server-side receipt SHA
  if srv.verify_written_task(task_id)['status']!='PASS_SCOPED_READBACK':raise ValueError('Bağımsız olmayan SHA kontrolü başarısız.')
  proof={'outcome':'CLIENT_OBSERVATION_UNVERIFIED','task_id':task_id,'work_id':work_id,'timestamp':srv.iso_now(),
         'client_observation':observed,'test':'CLIENT_REPORTED_DOM_BEHAVIOR_NO_INDEPENDENT_ATTESTATION',
         'independent_donecheck':False,'final_done':False}
  with srv.db_conn() as db:
   db.execute('UPDATE hfs_work_items SET browser_proof=? WHERE work_id=?',(json.dumps(proof,ensure_ascii=False),work_id));db.commit()
 return {'status':'CLIENT_OBSERVATION_RECORDED_VERIFYING','proof':proof,'not_independent_donecheck':True,'final_done':False}
