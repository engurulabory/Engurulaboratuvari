#!/usr/bin/env python3
"""Seven typed, read-only native task-specific P06 candidate objectives."""
from __future__ import annotations
import hashlib,json
from pathlib import Path

POLICY={
 'ZEKU': ('INSPECT_CANONICAL_STATE', 'CANONICAL_TRUTH_READ', ('heads','contractSha256')),
 'ATLAS': ('REVIEW_AUTHORITY_ARCHITECTURE', 'ARCHITECTURE_AST_REVIEW', ('sourceSha256','functions')),
 'FORGE': ('INSPECT_EXECUTOR_IMPLEMENTATION', 'ENGINEERING_EXECUTOR_INSPECTION', ('sourceSha256','classes')),
 'ASTRA': ('AUDIT_OFFLINE_CAPABILITY_PROVENANCE', 'OFFLINE_CAPABILITY_PROVENANCE', ('registrySha256','externalNetworkUsed')),
 'NEURON': ('AUDIT_DECISION_ENGINE', 'DECISION_ENGINE_CODE_AUDIT', ('sourceSha256','functions')),
 'SENTINEL': ('INSPECT_RECOVERY_IMPLEMENTATION', 'RECOVERY_SOURCE_AUDIT', ('sourceSha256','classes')),
 'FORMA': ('REVIEW_PRODUCT_PILOT_CONTRACT', 'PRODUCT_CONTRACT_REVIEW', ('sourceSha256','profileCount')),
}
def objective(pilot):
    if pilot not in POLICY: raise ValueError('UNQUALIFIED_PILOT')
    return 'P06_TASK_SPECIFIC_'+pilot+'_'+POLICY[pilot][0]

def qualify_native_result(pilot, result, profile):
    if pilot not in POLICY or profile.get('PILOT_ID')!=pilot:
        raise ValueError('TASK_PROFILE_BINDING')
    if not isinstance(result,dict):raise ValueError('TASK_NATIVE_RESULT_INVALID')
    _,operation,required=POLICY[pilot]
    if result.get('operation')!=operation:
        raise ValueError('TASK_NATIVE_OPERATION_MISMATCH')
    for key in required:
        if key not in result:raise ValueError('TASK_NATIVE_EVIDENCE_GAP:'+key)
    if pilot=='ZEKU':
        h=result.get('heads')
        if not isinstance(h,dict) or not all(isinstance(h.get(x),str) and len(h[x])==40 for x in ('control','product')):
            raise ValueError('TASK_NATIVE_HEAD_MISSING')
    if pilot in ('ATLAS','FORGE','NEURON','SENTINEL'):
        key='classes' if pilot in ('FORGE','SENTINEL') else 'functions'
        if not isinstance(result.get(key),list):raise ValueError('TASK_NATIVE_CODE_STRUCTURE')
    if pilot=='ASTRA' and result.get('externalNetworkUsed') is not False:
        raise ValueError('TASK_NATIVE_NETWORK_AUTHORITY')
    if pilot=='FORMA' and result.get('profileCount')!=7:
        raise ValueError('TASK_NATIVE_PROFILE_SET')
    return True
