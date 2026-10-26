"""P04: inspect actual pinned upstream Anthropic SKILL.md with official skills-ref.

This is compatibility inspection, not permission to reuse or redistribute.
The upstream per-skill LICENSE.txt is kept external and only SHA-256 is emitted.
"""
import hashlib
import json
import os
from pathlib import Path
from skills_ref import validate

def main():
    root=Path(os.environ["ENGURU_ANTHROPIC_SKILLS_CHECKOUT"]).resolve()
    observations=[]
    for skill in ("pdf","docx"):
        folder=root/"skills"/skill
        source=folder/"SKILL.md"
        licensefile=folder/"LICENSE.txt"
        if not source.is_file() or not licensefile.is_file():
            raise RuntimeError("PINNED_UPSTREAM_SKILL_OR_LICENSE_MISSING: "+skill)
        problems=validate(folder)
        license_bytes=licensefile.read_bytes()
        terms=license_bytes.decode("utf-8")
        if "Anthropic" not in terms or "Terms of Service" not in terms:
            raise RuntimeError("UNEXPECTED_PER_SKILL_LICENSE: "+skill)
        observations.append({
            "skill":skill,
            "reference_errors":problems,
            "validator_accepts":not bool(problems),
            "skill_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "license_sha256":hashlib.sha256(license_bytes).hexdigest(),
            "license_category":"ANTHROPIC_TERMS_RESTRICTED",
            "redistribution_authority":"HOLD"
        })
    output={
        "schema":"enguru.harvest.p04-upstream-structural-inspection/v1",
        "upstream_repository":"anthropics/skills",
        "source_commit":"dbd4588f9e1033efb41dad4bef2f7947c8993d44",
        "observations":observations,
        "skill_reference_format_valid":all(x["validator_accepts"] for x in observations),
        "legal_reuse_approved":False,
        "actual_skill_executed":False,
        "osi_execution":0,
        "official_proven":"HOLD",
    }
    output["state"]="PASS_UPSTREAM_SKILL_STRUCTURAL_ONLY" if output["skill_reference_format_valid"] else "HOLD_UPSTREAM_FORMAT"
    Path("anthropic-skills-structural-receipt.json").write_text(
        json.dumps(output,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,sort_keys=True))
    if not output["skill_reference_format_valid"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
