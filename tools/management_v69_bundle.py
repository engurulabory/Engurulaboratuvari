"""Read-only deterministic product bundle prototype. No installation operations."""
import io,zipfile,json,hashlib
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(o):return json.dumps(o,sort_keys=True,separators=(",",":")).encode()
def bundle(payload,inventory):
 if not isinstance(payload,bytes) or not payload:raise ValueError("HOLD_PAYLOAD")
 if not isinstance(inventory,dict) or inventory.get("source")!="SYNTHETIC" or inventory.get("arch")!="arm64":raise ValueError("HOLD_INVENTORY")
 manifest={"schema":"enguru.bundle.review.v1","payload_sha256":sha(payload),"inventory_sha256":sha(canonical(inventory)),"field_state":"HOLD"}
 out=io.BytesIO()
 with zipfile.ZipFile(out,"w") as z:
  for path,data in [("manifest.json",canonical(manifest)),("product.bin",payload)]:
   info=zipfile.ZipInfo(path,date_time=(2020,1,1,0,0,0));info.external_attr=0o600<<16;z.writestr(info,data)
 return out.getvalue()
def verify(blob,inventory):
 try:
  with zipfile.ZipFile(io.BytesIO(blob)) as z:
   if sorted(z.namelist())!=["manifest.json","product.bin"]:return "HOLD_LAYOUT"
   m=json.loads(z.read("manifest.json"))
   if set(m)!={"schema","payload_sha256","inventory_sha256","field_state"} or m["schema"]!="enguru.bundle.review.v1" or m["field_state"]!="HOLD":return "HOLD_MANIFEST"
   if m["inventory_sha256"]!=sha(canonical(inventory)):return "HOLD_DRIFT"
   if m["payload_sha256"]!=sha(z.read("product.bin")):return "HOLD_SHA"
   return "PASS_REVIEW_BUNDLE"
 except (ValueError,KeyError,TypeError,zipfile.BadZipFile):return "HOLD_BUNDLE"
