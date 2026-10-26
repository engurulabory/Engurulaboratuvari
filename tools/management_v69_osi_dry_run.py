#!/usr/bin/env python3
"""GitHub->OSi dry-run; uses synthetic inventory, performs zero Mac writes."""
import hashlib,json,tempfile,pathlib,zipfile
def sha(b):return hashlib.sha256(b).hexdigest()
def verify(spec,inventory,payload):
    errors=[]
    if inventory["os"]!=spec["os"]:errors.append("OS")
    if inventory["arch"]!=spec["arch"]:errors.append("ARCH")
    if inventory["free_mb"]<spec["disk_mb"]:errors.append("DISK")
    if spec["path"] not in inventory["allowed"]:errors.append("PATH")
    if spec["path"] in inventory["occupied"]:errors.append("CONFLICT")
    if sha(payload)!=spec["sha256"]:errors.append("SHA")
    if not inventory["authorized"]:errors.append("AUTHORITY")
    return errors
def main():
    payload=b"ENGURU SAFE PRODUCT DEMO V1"
    spec={"os":"macOS","arch":"arm64","disk_mb":100,"path":"~/Enguru/Apps/Demo","sha256":sha(payload)}
    base={"os":"macOS","arch":"arm64","free_mb":400,"allowed":[spec["path"]],"occupied":[],"authorized":True}
    cases={"valid":{},"wrong_os":{"os":"Linux"},"wrong_arch":{"arch":"x86_64"},"low_disk":{"free_mb":1},"path_guard":{"allowed":[]},"collision":{"occupied":[spec["path"]]},"missing_authority":{"authorized":False}}
    checks=0
    for round_no in range(3):
        for label,change in cases.items():
            result=verify(spec,{**base,**change},payload)
            assert (len(result)==0)==(label=="valid"),(round_no,label,result)
            checks+=1
    assert verify(spec,base,payload+b"tampered")==["SHA"]
    checks+=1
    with tempfile.TemporaryDirectory() as tmp:
        p=pathlib.Path(tmp)/"package.zip"
        with zipfile.ZipFile(p,"w") as z:z.writestr("product.txt",payload)
        with zipfile.ZipFile(p) as z:assert sha(z.read("product.txt"))==spec["sha256"]
    print(json.dumps({"state":"PASS_SYNTHETIC_SIMULATION","rounds":"3/3","checks":checks,"osi_mutation":0,"real_osi_inventory":"HOLD","github_three_final_ci":"HOLD","verified_finish":"HOLD"}))
if __name__=="__main__": main()
