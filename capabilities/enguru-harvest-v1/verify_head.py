"""Read-only Git HEAD/working byte equality and canonical V3 pin verification."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE="capabilities/enguru-harvest-v1/"
SOURCES=(
    "goal.json","source_candidates.json","harvest.py","evidence_gate.py",
    "skill_kernel.py","test_harvest.py","test_evidence_gate.py","test_skill_kernel.py",
    "run_three_simulations.py","OSI_HANDOFF_PREPARATION.md","ACCEPTANCE_MATRIX.md","TECHNICAL_TRIAL_LEDGER_V1.md","README.md",
    "root_license_observations.json","license_gate.py","test_license_gate.py",
    "external_skill_proof_plan.json","test_external_skill_plan.py",
    "upstream_execution_coverage.json","test_upstream_execution_coverage.py",
    "WORK_PACKAGES_ZULFIKAR_V13.json","run_k01_real_benchmark.py","test_k01_benchmark.py",
    "run_k03_cli_smoke.py","test_k03_cli_contract.py",
    "k02_source_policy.py","test_k02_source_policy.py","K01_K05_BUTUNLESIK_FINIS_RAPORU.md",
    "test_upstream_hypothesis.py","run_real_upstream_trials.py",
    "run_second_upstream_trials.py","run_lm_eval_fixture.py","promptfooconfig.json","check_promptfoo_receipt.py","mcp_typescript_trial.mjs","mcp_reference_stdio_trial.mjs","run_anthropic_skills_trial.py",
)
V3="governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
V3_SHA="11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc"
ADAPTERS=(".agents/skills/enguru-evidence-harvest/SKILL.md",".claude/skills/enguru-evidence-harvest/SKILL.md")

def git(*args):
    return subprocess.run(["git","-C",str(ROOT),*args],check=True,capture_output=True).stdout

def check():
    commit=git("rev-parse","HEAD").decode().strip()
    paths=[BASE+name for name in SOURCES]+[V3,*ADAPTERS]
    files={}
    for path in paths:
        work=(ROOT/path).read_bytes()
        pinned=git("show","HEAD:"+path)
        if work!=pinned:
            raise RuntimeError("HEAD_WORKTREE_MISMATCH: "+path)
        files[path]=hashlib.sha256(work).hexdigest()
    if files[V3]!=V3_SHA:
        raise RuntimeError("CANONICAL_V3_SHA_MISMATCH")
    return {
        "schema":"enguru.harvest.github-byte-receipt/v1",
        "commit":commit,
        "source_sha256":files,
        "bytes_equal_git_head":True,
        "canonical_v3_pin_pass":True,
        "github_engineering":"CI_CANDIDATE",
        "external_skill_proven":"HOLD",
        "independent_reviewer":"HOLD",
        "osi_field":"HOLD",
        "osi_execution_count":0,
        "verified_finish":"HOLD",
    }

if __name__=="__main__":
    print(json.dumps(check(),ensure_ascii=False,sort_keys=True,indent=2))
