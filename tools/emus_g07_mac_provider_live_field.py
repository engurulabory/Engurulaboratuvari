#!/usr/bin/env python3
"""EMUS G07 exact Mac Engineer provider -> Shared AI -> Ollama field probe."""
import argparse, hashlib, json, os, platform, subprocess, sys, time, types
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

def load_provider(repo, ref):
    p=subprocess.run(["git","-C",str(repo),"show",f"{ref}:runtime/provider.py"],capture_output=True,check=True)
    module=types.ModuleType("emus_pinned_mac_provider")
    exec(compile(p.stdout,"runtime/provider.py","exec"),module.__dict__)
    return module,hashlib.sha256(p.stdout).hexdigest()

def local_url(u,port):
    t=urlparse(u)
    return t.scheme=="http" and t.hostname in ("127.0.0.1","localhost") and t.port==port and not t.username and not t.password

def snapshot():
    with urlopen("http://127.0.0.1:11434/api/ps",timeout=5) as h:
        return json.load(h).get("models",[])

def collect(repo, ref):
    r={"schema":"enguru.emus.g07.mac-provider-live/v1","at":datetime.now(timezone.utc).isoformat(),"state":"HOLD","platform":platform.system()}
    if r["platform"]!="Darwin":return r
    if not local_url(os.environ.get("ENGURU_SHARED_AI_BASE_URL","http://127.0.0.1:8787"),8787):
        r["reason"]="ROUTER_NOT_LOOPBACK_8787";return r
    try:
        provider,source_hash=load_provider(repo,ref)
        r["provider_source_sha256"]=source_hash
        r["provider_source_ref"]=ref
        r["loaded_before"]=snapshot()
        vm=subprocess.run(["vm_stat"],capture_output=True,text=True,timeout=10)
        r["vm_before"]=vm.stdout[:4000]
        started=time.monotonic()
        result=provider.chat([{"role":"user","content":"Return precisely EMUS_G07_ROUTE_PASS"}])
        r["elapsed_s"]=round(time.monotonic()-started,3)
        r["chat_ok"]=result.get("ok") is True
        route=result.get("route_evidence",{})
        r["route"]={k:route.get(k) for k in ("provider","model","attempts","fallback_path","reason","estimated_cost")}
        r["response_match"]=result.get("text","").strip()=="EMUS_G07_ROUTE_PASS"
        r["loaded_after"]=snapshot()
        vm=subprocess.run(["vm_stat"],capture_output=True,text=True,timeout=10)
        r["vm_after"]=vm.stdout[:4000]
        # A source-pinned call confirms the adapter contract; independent GUI/app
        # acceptance and actual network-billing records are separately gated.
        r["state"]="FIELD_COLLECTED_ACCEPTANCE_PENDING"
    except Exception as ex:
        r["reason"]=type(ex).__name__
    return r

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--product-repo",type=Path,required=True)
    p.add_argument("--product-ref",required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists() or a.output.is_symlink():
        print("STATE=HOLD_OUTPUT_EXISTS");return 2
    r=collect(a.product_repo.expanduser(),a.product_ref)
    if r["platform"]!="Darwin":
        print("STATE=HOLD_MAC_REQUIRED");return 3
    a.output.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()
    with a.output.open("xb") as stream:stream.write(data)
    print("STATE="+r["state"]);print("EVIDENCE="+str(a.output))
    print("SHA256="+hashlib.sha256(data).hexdigest())
    return 0 if r["state"]=="FIELD_COLLECTED_ACCEPTANCE_PENDING" else 4
if __name__=="__main__":sys.exit(main())
