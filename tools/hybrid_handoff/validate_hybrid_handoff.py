#!/usr/bin/env python3
"""ENGÜRÜ Hybrid Handoff v1: fail-closed GitHub preflight (not OSi finalization)."""
import argparse
import copy
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

SCHEMA = "enguru.mac-engineer.hybrid-handoff/v1"
MODES = {"GITHUB_FIRST", "OSI_FIRST", "HYBRID"}
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")
GATES = ("state", "claim", "evidence", "judgment", "nextAction")
FIVE_AXES = ("THEORY", "DESIGN", "SIM1", "SIM2", "SIM3")


def validate(data, *, mode="template"):
    errors = []
    if mode not in {"template", "handoff", "project"}:
        return ["MODE_INVALID"]
    if not isinstance(data, dict):
        return ["ROOT_NOT_OBJECT"]
    if data.get("schema") != SCHEMA:
        errors.append("SCHEMA_MISMATCH")
    if mode == "template":
        if data.get("state") != "PENDING" or data.get("verifiedFinish") != "HOLD":
            errors.append("TEMPLATE_PREMATURE_FINISH")
    if mode in {"handoff", "project"}:
        if not data.get("projectId") or not data.get("subproduct"):
            errors.append("PROJECT_IDENTITY_MISSING")
        if not isinstance(data.get("executionMode"), str) or data["executionMode"] not in MODES:
            errors.append("EXECUTION_MODE_INVALID")
        if not data.get("canonicalRepo") or not data.get("sourceRef"):
            errors.append("SOURCE_IDENTITY_MISSING")
        if not HEX40.fullmatch(str(data.get("sourceCommit") or "")):
            errors.append("SOURCE_COMMIT_INVALID")
        if not HEX64.fullmatch(str(data.get("artifactDigest") or "")):
            errors.append("ARTIFACT_DIGEST_INVALID")
    suzgec = data.get("suzgec")
    if not isinstance(suzgec, dict) or any(k not in suzgec for k in GATES):
        errors.append("SUZGEC_DECISION_SEQUENCE_MISSING")
        suzgec = {}
    if data.get("verifiedFinish") == "LOCKED":
        # GitHub is deliberately incapable of asserting field acceptance.
        errors.append("GITHUB_CANNOT_LOCK_OSI_VERIFIED_FINISH")
    if suzgec.get("judgment") == "PASS" and not suzgec.get("evidence"):
        errors.append("UNSUPPORTED_PASS")
    for name in ("testEvidence", "negativeEvidence"):
        if not isinstance(data.get(name), list):
            errors.append(name.upper() + "_INVALID")
    for name in ("humanAuthorityScope", "progressProjectBinding", "fieldReceipt"):
        if not isinstance(data.get(name), dict):
            errors.append(name.upper() + "_MISSING")
    if mode in {"handoff", "project"}:
        field = data.get("fieldReceipt")
        if not isinstance(field, dict) or field.get("osiFieldState") != "UNVERIFIED":
            errors.append("GITHUB_FIELD_ATTESTATION_FORBIDDEN")
        if data.get("verifiedFinish") != "HOLD":
            errors.append("GITHUB_FINISH_AUTHORITY_HOLD")
    return errors


DIMENSIONS = ("scope", "feasibility", "resilience", "authoritySafety", "provability")
SCENARIOS = ("normal", "interruption", "replay", "collision", "wrongSource",
             "missingAuthority", "sourceDrift", "disk", "tool", "partial", "rollback")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE,
                                   timeout=30)


def source_snapshot(root):
    """Read actual tracked bytes and Git facts. Never install, fetch or checkout."""
    root = Path(root).resolve()
    names = git(root, "ls-files", "-z").decode().split("\0")[:-1]
    files = {}
    for name in names:
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError("SOURCE_SPECIAL_FILE_HOLD")
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"commit": git(root, "rev-parse", "HEAD").decode().strip(),
            "origin": git(root, "remote", "get-url", "origin").decode().strip(),
            "shallow": git(root, "rev-parse", "--is-shallow-repository").strip() != b"false",
            "dirty": bool(git(root, "status", "--porcelain", "--untracked-files=all")),
            "refsDigest": hashlib.sha256(git(root, "for-each-ref",
                "--format=%(refname) %(objectname)")).hexdigest(),
            "files": files, "artifactDigest": digest(files)}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def texts(value):
    return isinstance(value, list) and bool(value) and all(text(x) for x in value)


