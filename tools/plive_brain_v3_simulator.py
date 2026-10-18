"""Pure PLive brain architecture simulator. Not runtime, issuer, writer or progress authority.

All inputs are in-memory fixtures. No file writes, no network, no macOS Keychain,
no canonical state mutations. Used only to adversarially validate V3 contract.
"""
from __future__ import annotations
import json
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "governance/plive/ENGURU_PLIVE_BRAIN_ARCHITECTURE_V3.json"
AREA_IDS = ("motor", "core", "web", "app", "agent")
FACETS = ("LABORATUVAR", "ANA_FABRIKA")
STAGES = ("Hakikati gör", "Değeri koru", "Eksikleri ve ihtiyaçları tespit et",
          "Gerekli farkı üret", "Eksikleri tamamla, ihtiyaçları karşıla",
          "Kanıtla", "Bir sonraki ihtiyaçları belirle", "İlerlet")
REQUIRED_FINISH = ("12/12_COUNTED_PASS", "4/4_PACKAGE_DONECHECK",
                   "7/7_EXISTING_FIELD_PREREQUISITES", "HUMAN_THRESHOLD_ACCEPTED",
                   "NATIVE_VERIFIED_FINISH")
STALE_CANDIDATE_SECONDS = 300  # engineering fixture threshold; not OSi official SLA


def contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _at(data, path):
    cur = data
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def coverage(data):
    """Design specification gate score; NOT implementation or field acceptance."""
    g = data.get("acceptance", {}).get("designGates", [])
    if len(g) != 10 or len({v.get("id") for v in g}) != 10:
        return 0
    if sorted(v.get("points", 0) for v in g) != [10] * 10:
        return 0
    if [v.get("id") for v in g] != ["A%02d" % n for n in range(1, 11)]:
        return 0
    if data.get("method", {}).get("stages") != list(STAGES):
        return 0
    if not all(data.get("method", {}).get(k) is True
               for k in ("noNewCore", "noNinthStage", "noParallelProgress")):
        return 0
    if [x.get("id") for x in data.get("screen", {}).get("categories", [])] != list(AREA_IDS):
        return 0
    if data.get("production", {}).get("facet") != list(FACETS):
        return 0
    for obj, fields in (("screen", ("alwaysShowFive", "noSixthCategory", "singlePrimaryOwner", "readOnlyWithoutGrant")),
                        ("production", ("categoryOrthogonalToFacet",)),
                        ("userAuthority", ("noSelfGrant", "noImplicitReuseBetweenProjects")),
                        ("sources", ("sameInputSameOutput", "neverPromoteTechnicalPass")),
                        ("evidence", ("nativeProgressOnly", "technicalVsOfficialSeparate")),
                        ("execution", ("engineeringMayNotIssueGrants",))):
        if any(data.get(obj, {}).get(field) is not True for field in fields):
            return 0
    if data.get("acceptance", {}).get("p02FinishNeeds") != list(REQUIRED_FINISH):
        return 0
    if data.get("acceptance", {}).get("noAutomaticFieldPromotion") is not True:
        return 0
    if data.get("readiness", {}).get("githubModelSimulationOnly") is not True:
        return 0
    points = 0
    for gate in g:
        required = gate.get("requires") or []
        if not required or not gate.get("name"):
            continue
        if all(_at(data, p) is not None and _at(data, p) is not False
               and _at(data, p) not in ("", [], {}) for p in required):
            points += 10
    return points


