#!/usr/bin/env python3
# ENGURU PLive P02 -- single integrated canonical finish observation / OSi handoff
# GitHub design candidate. Standard library only. Read-only regarding canonical,
# installed applications and security authorities; writes receipts ONLY to AudiV13/Desktop.
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import unittest
from datetime import datetime, timezone

SCHEMA = "enguru.plive.p02.integrated-finish-readonly/v1"
ROOT_REL = "Enguru/Projects/Engurulaboratuvari"
BASELINE_HEAD = "269854b8a42a27e9419eae65a3c9e349bdcc7300"
BASELINE_SOURCE_PINS = {
    "governance/plive-p01-authorized-field/P01_ACCEPTANCE_FINAL_BINDING_V1.json":
        "e8847241b32960950a381bd179f56a7bbca8902a490ea226f72f3fe5a1c98510",
    "governance/plive-p01-authorized-field/STATE_V1.json":
        "68bc45cc41ed365d50b2e1b0476ecaaabfd0ccdfd21af54868276709cb877608",
    "governance/plive-p02-user-screen/PLIVE_P02_WORK_CONTRACT_V1.json":
        "1dc9b0bae00a13672a142fb91f6b1fe603f151bcebaa64482e297029deda7512",
    "governance/plive-p02-user-screen/STATE_V1.json":
        "ad29d034c8a97be75d69d972fca1c6e7ee207e7f7f1339e79b74e1ce6c40f432",
    "governance/plive-p02-user-screen/WORKLIST_V1.json":
        "4021dc7486363bc7baf503860969ea23324eabcbd4e3551930a20d79784532d2",
    "governance/progress-core/ENGURU_PROGRESS_CORE_PROJECT_REGISTRY_V1.json":
        "515748a88acffdd60be6afd4c837a2581a48a3bbeccd74c4a413ae3f986c4a80",
    "tools/enguru_progress.py":
        "f3e2610c6e325f6fd620baa84ec412437a015109dde88ac38cab7f08b2a365b4",
}
APP_IDENTIFIER = "local.enguru.plive.v31.isolated"
APP_VERSION = "0.3.1"
APP_BINARY_PIN = "32d533bed479434f77f848fd030c4330a2a33447e8e28d281f215bcb7b6db466"
AREA_IDS = ("motor", "core", "web", "app", "agent")
AREA_LABELS = ("Motor", "Çekirdek", "Web Yapımı", "Uygulama / App Yapımı", "Agent")
STAGES = ("Hakikati gör", "Değeri koru", "Eksikleri ve ihtiyaçları tespit et",
          "Gerekli farkı üret", "Eksikleri tamamla, ihtiyaçları karşıla",
          "Kanıtla", "Bir sonraki ihtiyaçları belirle", "İlerlet")
