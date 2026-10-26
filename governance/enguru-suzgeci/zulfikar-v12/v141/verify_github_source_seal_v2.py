"""Fail-closed exact-checkout Zülfikar 1.4.1 seal verification (technical only)."""
from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SEAL_PATH = HERE / "GITHUB_SOURCE_SHA_SEAL_V2.json"
PREFIX = "governance/enguru-suzgeci/zulfikar-v12/v141/"
SCHEMA = "enguru.zulfikar.v141.github-source-sha-seal/v2"


def verify(seal: dict, source_reader, tracked_paths: set[str]) -> dict:
    if not isinstance(seal, dict) or seal.get("schema") != SCHEMA:
        raise ValueError("SEAL_SCHEMA_HOLD")
    if seal.get("repository") != "engurulabory/Engurulaboratuvari":
        raise ValueError("SEAL_REPOSITORY_HOLD")
    if (seal.get("ownerDoneCheck") != "NOT_ISSUED" or
        seal.get("productVerifiedFinish") != "HOLD" or
        seal.get("macOsi") != "HOLD_NOT_OBSERVED"):
        raise ValueError("SEAL_AUTHORITY_HOLD")
    if [seal.get("expectedRealTestsPerRound"),seal.get("expectedRounds"),
        seal.get("expectedExecutedTests"),seal.get("architectureControls")] != [126,3,378,10]:
        raise ValueError("SEAL_TEST_SCOPE_HOLD")
    rows = seal.get("stageFiles")
    if not isinstance(rows, list) or len(rows) != seal.get("expectedSourceFiles") or len(rows) < 17:
        raise ValueError("SEAL_COVERAGE_COUNT_HOLD")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("SEAL_ROW_HOLD")
        path, expected = row.get("path"), row.get("sha256")
        if (not isinstance(path,str) or path in seen or path.startswith("/") or
            ".." in Path(path).parts or (not path.startswith(PREFIX) and not
            path.startswith(".github/workflows/enguru-zulfikar-v141-"))):
            raise ValueError("SEAL_PATH_HOLD")
        if not isinstance(expected,str) or len(expected)!=64 or any(c not in "0123456789abcdef" for c in expected):
            raise ValueError("SEAL_SHA_FORMAT_HOLD")
        if path not in tracked_paths:
            raise ValueError(f"SEAL_UNTRACKED_SOURCE_HOLD:{path}")
        raw = source_reader(path)
        if not isinstance(raw, bytes) or hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"SEAL_SOURCE_DRIFT_HOLD:{path}")
        seen.add(path)
    for required in ["preflight.py", "dom/engine.py", "dom/proof_chain.py", "dom/completion_guard.py",
                     "dom/test_engine.py", "dom/test_proof_chain.py", "dom/test_completion_guard.py",
                     "dom/test_final_hardening.py", "verify_github_source_seal_v2.py"]:
        if PREFIX + required not in seen:
            raise ValueError(f"SEAL_REQUIRED_SOURCE_MISSING:{required}")
    required_workflows={".github/workflows/enguru-zulfikar-v141-dom-preflight.yml",
                        ".github/workflows/enguru-zulfikar-v141-source-seal-v2.yml"}
    if not required_workflows <= seen:
        raise ValueError("SEAL_WORKFLOW_GAP_HOLD")
    # Detect newly added operational Python and workflow files, even if a previous seal still verifies.
    operational={p for p in tracked_paths if (p.startswith(PREFIX) and p.endswith(".py")) or
                 p.startswith(".github/workflows/enguru-zulfikar-v141-")}
    if not operational <= seen:
        raise ValueError("SEAL_NEW_UNCOVERED_OPERATIONAL_SOURCE_HOLD:"+",".join(sorted(operational-seen)))
    return {"state":"PASS_EXACT_CHECKOUT_SHA_SEAL_V2", "files":len(seen),
            "tests_expected":378,"officialVerifiedFinish":"HOLD"}


def _git(*args:str) -> bytes:
    return subprocess.check_output(["git","-C",str(ROOT),*args], timeout=35)


def run() -> dict:
    # HEAD is the checked-out immutable Git commit. No branch update or canonical mutation.
    tracked=set(_git("ls-tree","-r","--name-only","HEAD").decode().splitlines())
    seal=json.loads(_git("show", "HEAD:"+PREFIX+"GITHUB_SOURCE_SHA_SEAL_V2.json"))
    return verify(seal, lambda p: _git("show", "HEAD:"+p), tracked)

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