def ready_items(items, accepted):
    """Deterministic candidate ordering, not an operator scheduler."""
    if not isinstance(items, list) or not isinstance(accepted, (list, set, tuple)):
        return {"state": "HOLD", "reason": "INPUT_TYPE"}
    ids = [x.get("workId") for x in items if isinstance(x, dict)]
    if len(ids) != len(items) or len(set(ids)) != len(ids) or not all(isinstance(k, str) and k for k in ids):
        return {"state": "HOLD", "reason": "DUPLICATE_OR_INVALID_WORK_ID"}
    by_id = {x["workId"]: x for x in items}
    for x in items:
        if type(x.get("priority")) is not int or not isinstance(x.get("dependsOn"), list):
            return {"state": "HOLD", "reason": "BAD_PRIORITY_OR_DEPENDENCY"}
        if any(d not in by_id or not isinstance(d, str) for d in x["dependsOn"]):
            return {"state": "HOLD", "reason": "UNKNOWN_DEPENDENCY"}
    colors = {}
    def visit(node):
        if colors.get(node) == 1:
            return False
        if colors.get(node) == 2:
            return True
        colors[node] = 1
        if not all(visit(d) for d in by_id[node]["dependsOn"]):
            return False
        colors[node] = 2
        return True
    if not all(visit(k) for k in ids):
        return {"state": "HOLD", "reason": "DEPENDENCY_CYCLE"}
    accepted_set = set(accepted)
    if not accepted_set <= set(ids):
        return {"state": "HOLD", "reason": "UNREGISTERED_ACCEPTED_ITEM"}
    candidate = [x for x in items if x["workId"] not in accepted_set and
                 all(d in accepted_set for d in x["dependsOn"])]
    candidate.sort(key=lambda x: (x["priority"], x["workId"]))
    return {"state": "PASS_MODEL_ONLY", "ready": [x["workId"] for x in candidate]}


def read_projection(snapshot, now):
    """Five visible production headings, native readback only, fail-closed."""
    empty = {a: [] for a in AREA_IDS}
    if not isinstance(snapshot, dict) or not isinstance(now, int):
        return {"state": "HOLD", "reason": "INPUT_TYPE", "areas": empty}
    source = snapshot.get("source", {})
    native = snapshot.get("native", {})
    if not isinstance(source, dict) or source.get("valid") is not True or not source.get("head"):
        return {"state": "HOLD", "reason": "UNVERIFIED_SOURCE", "areas": empty}
    read_at = source.get("readAt")
    if type(read_at) is not int or read_at > now:
        return {"state": "HOLD", "reason": "BAD_SOURCE_TIME", "areas": empty}
    if not isinstance(native, dict) or native.get("verified") is not True:
        return {"state": "HOLD", "reason": "NATIVE_PROGRESS_NOT_VERIFIED", "areas": empty}
    done, total = native.get("countedPass"), native.get("total")
    if type(done) is not int or type(total) is not int or total <= 0 or not (0 <= done <= total):
        return {"state": "HOLD", "reason": "INVALID_NATIVE_COUNTER", "areas": empty}
    if native.get("finish") == "VERIFIED" and done != total:
        return {"state": "HOLD", "reason": "FINISH_COUNT_CONTRADICTION", "areas": empty}
    areas = {a: [] for a in AREA_IDS}
    unknown = []
    seen = set()
    projects = snapshot.get("workItems", [])
    if not isinstance(projects, list):
        return {"state": "HOLD", "reason": "BAD_WORK_ITEMS", "areas": empty}
    for item in projects:
        if not isinstance(item, dict) or not isinstance(item.get("workId"), str) or not item["workId"]:
            return {"state": "HOLD", "reason": "BAD_WORK_ID", "areas": empty}
        ident = item["workId"]
        if ident in seen:
            return {"state": "HOLD", "reason": "DUPLICATE_WORK_ID", "areas": empty}
        seen.add(ident)
        category = item.get("primaryArea")
        facet = item.get("facet")
        if facet not in FACETS and facet is not None:
            return {"state": "HOLD", "reason": "INVALID_FACET", "areas": empty}
        compact = {"workId": ident, "facet": facet or "KAYNAK_BEKLIYOR"}
        if category not in AREA_IDS:
            unknown.append(compact)
        else:
            areas[category].append(compact)
    for k in AREA_IDS:
        areas[k].sort(key=lambda x: x["workId"])
    unknown.sort(key=lambda x: x["workId"])
    p01 = snapshot.get("p01", {})
    p01_verified = isinstance(p01, dict) and p01.get("bindingValid") is True and \
        p01.get("nativeVerified") is True and p01.get("countedPass") == 2 and p01.get("total") == 2
    freshness = "SON_DOGRULANMIS_OKUMA" if now - read_at > STALE_CANDIDATE_SECONDS else "CANLI_DOGRULANMIS_KAYNAK"
    return {"state": "PASS_MODEL_ONLY", "areas": areas, "unknown": unknown,
            "p01": "DOGRULANDI_KILITLI" if p01_verified else "DURUM_DOGRULANIYOR",
            "native": {"countedPass": done, "total": total, "finish": native.get("finish")},
            "freshness": freshness, "readAt": read_at,
            "officialFinish": "MODEL_DISPLAY_ONLY_NOT_AUTHORITY"}