def project_checks(data, snapshot):
    """Twenty preparation checks, four per /20 dimension; no product counter."""
    p = data.get("projectPlan", {})
    p = p if isinstance(p, dict) else {}
    rows = []
    def check(dimension, name, ok, evidence):
        rows.append({"dimension": dimension, "check": name, "state": "PASS" if ok else "HOLD",
                     "points": 5 if ok else 0, "evidence": evidence})
    check("scope", "goal", p.get("version") == "1" and text(p.get("goal")) and text(p.get("owner")), "projectPlan version 1; goal/owner")
    matrix = p.get("acceptance")
    fields = ("CONTROL_ID", "REQUIREMENT", "PASS_CONDITION", "REQUIRED_EVIDENCE", "VERIFIER", "AUTHORITY", "STATE")
    matrix_ok = isinstance(matrix, list) and bool(matrix) and all(
        isinstance(c, dict) and all(text(c.get(k)) for k in fields)
        and c["STATE"] in {"PASS", "HOLD", "NOT_REQUIRED"} for c in matrix)
    matrix_ok = matrix_ok and len({c["CONTROL_ID"] for c in matrix}) == len(matrix)
    check("scope", "acceptance", matrix_ok, "V3 original CONTROL_ID matrix; unique IDs")
    inv = p.get("inventory", {})
    inv = inv if isinstance(inv, dict) else {}
    check("scope", "inventory", all(text(inv.get(k)) for k in
          ("history", "files", "branches", "githubRecords", "secrets")), "explicit inventory coverage, Git != GitHub records")
    target = p.get("target", {})
    target = target if isinstance(target, dict) else {}
    check("scope", "target", text(target.get("platform")) and text(target.get("path"))
          and Path(target["path"]).is_absolute() and target.get("collisionPolicy") == "HOLD_PRESERVE_EXISTING"
          and texts(target.get("preserve")), "proposed target; preserve foreign/dirty files")
    deps = p.get("dependencies")
    dep_ok = isinstance(deps, list) and all(isinstance(d, dict) and text(d.get("id"))
             and isinstance(d.get("requires"), list) and all(text(x) for x in d["requires"]) for d in deps)
    if dep_ok:
        graph = {d["id"]: set(d["requires"]) for d in deps}
        dep_ok = len(graph) == len(deps) and all(v <= graph.keys() for v in graph.values())
        remaining = dict(graph)
        while dep_ok and remaining:
            ready = {k for k, v in remaining.items() if not v & remaining.keys()}
            if not ready:
                dep_ok = False
                break
            remaining = {k: v for k, v in remaining.items() if k not in ready}
    check("feasibility", "dependencies", dep_ok, "dependency DAG, no missing/cyclic dependency")
    check("feasibility", "tools", texts(p.get("tools")), "required versions/probes; target probes remain field HOLD")
    budget = p.get("budget", {})
    check("feasibility", "budget", isinstance(budget, dict) and all(
          type(budget.get(k)) is int and budget[k] == 0 for k in ("purchasedCredits", "paidApi", "purchases"))
          and text(budget.get("actionsBilling")), "zero purchase limits; Actions evidence separate")
    check("feasibility", "steps", texts(p.get("steps")), "ordered handoff steps; preparation executes none")
    cases = p.get("scenarios", {})
    cases = cases if isinstance(cases, dict) else {}
    attempts = p.get("attempts", [])
    attempt_keys = ("hypothesis", "intervention", "evidenceDigest")
    attempts_ok = isinstance(attempts, list) and all(isinstance(a, dict) and
        all(text(a.get(k)) for k in attempt_keys) and HEX64.fullmatch(a["evidenceDigest"]) for a in attempts)
    stalled = attempts_ok and len(attempts) >= 2 and all(
        attempts[-1][k] == attempts[-2][k] for k in attempt_keys)
    for name, group in (("recovery", ("interruption", "replay")), ("conflicts", ("collision", "wrongSource", "sourceDrift")),
                        ("resources", ("disk", "tool", "partial")), ("rollback", ("normal", "missingAuthority", "rollback"))):
        ok = all(text(cases.get(k)) for k in group)
        if name == "recovery":
            ok = ok and attempts_ok and not stalled
        check("resilience", name, ok, "scenario response: " + ",".join(group) +
              ("; GÜVENLİ_DUR_REDIAGNOSE" if stalled and name == "recovery" else ""))
    check("authoritySafety", "scope", text(p.get("humanDecisionScope")), "exact project/path/operation scope for human decision")
    check("authoritySafety", "delegation", data.get("verifiedFinish") == "HOLD" and
          data.get("fieldReceipt", {}).get("osiFieldState") == "UNVERIFIED", "OSi and canonical DoneCheck own acceptance")
    check("authoritySafety", "risks", texts(p.get("risks")), "known risks and protected values")
    check("authoritySafety", "rollbackPlan", isinstance(p.get("rollback"), dict) and all(
          text(p["rollback"].get(k)) for k in ("scope", "steps", "verification")), "owned staging only; authenticated recovery verification")
    check("provability", "source", bool(snapshot) and snapshot["commit"] == data.get("sourceCommit")
          and snapshot["origin"] in {f"https://github.com/{data.get('canonicalRepo')}.git",
                                     f"https://github.com/{data.get('canonicalRepo')}"}, "observed Git HEAD and origin")
    check("provability", "bytes", bool(snapshot) and bool(snapshot["files"])
          and snapshot["artifactDigest"] == data.get("artifactDigest"), "SHA-256 manifest of actual tracked bytes")
    check("provability", "history", bool(snapshot) and not snapshot["shallow"] and not snapshot["dirty"],
          "full source ancestry; clean observed source worktree")
    check("provability", "refs", bool(snapshot) and snapshot["refsDigest"] == p.get("refsDigest"), "observed local refs SHA-256; remote refs reconciled at execution")
    return rows


