#!/usr/bin/env python3
"""ENGURU MK GitHub transport adapter; branch-scoped, delivery-only, no owner acceptance."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

ROOT=Path("governance/enguru-suzgeci/learning/bridge/pilot")
TASK="ENGURU_MK_BRIDGE_PILOT_V1"
EVENT_KEYS={"schema","eventId","taskId","blockId","producer","sequence","type","code","sourceCommit","evidenceSha256","observedAt","visibility"}
CODES={"PILOT_HELLO","GITHUB_RECEIVED","PILOT_RECOVERY","RUNTIME_DRIFT","PACKAGE_ABSENT","INTERACTIVE_TIMEOUT","NODE_TAP_MISMATCH"}
class Hold(Exception): pass
def pairs(kv):
    d={}
    for k,v in kv:
        if k in d: raise Hold("DUPLICATE_KEY")
        d[k]=v
    return d
def canon(x):
    return (json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False)+"\n").encode()
def digest(x): return hashlib.sha256(canon(x)).hexdigest()
def read(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>4096: raise Hold("SOURCE_FILE")
    try: return json.loads(path.read_bytes(),object_pairs_hook=pairs)
    except (ValueError,UnicodeError) as e: raise Hold("JSON_FORMAT") from e
def event(x):
    if not isinstance(x,dict) or set(x)!=EVENT_KEYS:raise Hold("EVENT_KEYS")
    if x["schema"]!="enguru.mk.bridge-event/v1" or x["taskId"]!=TASK:raise Hold("SCOPE")
    if x["producer"]!="MAC_OSI_MK" or x["visibility"]!="PUBLIC_SANITIZED":raise Hold("VISIBILITY")
    if x["type"] not in ("SUCCESS","ERROR","NEED","MISMATCH") or x["code"] not in CODES:raise Hold("CODE")
    if type(x["sequence"]) is not int or not 1<=x["sequence"]<=99999999 or x["eventId"]!=f'MAC-{x["sequence"]:08d}':raise Hold("SEQ")
    if not isinstance(x["blockId"],str) or not re.fullmatch(r"OSIBLOCK-[0-9]{8}-[A-Z0-9]{3,16}",x["blockId"]):raise Hold("BLOCK")
    if not isinstance(x["sourceCommit"],str) or not re.fullmatch(r"[0-9a-f]{40}",x["sourceCommit"]):raise Hold("COMMIT")
    if not isinstance(x["evidenceSha256"],str) or not re.fullmatch(r"[0-9a-f]{64}",x["evidenceSha256"]):raise Hold("DIGEST")
    try:
        t=datetime.fromisoformat(x["observedAt"].replace("Z","+00:00"))
        if t.utcoffset() is None:raise ValueError()
    except (TypeError,ValueError,AttributeError) as e:raise Hold("TIME") from e
    return digest(x)
def write_once(path,body):
    if path.is_symlink():raise Hold("SYMLINK")
    if path.exists():
        if path.read_bytes()!=body:raise Hold("CONTENT_CONFLICT")
        return False
    path.parent.mkdir(parents=True,exist_ok=True)
    with open(path,"xb") as w:w.write(body)
    return True
def process(worktree,owner,actor):
    if not owner or owner!=actor or actor.endswith("[bot]"):raise Hold("ACTOR")
    root=Path(worktree)/ROOT
    for part in ("streams/mac","acks/mac","streams/github"):
        directory=root/part
        if directory.is_symlink():raise Hold("DIR_SYMLINK")
        directory.mkdir(parents=True,exist_ok=True)
    incoming=root/"streams/mac"
    entries=sorted(incoming.iterdir())
    if len(entries)>100:raise Hold("CAPACITY")
    created=0
    for num,p in enumerate(entries,1):
        if not re.fullmatch(r"MAC-[0-9]{8}\.json",p.name):raise Hold("FILENAME")
        x=read(p)
        h=event(x)
        if x["sequence"]!=num or p.name!=x["eventId"]+".json":raise Hold("GAP_OR_REPLAY")
        ack={"schema":"enguru.mk.bridge-ack/v1","eventId":x["eventId"],
             "receiver":"GITHUB_MK","eventSha256":h,
             "delivery":"RECEIVED_ONLY","officialAcceptance":"HOLD"}
        created+=write_once(root/"acks/mac"/p.name,canon(ack))
        reply=dict(x)
        reply.update(eventId=f"GH-{num:08d}",producer="GITHUB_MK",code="GITHUB_RECEIVED")
        created+=write_once(root/"streams/github"/f"GH-{num:08d}.json",canon(reply))
    return {"state":"PASS_GITHUB_TRANSPORT_ONLY","received":len(entries),"newRecords":created,"officialAcceptance":"HOLD"}
def self_test():
    from pathlib import Path
    with tempfile.TemporaryDirectory() as t:
        base=Path(t)/ROOT/"streams/mac";base.mkdir(parents=True)
        x={"schema":"enguru.mk.bridge-event/v1","eventId":"MAC-00000001","taskId":TASK,
           "blockId":"OSIBLOCK-20261024-PILOT","producer":"MAC_OSI_MK","sequence":1,"type":"SUCCESS",
           "code":"PILOT_HELLO","sourceCommit":"a"*40,
           "evidenceSha256":hashlib.sha256(b"ENGURU_PUBLIC_PILOT_ONLY_V1").hexdigest(),
           "observedAt":"2026-10-24T14:00:00Z","visibility":"PUBLIC_SANITIZED"}
        write_once(base/"MAC-00000001.json",canon(x))
        assert process(t,"owner","owner")["newRecords"]==2
        assert process(t,"owner","owner")["newRecords"]==0
        assert json.loads((Path(t)/ROOT/"acks/mac/MAC-00000001.json").read_bytes())["eventSha256"]==digest(x)
        reply=json.loads((Path(t)/ROOT/"streams/github/GH-00000001.json").read_bytes())
        assert reply["eventId"]=="GH-00000001" and reply["code"]=="GITHUB_RECEIVED"
        x["code"]="OTHER"
        assert not (x["code"] in CODES)
        try:process(t,"owner","intruder");raise AssertionError()
        except Hold:pass
    print("GITHUB_PILOT_SELF_TEST=PASS")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true")
    p.add_argument("--worktree",default=".");p.add_argument("--owner",default=os.getenv("ENGURU_MK_OWNER",""))
    p.add_argument("--actor",default=os.getenv("ENGURU_MK_ACTOR",""))
    a=p.parse_args()
    try:
        if a.self_test:self_test()
        else:print(json.dumps(process(a.worktree,a.owner,a.actor),sort_keys=True))
    except Hold as e:
        print("STATE=HOLD_GITHUB_BRIDGE; REASON="+str(e))
        raise SystemExit(50)