def lab_to_factory_handoff(record, owner_approved):
    """Lab qualification does not move canonical items or count any item twice."""
    if not isinstance(record, dict) or owner_approved is not True:
        return {"state": "HOLD", "reason": "NO_EXPLICIT_OWNER_APPROVAL"}
    required = ("source_project_id", "source_head", "evidence_sha256", "scope",
                "qualification_receipt")
    if any(not isinstance(record.get(k), str) or not record[k] for k in required):
        return {"state": "HOLD", "reason": "INCOMPLETE_PROVENANCE"}
    if record.get("sourceFacet") != "LABORATUVAR" or record.get("targetFacet") != "ANA_FABRIKA":
        return {"state": "HOLD", "reason": "INCORRECT_FACET_TRANSITION"}
    if record.get("canonicalWrite") or record.get("newWorkId"):
        return {"state": "HOLD", "reason": "IMPLICIT_CANONICAL_PROMOTION"}
    return {"state": "QUALIFIED_HANDOFF_CANDIDATE_ONLY", "canonicalWrites": 0}


def privileged_decision(request, grant, writer, now):
    """Decision-only verifier; cannot mint grants, write state or claim authorization."""
    if not isinstance(request, dict) or not isinstance(grant, dict) or not isinstance(writer, dict):
        return {"state": "HOLD", "reason": "MISSING_VERIFIED_AUTHORITY"}
    if request.get("ownerExplicit") is not True or grant.get("issuerVerified") is not True or \
       grant.get("signatureVerified") is not True or writer.get("accepted") is not True:
        return {"state": "HOLD", "reason": "MISSING_VERIFIED_AUTHORITY"}
    for k in ("projectId", "workId", "action", "sourceHead"):
        if not request.get(k) or request.get(k) != grant.get(k):
            return {"state": "HOLD", "reason": "SCOPE_MISMATCH"}
    if type(grant.get("expiresAt")) is not int or type(now) is not int or grant["expiresAt"] <= now:
        return {"state": "HOLD", "reason": "EXPIRED_GRANT"}
    if not grant.get("nonce") or grant.get("nonceConsumed") is True:
        return {"state": "HOLD", "reason": "REPLAY_OR_MISSING_NONCE"}
    return {"state": "READY_FOR_AUTHORIZED_OSI_FIELD_REVIEW_ONLY",
            "canonicalWrites": 0, "grantIssued": False}


def simulated_finish(counted, donechecks, gates, human, native_finish):
    """Mathematical predicate only; model NEVER declares project PASS."""
    complete = (type(counted) is int and counted == 12
                and type(donechecks) is int and donechecks == 4
                and type(gates) is int and gates == 7
                and human == "ACCEPTED" and native_finish == "VERIFIED")
    return {"state": ("MODEL_FINISH_CONDITIONS_MET_ONLY" if complete else "HOLD"),
            "officialPassGranted": False, "nativeWrites": 0}
