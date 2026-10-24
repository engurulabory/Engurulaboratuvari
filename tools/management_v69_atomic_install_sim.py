#!/usr/bin/env python3
"""Portable simulation of atomic install, idempotency, rollback and gates. No OSi access."""
import hashlib, tempfile, pathlib, json
def digest(b): return hashlib.sha256(b).hexdigest()
def install(root, payload, pin, inventory, fail_stage=None):
    dest=root/"app.bin"
    if not inventory.get("authorized") or not inventory.get("fresh") or inventory.get("arch")!="arm64":
        return "HOLD_PREFLIGHT"
    if not inventory.get("safe_path") or dest.is_symlink():return "HOLD_PATH"
    if digest(payload)!=pin:return "HOLD_SHA"
    previous=dest.read_bytes() if dest.exists() else None
    if previous==payload:return "PASS_IDEMPOTENT"
    candidate=root/"app.pending"
    if candidate.exists() or candidate.is_symlink():return "HOLD_PENDING_CONFLICT"
    try:
        candidate.write_bytes(payload)
        if fail_stage=="after_stage":raise RuntimeError("injected")
        if digest(candidate.read_bytes())!=pin:raise RuntimeError("stage SHA")
        candidate.replace(dest)
        if fail_stage=="after_replace":raise RuntimeError("injected")
        assert digest(dest.read_bytes())==pin
        return "PASS_INSTALL_SIMULATED"
    except Exception:
        if previous is None:
            dest.unlink(missing_ok=True)
        else:
            dest.write_bytes(previous)
        return "PASS_ROLLBACK_SIMULATED" if (dest.read_bytes() if dest.exists() else None)==previous else "FAIL_ROLLBACK"
    finally:
        candidate.unlink(missing_ok=True)
def run():
    payload=b"Enguru isolated product";pin=digest(payload)
    cases=0
    for round_id in range(3):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            inv=dict(authorized=True,fresh=True,arch="arm64",safe_path=True)
            assert install(root,payload,pin,inv)=="PASS_INSTALL_SIMULATED";cases+=1
            assert install(root,payload,pin,inv)=="PASS_IDEMPOTENT";cases+=1
            assert install(root,b"tampered",pin,inv)=="HOLD_SHA";cases+=1
            for k in ("authorized","fresh","safe_path"):
                bad=dict(inv,**{k:False})
                assert install(root,payload,pin,bad)=="HOLD_"+("PATH" if k=="safe_path" else "PREFLIGHT");cases+=1
            old=b"prior verified binary"
            (root/"app.bin").write_bytes(old)
            for stage in ("after_stage","after_replace"):
                assert install(root,payload,pin,inv,stage)=="PASS_ROLLBACK_SIMULATED"
                assert (root/"app.bin").read_bytes()==old;cases+=1
            assert install(root,payload,pin,dict(inv,arch="x86_64"))=="HOLD_PREFLIGHT";cases+=1
            (root/"app.bin").unlink()
            (root/"app.bin").symlink_to(root/"external")
            assert install(root,payload,pin,inv)=="HOLD_PATH";cases+=1
    print(json.dumps({"simulated_rounds":3,"checks":cases,"state":"PASS_ISOLATED_ATOMIC_INSTALL_SIM","real_osi":"HOLD","authority":"HOLD"}))
if __name__=="__main__":run()