ITEMS = tuple(f"P02.S{pkg:02d}.{i:02d}" for pkg in range(1, 5) for i in range(1, 4))
DELIVERABLES = {
    "P02.S01.01": ("S01", "P01 korunumu / G3 ilk yetkili item", "Gerçek issuer + scope-grant + writer receipt"),
    "P02.S01.02": ("S01", "P02 Work Contract / Worklist / State", "Yetkili kayıt + kaynak sürümü"),
    "P02.S01.03": ("S01", "Progress Core registry bağı", "Native verify + S01 DoneCheck"),
    "P02.S02.01": ("S02", "Tek aktif OSi yürütme odağı", "Yetkili gerçek UI/progress bağı"),
    "P02.S02.02": ("S02", "A -> B -> A iş seçimi", "Gerçek Mac gözlemi"),
    "P02.S02.03": ("S02", "Gerçek ad / aşama / ilerleme", "Native ilerleme ve UI uyuşması"),
    "P02.S03.01": ("S03", "Üretim keşfi / beşli sınıflandırma", "Canonical primaryArea + negatif test"),
    "P02.S03.02": ("S03", "Canlı ekran yenileme", "Kaynaklı gerçek ekran ve insan gözlemi"),
    "P02.S03.03": ("S03", "Kaydırma / sürükleme / çakışma", "Mac kullanım ve erişilebilirlik gözlemi"),
    "P02.S04.01": ("S04", "Runtime G04 yetki ve süreklilik", "OS restart + kalıcı journal kanıtı"),
    "P02.S04.02": ("S04", "DoneCheck / bağımsız karşıt sınama", "4/4 gerçek paket DoneCheck"),
    "P02.S04.03": ("S04", "Human Threshold + Verified Finish", "7/7 saha, 12/12 item, human, native finish"),
}
PRIOR_OBSERVATIONS = {
    "P01": "2/2 LOCKED VERIFIED (previous exact native receipt)",
    "P02": "0/12 HOLD (previous exact native receipt)",
    "V31": "Five headings visible; user observed selection, Cmd-R and Finder relaunch; not official P02 countedPass",
    "classifiedProjectRecords": 0,
    "unclassifiedProjectRecords": 7,
    "foundUnbound": 5,
    "plannedOutOfCounter": 8,
    "donecheck": "0/4 (older observation, MUST re-read for current)",
    "fieldPrerequisites": "1/7 (older observation, MUST re-read for current)",
    "authority": "G3 issuer/grant/writer NOT demonstrated in prior field receipts",
}

def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())