def read_theoretical_main_balance():
    """Reuse the existing ENGURU Ana Terazi evaluator; missing proof is HOLD."""
    runner = Path(__file__).resolve().parents[1] / "enguru_ana_terazi_v1.py"
    try:
        run = subprocess.run([sys.executable, "-B", str(runner)],
                             capture_output=True, text=True, timeout=60, check=False)
        receipt = json.loads(run.stdout)
        raw = receipt.get("scores", {})
        scores = {axis: raw.get(axis, 0) if type(raw.get(axis)) in (int, float) else 0
                  for axis in FIVE_AXES}
        valid = (run.returncode == 0
                 and receipt.get("verdict") == "PASS_THEORETICAL_PREPARATION_5X100"
                 and set(raw) == set(FIVE_AXES)
                 and all(scores[axis] == 100 for axis in FIVE_AXES))
        return {"state": "PASS" if valid else "HOLD",
                "verdict": receipt.get("verdict", "HOLD"),
                "scores": scores,
                "source": "tools/enguru_ana_terazi_v1.py",
                "scope": "GENERAL_SYNTHETIC_METHOD_ORACLES"}
    except (OSError, ValueError, TypeError, subprocess.SubprocessError, RecursionError):
        return {"state": "HOLD", "verdict": "HOLD_UNAVAILABLE_ANA_TERAZI",
                "scores": {axis: 0 for axis in FIVE_AXES},
                "source": "tools/enguru_ana_terazi_v1.py",
                "scope": "GENERAL_SYNTHETIC_METHOD_ORACLES"}


def assess_project(data, root):
    errors = validate(data, mode="project")
    snapshot = None
    if not errors:
        try:
            snapshot = source_snapshot(root)
        except (OSError, ValueError, subprocess.SubprocessError, UnicodeError):
            errors.append("SOURCE_UNREADABLE")
    rows = project_checks(data, snapshot) if isinstance(data, dict) and not errors else []
    scores = {d: sum(r["points"] for r in rows if r["dimension"] == d) for d in DIMENSIONS}
    prepared = not errors and len(rows) == 20 and all(r["state"] == "PASS" for r in rows)
    return {"state": "PASS_PROJECT_STRUCTURE_ONLY" if prepared else "HOLD_PROJECT_STRUCTURE",
            "structureReady": "PASS" if prepared else "HOLD",
            "planDigest": digest(data), "acceptanceDigest": digest(data.get("projectPlan", {}).get("acceptance"))
                if isinstance(data, dict) and isinstance(data.get("projectPlan"), dict) else None,
            "gates": {"PREPARED": "HOLD", "FIELD_READY": "HOLD",
                      "HUMAN_AUTHORIZED": "HOLD", "VERIFIED_FINISH": "HOLD"},
            "scores": scores, "preparationChecklistScore": sum(scores.values()), "checks": rows,
            "rubricScope": "STRUCTURAL_PREPARATION_ONLY_SEMANTIC_REVIEW_SEPARATE",
            "errors": errors, "source": snapshot,
            "authorityVerification": "DELEGATED_TO_CANONICAL_DONECHECK_AND_HUMAN_THRESHOLD",
            "nextAction": "VERIFY_FIVE_INDEPENDENT_100_GATES" if prepared else "REPAIR_PREPARATION_GAPS"}


def independent_source_check(data, root):
    """T3 uses committed Git archive, independently of working-file hashing."""
    content = git(root, "archive", "--format=tar", "HEAD")
    files = {}
    with tarfile.open(fileobj=io.BytesIO(content)) as archive:
        for item in archive:
            if item.isfile():
                files[item.name] = hashlib.sha256(archive.extractfile(item).read()).hexdigest()
            elif not item.isdir():
                return False
    return digest(files) == data.get("artifactDigest")


