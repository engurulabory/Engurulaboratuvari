from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "tools/mac_engineer_capability_registry_guard.py"
REGISTRY = ROOT / "governance/mac-engineer/CAPABILITY_REGISTRY_V1.json"
SCHEMA = ROOT / "governance/mac-engineer/CAPABILITY_REGISTRY_V1.schema.json"
INVENTORY = ROOT / "governance/mac-engineer/CURRENT_PROVEN_CAPABILITY_INVENTORY_V1.md"


def run_guard(registry: Path = REGISTRY) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GUARD),
            "--registry",
            str(registry),
            "--schema",
            str(SCHEMA),
            "--inventory",
            str(INVENTORY),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_variant(tmp_path: Path, mutate) -> Path:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def test_canonical_registry_guard_passes():
    p = run_guard()
    assert p.returncode == 0, p.stdout + p.stderr
    assert "STATE=PASS" in p.stdout
    assert "INVENTORY_PARITY=19_OF_19" in p.stdout
    assert "SCHEMA_CONTRACT_VALIDATION=PASS" in p.stdout
    assert "PACKAGE03_GRAPH_PREAUTHORIZATION=0" in p.stdout


def test_duplicate_capability_id_fails_closed(tmp_path):
    path = write_variant(
        tmp_path,
        lambda d: d["capabilities"].__setitem__(
            1, {**d["capabilities"][1], "CAPABILITY_ID": d["capabilities"][0]["CAPABILITY_ID"]}
        ),
    )
    p = run_guard(path)
    assert p.returncode != 0
    assert "DUPLICATE_CAPABILITY_ID" in p.stdout


def test_false_fail_closed_is_rejected(tmp_path):
    path = write_variant(
        tmp_path,
        lambda d: d["capabilities"][0].__setitem__("FAIL_CLOSED", False),
    )
    p = run_guard(path)
    assert p.returncode != 0
    assert "FAIL_CLOSED_FALSE" in p.stdout


def test_package03_transition_preauthorization_is_rejected(tmp_path):
    path = write_variant(
        tmp_path,
        lambda d: d["capabilities"][0].__setitem__(
            "NEXT_COMPATIBLE_CAPABILITIES", ["BUILD"]
        ),
    )
    p = run_guard(path)
    assert p.returncode != 0
    assert "PACKAGE03_GRAPH_PREAUTHORIZED" in p.stdout


def test_unknown_authority_is_rejected(tmp_path):
    path = write_variant(
        tmp_path,
        lambda d: d["capabilities"][0].__setitem__("AUTHORITY", "UNBOUNDED"),
    )
    p = run_guard(path)
    assert p.returncode != 0
    assert "UNKNOWN_AUTHORITY" in p.stdout