def check_regular(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()

def verify_source_pins(root: Path, pins=BASELINE_SOURCE_PINS) -> dict:
    results = {}
    for rel, expected in pins.items():
        p = root / rel
        if not check_regular(p):
            results[rel] = {"state": "HOLD_MISSING_OR_SYMLINK", "expectedSha256": expected}
            continue
        observed = digest_file(p)
        results[rel] = {
            "state": "PASS" if observed == expected else "HOLD_CHANGED_REQUALIFICATION_REQUIRED",
            "sha256": observed, "expectedSha256": expected, "bytes": p.stat().st_size
        }
    return results

def native_pairs(text: str) -> dict:
    """Parse native verify output; never interpret a test PASS as countedPass."""
    mapping = {}
    for raw in text.splitlines():
        m = re.match(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s{2,}(\S.*?)\s*$", raw)
        if m:
            mapping[m.group(1)] = m.group(2).strip()
    return mapping

def native_qualified(m: dict, kind: str) -> tuple[bool, list[str]]:
    why = []
    required = ("project", "worklist", "state", "itemSetAgreement",
                "deterministicProjection", "progressIntegrity", "countedPass",
                "unverifiedPass", "stateDrift", "finishState")
    for k in required:
        if k not in m:
            why.append("MISSING_NATIVE_" + k)
    if why:
        return False, why
    if m["project"] != ("plive-p01-authorized-field" if kind == "P01" else "plive-p02-user-screen"):
        why.append("PROJECT_ID_MISMATCH")
    for k in ("worklist", "state", "itemSetAgreement", "deterministicProjection", "progressIntegrity"):
        if m[k] != "PASS":
            why.append("NATIVE_" + k + "_NOT_PASS")
    if m["stateDrift"] != "NONE" or m["unverifiedPass"] != "0":
        why.append("STATE_DRIFT_OR_UNVERIFIED_PASS")
    try:
        counted = int(m["countedPass"])
    except (ValueError, KeyError):
        why.append("NONNUMERIC_COUNTED_PASS")
        counted = -1
    if kind == "P01":
        if counted != 2 or m["finishState"] != "VERIFIED":
            why.append("P01_LAST_FINISH_NOT_VERIFIED")
    else:
        if not (0 <= counted <= 12):
            why.append("P02_COUNT_OUT_OF_SCOPE")
        if counted != 12 and m["finishState"] == "VERIFIED":
            why.append("P02_EARLY_FINISH")
    return not why, why

def extract_item_ids(worklist: object) -> list[str]:
    """Find only explicit item IDs, not inferred project names or progress."""
    serialized = json.dumps(worklist, ensure_ascii=False)
    return sorted(set(re.findall(r"P02\.S0[1-4]\.0[1-3]", serialized)))

def classify_projects(projects: list[dict]) -> dict:
    """Presentation candidates only. Never mutate source, infer from name or count twice."""
    areas = {k: [] for k in AREA_IDS}
    unknown, seen = [], set()
    for item in projects:
        if not isinstance(item, dict) or not isinstance(item.get("projectId"), str):
            return {"state": "HOLD_BAD_SOURCE_PROJECT", "areas": areas, "unknown": unknown}
        pid = item["projectId"]
        if not pid or pid in seen:
            return {"state": "HOLD_DUPLICATE_PROJECT_ID", "areas": areas, "unknown": unknown}
        seen.add(pid)
        area = item.get("primaryArea")
        if area in AREA_IDS:
            areas[area].append(pid)
        else:
            unknown.append(pid)
    return {"state": "PASS_PRESENTATION_ONLY", "areas": areas, "unknown": unknown}

def finish_predicate(*, items, donechecks, field_gates, human, native_finish, authority) -> dict:
    """Simulation is never a production grant or official acceptance."""
    gates = {
        "items": type(items) is int and items == 12,
        "donechecks": type(donechecks) is int and donechecks == 4,
        "field": type(field_gates) is int and field_gates == 7,
        "human": human == "ACCEPTED",
        "native": native_finish == "VERIFIED",
        "authority": authority == "REAL_VERIFIED_P02_AUTHORITY",
    }
    return {"modelAllPredicatesTrue": all(gates.values()),
            "officiallyAccepted": False,
            "predicates": gates,
            "verdict": "MODEL_READY_FOR_REAL_AUTHORIZED_REVIEW" if all(gates.values()) else "HOLD_GUVENLI_DUR"}

def run_readonly(command: list[str], cwd: Path | None = None, timeout: int = 25) -> dict:
    try:
        r = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout,
                           check=False, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return {"rc": r.returncode, "stdout": r.stdout[-16000:], "stderr": r.stderr[-4000:]}
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"rc": 99, "stdout": "", "stderr": type(e).__name__ + ": " + str(e)}

def inspect_app(app: Path) -> dict:
    result = {"path": str(app), "status": "HOLD_NOT_FOUND"}
    try:
        info = app / "Contents/Info.plist"
        binary = app / "Contents/MacOS/PLive"
        if app.is_symlink() or not app.is_dir() or not check_regular(info) or not check_regular(binary):
            return result
        p = plistlib.loads(info.read_bytes())
        ident = p.get("CFBundleIdentifier")
        version = p.get("CFBundleShortVersionString")
        bsha = digest_file(binary)
        matches = (ident == APP_IDENTIFIER and version == APP_VERSION and bsha == APP_BINARY_PIN)
        return {"path": str(app), "status": "PASS_PINNED_IDENTITY" if matches else "HOLD_IDENTITY_CHANGE",
                "bundleID": ident, "version": version, "binarySha256": bsha, "expectedBinarySha256": APP_BINARY_PIN}
    except (OSError, ValueError, TypeError, plistlib.InvalidFileException) as e:
        return {"path": str(app), "status": "HOLD_READ", "reason": str(e)[:500]}

class AdversarialTests(unittest.TestCase):
    def test_eight_stages(self): self.assertEqual(len(STAGES), 8)
    def test_no_new_p02_items(self): self.assertEqual(len(ITEMS), 12)
    def test_four_packages(self): self.assertEqual({x[:7] for x in ITEMS}, {"P02.S01", "P02.S02", "P02.S03", "P02.S04"})
    def test_exact_item_contract(self): self.assertEqual(set(ITEMS), set(DELIVERABLES))
    def test_five_areas(self): self.assertEqual(len(AREA_IDS), 5)
    def test_names_not_categories(self): self.assertNotIn("LABORATUVAR", AREA_IDS)
    def test_native_zero_p02(self):
        v = dict(project="plive-p02-user-screen", worklist="PASS", state="PASS",
                 itemSetAgreement="PASS", deterministicProjection="PASS",
                 progressIntegrity="PASS", stateDrift="NONE",
                 unverifiedPass="0", countedPass="0", finishState="HOLD")
        self.assertTrue(native_qualified(v, "P02")[0])
    def test_early_finish_denied(self):
        v = dict(project="plive-p02-user-screen", worklist="PASS", state="PASS",
                 itemSetAgreement="PASS", deterministicProjection="PASS",
                 progressIntegrity="PASS", stateDrift="NONE",
                 unverifiedPass="0", countedPass="0", finishState="VERIFIED")
        self.assertFalse(native_qualified(v, "P02")[0])
    def test_project_confusion_denied(self):
        v = dict(project="OTHER", worklist="PASS", state="PASS",
                 itemSetAgreement="PASS", deterministicProjection="PASS",
                 progressIntegrity="PASS", stateDrift="NONE",
                 unverifiedPass="0", countedPass="2", finishState="VERIFIED")
        self.assertFalse(native_qualified(v, "P01")[0])
    def test_no_raw_pass_promotion(self):
        self.assertFalse(finish_predicate(items=12, donechecks=4, field_gates=7,
                                          human="ACCEPTED", native_finish="VERIFIED",
                                          authority="REAL_VERIFIED_P02_AUTHORITY")["officiallyAccepted"])
    def test_all_gates_math(self):
        x = finish_predicate(items=12, donechecks=4, field_gates=7,
                             human="ACCEPTED", native_finish="VERIFIED",
                             authority="REAL_VERIFIED_P02_AUTHORITY")
        self.assertTrue(x["modelAllPredicatesTrue"])
        self.assertEqual(x["verdict"], "MODEL_READY_FOR_REAL_AUTHORIZED_REVIEW")
    def test_unqualified_authority_denied(self):
        self.assertEqual(finish_predicate(items=12, donechecks=4, field_gates=7,
                            human="ACCEPTED", native_finish="VERIFIED",
                            authority="HOLD")["verdict"], "HOLD_GUVENLI_DUR")
    def test_duplicate_project_denied(self):
        self.assertEqual(classify_projects([{"projectId":"a"}, {"projectId":"a"}])["state"], "HOLD_DUPLICATE_PROJECT_ID")
    def test_unknown_area_visible(self):
        r = classify_projects([{"projectId":"a", "name":"Agent"}, {"projectId":"b", "primaryArea":"web"}])
        self.assertEqual(r["unknown"], ["a"])
        self.assertEqual(r["areas"]["web"], ["b"])
    def test_no_double_count(self):
        r = classify_projects([{"projectId":"a", "primaryArea":"agent", "crossTags":["web", "core"]}])
        self.assertEqual(sum(len(x) for x in r["areas"].values())+len(r["unknown"]), 1)
    def test_native_parser(self):
        s = "project                   plive-p02-user-screen\ncountedPass               0\nfinishState               HOLD\n"
        self.assertEqual(native_pairs(s)["countedPass"], "0")
    def test_worklist_regex(self):
        self.assertEqual(extract_item_ids({"items": list(ITEMS)}), list(ITEMS))
    def test_missing_worklist_rejected(self):
        self.assertNotEqual(extract_item_ids({"items":list(ITEMS)[:-1]}), list(ITEMS))
    def test_invalid_issuer_fixture_denied(self):
        self.assertFalse(finish_predicate(items=12, donechecks=4, field_gates=7,
                             human="ACCEPTED", native_finish="VERIFIED",
                             authority="FAKE_FIXTURE")["modelAllPredicatesTrue"])
    def test_finish_requires_true_human(self):
        self.assertFalse(finish_predicate(items=12, donechecks=4, field_gates=7,
                             human="PENDING", native_finish="VERIFIED",
                             authority="REAL_VERIFIED_P02_AUTHORITY")["modelAllPredicatesTrue"])
    def test_finish_requires_native(self):
        self.assertFalse(finish_predicate(items=12, donechecks=4, field_gates=7,
                             human="ACCEPTED", native_finish="HOLD",
                             authority="REAL_VERIFIED_P02_AUTHORITY")["modelAllPredicatesTrue"])
    def test_invalid_count_boolean(self):
        self.assertFalse(finish_predicate(items=True, donechecks=4, field_gates=7,
                             human="ACCEPTED", native_finish="VERIFIED",
                             authority="REAL_VERIFIED_P02_AUTHORITY")["modelAllPredicatesTrue"])
    def test_immutable_classification_input(self):
        src=[{"projectId":"x", "primaryArea":"web"}]
        original=json.dumps(src)
        classify_projects(src)
        self.assertEqual(json.dumps(src), original)

# Additional per-item acceptance negatives: each missing item/gate remains HOLD.
def _extra_tests():
    for idx in range(12):
        def check(self, idx=idx):
            ids = list(ITEMS)
            ids.pop(idx)
            self.assertNotEqual(ids, list(ITEMS))
            self.assertEqual(len(ids), 11)
        setattr(AdversarialTests, "test_missing_item_%02d" % (idx+1), check)
    for missing in ("items", "donechecks", "field_gates", "human", "native_finish", "authority"):
        def check(self, missing=missing):
            a = dict(items=12, donechecks=4, field_gates=7, human="ACCEPTED",
                     native_finish="VERIFIED", authority="REAL_VERIFIED_P02_AUTHORITY")
            a[missing] = None
            self.assertFalse(finish_predicate(**a)["modelAllPredicatesTrue"])
        setattr(AdversarialTests, "test_missing_finish_%s" % missing, check)
_extra_tests()

def test_suite() -> tuple[bool, int, int]:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AdversarialTests)
    result = unittest.TextTestRunner(verbosity=0, stream=sys.stderr).run(suite)
    print(f"PRE_OSi_ADVERSARIAL={result.testsRun-result.failures.__len__()-result.errors.__len__()}/{result.testsRun}")
    return result.wasSuccessful(), result.testsRun, len(result.failures)+len(result.errors)

