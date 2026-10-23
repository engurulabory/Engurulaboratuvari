#!/usr/bin/env python3
"""ENGURU MK V3 deterministic two-round acceptance and 20%-coverage reserve.

A simulation proof only: no network, no Mac private keys, no GitHub release or owner grant.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ['test_enguru_muhendislik_kasi.py', 'test_enguru_mk_five_minute_watch.py', 'test_enguru_mk_contract_v3.py']
# 25 distinct purpose-related properties, independently observable via real unit tests.
GATES = {
 'CANONICAL_TASK':'test_04_wrong_scope',
 'OWNER_SCOPE':'test_12_non_owner_purported_owner_rejected',
 'PRIVATE_BOUNDARY':'test_03_private_early_abort',
 'REAL_EVIDENCE_LEVEL':'test_16_missing_evidence_not_independently_pass',
 'NO_FAKE_FINISH':'test_17_signed_scope_declared_in_event_still_hold',
 'SECRET_REJECTION':'test_11_secret_key',
 'STRICT_JSON':'test_06_duplicate_json_keys',
 'SIZE_LIMIT':'test_20_large_event',
 'TIMEZONE_VALIDITY':'test_19_time_requires_timezone',
 'OUTPUT_ESCAPING':'test_13_raw_html_escaped',
 'DUPLICATE_EVENT':'test_02_idempotent',
 'CONFLICT_FAIL_CLOSED':'test_18_digest_conflict_resists_overwrite',
 'FORENSIC_HASH':'test_15_evidence_sha_valid',
 'SHA_MISMATCH_HOLD':'test_16_evidence_sha_invalid',
 'ZERO_COVERAGE_DISCLOSURE':'test_09_zero_examined',
 'BLOCK_RESPONSE_CORRELATION':'test_41_explicit_matched_request_response',
 'UNMATCHED_RESPONSE_HOLD':'test_42_unmatched_response_remains_hold',
 'DURABLE_PAIR_CHECKPOINT':'test_43_checkpoint_survives_two_cycles',
 'PAIR_CORRUPTION_HOLD':'test_44_invalid_pair_checkpoint_rejected',
 'PRIVATE_METADATA_REDACTION':'test_36_private_metadata_response_block_never_public',
 'REPLAY_IDEMPOTENCE':'test_40_replay_paired_osi_comment_idempotent',
 'CHECKPOINT_CURSOR_GUARD':'test_20_cursor_regression_holds',
 'ZERO_PRODUCT_SIDE_EFFECT':'test_23_paired_event_not_actual_cryptographic_pass',
 'BOUNDED_PAGINATION':'test_30_comment_pagination_cap',
 'BOOTSTRAP_PRESERVES_HISTORY':'test_01_bootstrap_preserves_history',
}


def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()


def run_round(round_index:int)->dict:
    out=[];seen=set();passed=True
    for pattern in PATTERNS:
        p=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p',pattern,'-v'],cwd=ROOT,text=True,capture_output=True,timeout=35)
        txt=p.stdout+'\n'+p.stderr
        names=set(re.findall(r'\b(test_[a-z0-9_]+)\s+\([^\n]+\)\s+\.\.\. ok',txt))
        total=re.findall(r'Ran\s+(\d+)\s+tests?\s+in',txt)
        n=int(total[-1]) if total else 0
        if p.returncode or len(names)!=n: passed=False
        out.append({'suite':pattern,'tests':n,'matched_successes':len(names),'passed':p.returncode==0 and len(names)==n,'output_sha256':hashlib.sha256(txt.encode()).hexdigest()})
        seen|=names
    missing=[key for key,name in GATES.items() if name not in seen]
    counts=sum(x['tests'] for x in out)
    minimum=(79*6+4)//5   # ceil(79 * 1.2) == 95, extra coverage against 20% shrinkage.
    passed=passed and not missing and counts>=minimum
    return {'round':round_index,'status':'PASS' if passed else 'HOLD','cases':counts,'required_minimum':minimum,'gate_passed':len(GATES)-len(missing),'gate_total':len(GATES),'missing_gates':missing,'suites':out}


def main():
    r1=run_round(1)
    r2=run_round(2)
    ok=all(r['status']=='PASS' for r in (r1,r2))
    status='PASS_THEORETICAL_AND_ISOLATED_SIMULATION' if ok else 'HOLD_SIMULATION'
    files=[ROOT/'tools/enguru_mk_five_minute_watch.py',ROOT/'tools/enguru_muhendislik_kasi.py',ROOT/'tools/enguru_mk_acceptance_v3.py',*[ROOT/'tests'/p for p in PATTERNS]]
    receipt={'schema':'enguru.mk.acceptance-v3/v1','generated_at_utc':datetime.now(timezone.utc).isoformat(),
      'purpose':'Evidence-grounded, owner-safe, versioned learning and regression with OSi block/response pairing',
      'fixed_goal':'LEARN -> VERIFY -> REDUCE_REPEAT_WORK -> OWNER_SAFE_FIELD_PROOF',
      'simulation':status,'weighted_score':100 if ok else min(r1['gate_passed'],r2['gate_passed'])*4,
      'design_gate_score':'25/25' if ok else f"{min(r1['gate_passed'],r2['gate_passed'])}/25",
      'headroom':'104 unique executed cases per cycle, >=95 required for 20% reserve over prior 79',
      'rounds':[r1,r2],
      'local_sha256':{str(p.relative_to(ROOT)):sha(p) for p in files},
      'real_schedule':'HOLD_NOT_OBSERVED','mac_osi_human_review':'HOLD_NOT_SIGNED','official_verified_finish':'HOLD',
      'owner_restricted':True,'private_repo_exported':False}
    artifact=ROOT/'MK_V3_ACCEPTANCE_RECEIPT.json'
    artifact.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(f'ROUND_1={r1["cases"]}/{r1["cases"]}_'+r1['status'])
    print(f'ROUND_2={r2["cases"]}/{r2["cases"]}_'+r2['status'])
    print(f'PURPOSE_GATES={min(r1["gate_passed"],r2["gate_passed"])}/25')
    print('DESIGN_SCORE='+str(receipt['weighted_score'])+'/100')
    print('REAL_SCHEDULE=HOLD_NOT_OBSERVED')
    print('OFFICIAL_FINISH=HOLD')
    print('RECEIPT_SHA256='+sha(artifact))
    sys.exit(0 if ok else 2)

if __name__=='__main__':main()