"""Bounded composition of existing v2.4 language pre-send and source preflight.

Candidate-only: does not grant OSI runtime, approval, or Verified Finish.
"""
import argparse
import json
from pathlib import Path
from tools.enguru_suzgec_v24_source_preflight import assess
from tools.enguru_suzgec_v24_language_presend import inspect

def evaluate(root, manifest, draft, surface="OSi"):
    result={"state":"HOLD_GUVENLI_DUR","verifiedFinish":"HOLD","stage":"PRESEND_COMPOSITION_CANDIDATE"}
    source=assess(root, manifest)
    result["source"]=source
    if source.get("state")!="PASS_SOURCE_PREFLIGHT_ONLY":
        result["reason"]="SOURCE_PREFLIGHT_HOLD"
        return result
    try:
        p=Path(draft)
        if p.is_symlink() or not p.is_file():
            raise ValueError("DRAFT_SOURCE_INVALID")
        text=p.read_text(encoding="utf-8")
        language=inspect(text,Path(root),surface)
    except (OSError,ValueError,UnicodeError) as e:
        result["reason"]="DRAFT_READ_HOLD"
        return result
    result["language"]=language
    if language.get("state")!="PASS_SCOPED_DRAFT_LANGUAGE_GATE":
        result["reason"]="LANGUAGE_PRESEND_HOLD"
        return result
    result["state"]="PASS_BOUNDED_PREPARATION_ONLY"
    result["reason"]="NATIVE_OSI_EVIDENCE_AND_AUTHORITY_STILL_REQUIRED"
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--draft",required=True)
    ap.add_argument("--surface",default="OSi")
    a=ap.parse_args()
    print(json.dumps(r:=evaluate(a.root,a.manifest,a.draft,a.surface),ensure_ascii=False,sort_keys=True))
    return 0 if r["state"]=="PASS_BOUNDED_PREPARATION_ONLY" else 50

if __name__=="__main__":
    raise SystemExit(main())