def observe():
    passed, n, errors = test_suite()
    if not passed:
        print("STATE=HOLD_PRE_OSi_SIMULATION")
        return 4
    home = Path.home()
    root = home / ROOT_REL
    audi = home / "Desktop/AudiV13"
    report = {
        "schema": SCHEMA,
        "scope": "READ_ONLY_OSi_SOURCE_AND_NATIVE_READBACK",
        "eightStages": list(STAGES),
        "baselineHead": BASELINE_HEAD,
        "gitHubSource": "engurulabory/Engurulaboratuvari PR #188 architecture baseline + P02 closure draft",
        "preOSiSimulation": {"pass": n, "total": n, "failures": errors},
        "p01": {}, "p02": {}, "app": {}, "source": {},
        "requiredFinish": {
            "countedItems": "12/12", "packageDoneChecks": "4/4",
            "existingFieldPrerequisites": "7/7", "humanThreshold": "ACCEPTED",
            "nativeFinish": "VERIFIED", "realExistingIssuerGrantWriter": "REQUIRED"
        },
        "worklist": [{"id": k, "package": v[0], "deliverable": v[1],
                      "acceptanceEvidence": v[2], "officialPass": "READ_NATIVE_ONLY"}
                     for k,v in DELIVERABLES.items()],
        "priorObservationCandidates": PRIOR_OBSERVATIONS,
        "categoryRule": "ONLY_EXPLICIT_CANONICAL_PRIMARY_AREA__UNKNOWN_VISIBLE__NO_DUPLICATE_COUNT",
        "positiveLanguage": {"PASS":"Doğrulandı", "HOLD":"Yetkili kanıt / kaynak bağı bekliyor",
                             "NEXT":"Bir sonraki yapılabilir adım"},
        "authorityClaim": "NO_GRANT__NO_SIGNING__NO_WRITER__NO_HUMAN_THRESHOLD",
        "canonicalWrites": 0,
        "productionWrites": 0,
    }
    blockers = []
    if not audi.is_dir() or audi.is_symlink():
        print("STATE=HOLD_AudiV13_ARCHIVE_MISSING")
        return 5
    if root.is_symlink() or not root.is_dir():
        blockers.append("OSi_ROOT_NOT_AVAILABLE")
    head = run_readonly(["/usr/bin/git", "rev-parse", "HEAD"], cwd=root) if not blockers else {"rc":99,"stdout":"","stderr":"root unavailable"}
    branch = run_readonly(["/usr/bin/git", "branch", "--show-current"], cwd=root) if not blockers else {"rc":99,"stdout":"","stderr":"root unavailable"}
    status_before = run_readonly(["/usr/bin/git", "status", "--porcelain", "--untracked-files=no"], cwd=root) if not blockers else {"rc":99,"stdout":"","stderr":"root unavailable"}
    head_sha = head["stdout"].strip()
    report["git"] = {"head":head_sha, "headExpected":BASELINE_HEAD,
                     "branch":branch["stdout"].strip(), "trackedStatusBefore":status_before["stdout"].splitlines()}
    if head["rc"] != 0 or head_sha != BASELINE_HEAD:
        blockers.append("OSi_HEAD_CHANGED__REQUALIFY_EXACT_SOURCE")
    if not blockers:
        first_pins = verify_source_pins(root)
        report["source"] = first_pins
        if any(v["state"]!="PASS" for v in first_pins.values()):
            blockers.append("SOURCE_PIN_CHANGED__REQUALIFY_EXACT_SOURCE")
    else:
        first_pins = {}
    if not blockers:
        p02work = json.loads((root / "governance/plive-p02-user-screen/WORKLIST_V1.json").read_text(encoding="utf-8"))
        IDs = extract_item_ids(p02work)
        report["p02"]["canonicalIds"] = IDs
        report["p02"]["packageIds"] = sorted(set(x[:7] for x in IDs))
        if IDs != list(ITEMS):
            blockers.append("P02_WORKLIST_ITEM_SET_CHANGED")
        p01state = json.loads((root / "governance/plive-p01-authorized-field/STATE_V1.json").read_text(encoding="utf-8"))
        report["p01"]["stateVerifiedFinish"] = p01state.get("verifiedFinish")
        if p01state.get("verifiedFinish") != "LOCKED":
            blockers.append("P01_STATE_REQUIRES_RECONCILIATION")
        app = home / "Applications/ENGURU-PLive-V31.app"
        report["app"] = inspect_app(app)
        if report["app"]["status"]!="PASS_PINNED_IDENTITY":
            blockers.append("USER_APP_IDENTITY_OR_INSTALL_REQUIRES_REVIEW")
        for kind, slug in (("P01","plive-p01-authorized-field"),("P02","plive-p02-user-screen")):
            proc = run_readonly([sys.executable, "-B", "tools/enguru_progress.py", slug, "--verify"], cwd=root)
            parsed = native_pairs(proc["stdout"])
            qualified, reasons = native_qualified(parsed, kind)
            report[kind.lower()]["native"]={"returnCode":proc["rc"],"parsed":parsed,"qualified":qualified,
                                            "reason":reasons,"stderr":proc["stderr"]}
            if proc["rc"] != 0 or not qualified:
                blockers.append(kind+"_NATIVE_VERIFY_REQUIRES_REVIEW")
    if root.is_dir() and not root.is_symlink():
        report["sourceAfter"] = verify_source_pins(root) if first_pins else {}
        if first_pins and report["sourceAfter"] != first_pins:
            blockers.append("SOURCE_DRIFT_DURING_READONLY")
        status_after = run_readonly(["/usr/bin/git", "status", "--porcelain", "--untracked-files=no"], cwd=root)
        report["git"]["trackedStatusAfter"] = status_after["stdout"].splitlines()
        if status_before["rc"] == 0 and (status_after["rc"] != 0 or status_before["stdout"] != status_after["stdout"]):
            blockers.append("TRACKED_WORKTREE_CHANGED_DURING_READONLY")
        head_after = run_readonly(["/usr/bin/git", "rev-parse", "HEAD"],cwd=root)
        report["git"]["headAfter"] = head_after["stdout"].strip()
        if head_sha and report["git"]["headAfter"] != head_sha:
            blockers.append("HEAD_CHANGED_DURING_READONLY")
    # Authority cannot be demonstrated by these observations: always fail closed.
    report["authorityState"] = "G3_REAL_ISSUER_GRANT_WRITER_REQUIRES_SEPARATE_HUMAN_AND_SECURITY_REVIEW"
    report["officialP02Acceptance"] = "NATIVE_SNAPSHOT_ONLY__NO_PROMOTION_FROM_THIS_AUDIT"
    report["donecheckNow"] = "NOT_MEASURED_BY_THIS_READONLY_AUDIT"
    report["sevenFieldPrerequisitesNow"] = "NOT_MEASURED_BY_THIS_READONLY_AUDIT"
    report["humanThresholdNow"] = "NOT_ACCEPTED_BY_THIS_AUDIT"
    report["nextAuthorizedAction"] = {
        "sortie":"S01", "item":"P02.S01.01",
        "action":"Verify real approved independent trust root, issuer identity, private key custody, revoke policy, bounded pilot grant and authorized writer with existing security owner. No self-grant.",
        "onUnverified":"HOLD_WITH_BLOCKER_OWNER_AND_NO_CANONICAL_WRITE",
        "then":"With separately approved real grant, first exact-scope native P02 item pilot; native readback; S01 completion, then existing S02/S03/S04 in dependency order."
    }
    report["blockers"] = list(dict.fromkeys(blockers))
    report["state"] = ("PASS_READONLY_RECONCILIATION__OFFICIAL_P02_HOLD" if not blockers
                       else "HOLD_SAFE_OSi_REQUALIFICATION")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    name = "ENGURU_PLIVE_P02_BUTUNLESIK_SAHA_"+stamp+".json"
    raw = (json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)+"\n").encode("utf-8")
    original = audi / name
    upload = home / "Desktop" / name
    if upload.exists() or original.exists() or upload.is_symlink() or original.is_symlink():
        print("STATE=HOLD_REPORT_NAME_COLLISION")
        return 6
    try:
        with original.open("xb") as f: f.write(raw)
        with upload.open("xb") as f: f.write(raw)
        if digest_file(original) != digest_file(upload):
            print("STATE=HOLD_RECEIPT_COPY_INTEGRITY")
            return 7
    except OSError as e:
        print("STATE=HOLD_REPORT_WRITE "+str(e))
        return 8
    print("PRE_OSi_SOURCE_PINS="+str(sum(v["state"]=="PASS" for v in first_pins.values()))+"/7")
    print("P01_NATIVE="+report.get("p01",{}).get("native",{}).get("parsed",{}).get("countedPass","UNREAD")+"/2")
    print("P02_NATIVE="+report.get("p02",{}).get("native",{}).get("parsed",{}).get("countedPass","UNREAD")+"/12")
    print("APPLICATION="+report.get("app",{}).get("status","UNREAD"))
    print("AUTHORITY=HOLD_REAL_G3_REVIEW")
    print("CANONICAL_WRITES=0")
    print("STATE="+report["state"])
    print("REPORT_SHA256="+digest_file(original))
    print("UPLOAD="+str(upload))
    return 0 if not blockers else 20

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="PLive P02 Süzgeç v2.4 integrated read-only OSi closure handoff")
    parser.add_argument("--self-test", action="store_true", help="isolated adversarial model; no OSi")
    parser.add_argument("--observe", action="store_true", help="OSi source/readback + AudiV13 receipt; no canonical writes")
    args=parser.parse_args()
    if args.self_test: sys.exit(0 if test_suite()[0] else 3)
    if args.observe: sys.exit(observe())
    parser.print_help()
