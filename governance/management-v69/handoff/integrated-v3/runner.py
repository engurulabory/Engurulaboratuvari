#!/usr/bin/env python3
"""Run ten pinned theory module test entrypoints, then independently verify ledger."""
import argparse,hashlib,json,pathlib,sqlite3,subprocess,sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
MANIFEST=json.loads((HERE/"source_manifest.json").read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def run(out):
 out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(out/"ledger.sqlite3")
 db.execute("CREATE TABLE IF NOT EXISTS receipt(goal INTEGER PRIMARY KEY,task TEXT,src TEXT,stdout TEXT,body TEXT,previous TEXT,digest TEXT,rc INTEGER)")
 prev="GENESIS";task="ENGURU_V69_T01_T10"
 for i,m in enumerate(MANIFEST,1):
  f=(ROOT/m["path"]).resolve()
  if not f.is_relative_to(ROOT) or not f.is_file() or sha(f.read_bytes())!=m["source_sha256"]:
   print("HOLD_SOURCE_PIN",i);return 2
  try:
   cp=subprocess.run([sys.executable,"-B",str(f)],cwd=ROOT,capture_output=True,timeout=120)
  except subprocess.TimeoutExpired:
   print("HOLD_TIMEOUT",i);return 2
  if cp.returncode!=0:
   print("HOLD_EXECUTION",i,cp.returncode);return 2
  output=(cp.stdout+cp.stderr).decode(errors="replace")
  record={"goal":i,"task":task,"src":m["source_sha256"],"stdout":sha(output.encode()),"previous":prev,"rc":0}
  digest=sha(canon(record))
  db.execute("INSERT INTO receipt VALUES(?,?,?,?,?,?,?,?)",(i,task,m["source_sha256"],record["stdout"],output,prev,digest,0))
  db.commit();prev=digest;print("MODULE_PASS",i,flush=True)
 db.close();return 0
def verify(out):
 db=sqlite3.connect(pathlib.Path(out)/"ledger.sqlite3")
 rows=db.execute("SELECT goal,task,src,stdout,body,previous,digest,rc FROM receipt ORDER BY goal").fetchall()
 if len(rows)!=10:return 2
 prev="GENESIS"
 for i,(goal,task,src,stdout,body,previous,digest,rc) in enumerate(rows,1):
  if goal!=i or task!="ENGURU_V69_T01_T10" or src!=MANIFEST[i-1]["source_sha256"] or sha(body.encode())!=stdout or previous!=prev or rc!=0:return 2
  record={"goal":goal,"task":task,"src":src,"stdout":stdout,"previous":previous,"rc":rc}
  if sha(canon(record))!=digest:return 2
  prev=digest
 print("INDEPENDENT_LEDGER_CHECK=PASS");return 0
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--run");a.add_argument("--verify");args=a.parse_args()
 sys.exit(run(args.run) if args.run else verify(args.verify) if args.verify else 2)