def simulate_project(data, root):
    """Read-only bounded preparation simulations; never an OSi transfer."""
    baseline = assess_project(data, root)
    if baseline["structureReady"] != "PASS":
        return {"state": "HOLD", "gates": baseline["gates"], "baseline": baseline,
                "scores": {axis: 0 for axis in FIVE_AXES}, "cases": [],
                "nextAction": "REPAIR_PREPARATION_GAPS"}
    mutations = {
        "interruption": lambda x: x["projectPlan"]["scenarios"].pop("interruption"),
        "replay": lambda x: x["projectPlan"]["acceptance"].append(copy.deepcopy(x["projectPlan"]["acceptance"][0])),
        "collision": lambda x: x["projectPlan"]["target"].update(collisionPolicy="OVERWRITE"),
        "wrongSource": lambda x: x.update(canonicalRepo="foreign/repo"),
        "missingAuthority": lambda x: x["projectPlan"].update(humanDecisionScope=""),
        "sourceDrift": lambda x: x.update(sourceCommit="0" * 40),
        "disk": lambda x: x["projectPlan"]["scenarios"].pop("disk"),
        "tool": lambda x: x["projectPlan"].update(tools=[]),
        "partial": lambda x: x.update(artifactDigest="0" * 64),
        "rollback": lambda x: x["projectPlan"].update(rollback={}),
    }
    cases = [{"scenario": "normal", "expected": "PASS", "observed": "PASS"}]
    for name, mutate in mutations.items():
        candidate = copy.deepcopy(data)
        mutate(candidate)
        result = assess_project(candidate, root)
        cases.append({"scenario": name, "expected": "HOLD", "observed": result["structureReady"]})
    independent = independent_source_check(data, root)
    after = assess_project(data, root)
    source_unchanged = source_snapshot(root) == baseline["source"]
    authority_held = all(after["gates"][k] == "HOLD" for k in
                         ("FIELD_READY", "HUMAN_AUTHORIZED", "VERIFIED_FINISH"))
    negative_caught = sum(c["observed"] == c["expected"] for c in cases[1:])
    local_scores = {
        "THEORY": 100 if (baseline["structureReady"] == "PASS"
                          and baseline["source"] is not None) else 0,
        "DESIGN": baseline["preparationChecklistScore"],
        "SIM1": 5 * sum(r["state"] == "PASS" for r in baseline["checks"]),
        "SIM2": 10 * negative_caught,
        "SIM3": 25 * sum((independent, after == baseline, source_unchanged, authority_held)),
    }
    general = read_theoretical_main_balance()
    scores = {axis: min(local_scores[axis], general["scores"][axis]) for axis in FIVE_AXES}
    ready = (general["state"] == "PASS"
             and all(scores[axis] == 100 for axis in FIVE_AXES))
    open_axes = [axis for axis in FIVE_AXES if scores[axis] < 100]
    return {
        "state": "PASS_GITHUB_PREPARATION_5X100" if ready else "HOLD",
        "baseline": baseline, "theoreticalMainBalance": general,
        "localProjectScores": local_scores, "scores": scores,
        "fixedDenominators": "THEORY canonical+source; DESIGN 20x5; SIM1 20x5; SIM2 10x10; SIM3 4x25",
        "gates": dict(baseline["gates"], PREPARED="PASS" if ready else "HOLD"),
        "cases": cases, "independentCommittedBytes": "PASS" if independent else "HOLD",
        "readOnlyReplay": after == baseline, "sourceUnchanged": source_unchanged,
        "fieldExecution": "NOT_EXECUTED",
        "nextAction": "STOP_FOR_OSI_READ_ONLY_PREFLIGHT_AND_HUMAN_DECISION" if ready
                      else "REPAIR_FIVE_AXIS_PREPARATION:" + ",".join(open_axes),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--mode", choices=("template", "handoff", "project"), default="template")
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    try:
        def unique(pairs):
            obj = {}
            for key, value in pairs:
                if key in obj:
                    raise ValueError("DUPLICATE_JSON_KEY")
                obj[key] = value
            return obj
        data = json.loads(args.path.read_text(encoding="utf-8"), object_pairs_hook=unique)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print("STATE=HOLD\nREASON=UNREADABLE_JSON:" + type(exc).__name__)
        return 2
    if args.mode == "project":
        if args.source_root is None:
            print("STATE=HOLD\nREASON=SOURCE_ROOT_REQUIRED")
            return 2
        try:
            result = simulate_project(data, args.source_root)
        except (OSError, ValueError, TypeError, KeyError, RecursionError, subprocess.SubprocessError):
            print("STATE=HOLD\nREASON=PROJECT_INPUT_OR_SOURCE_INVALID")
            return 2
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        return 0 if result["state"] == "PASS_GITHUB_PREPARATION_5X100" else 2
    errors = validate(data, mode=args.mode)
    if errors:
        print("STATE=HOLD\nREASON=" + ",".join(errors))
        return 1
    print("STATE=PASS_HANDOFF_SHAPE\nPREPARED=NOT_ASSESSED\nFIELD_STATE=UNVERIFIED\nverifiedFinish=HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
