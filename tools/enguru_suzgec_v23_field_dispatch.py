"""ENGURU Suzgec v2.3 T01: explicitly invoked read-only production caller.

No user-supplied callbacks or abilities are permitted. A successful caller observation
is not authorization to finish; no canonical mutation or Human Threshold implied.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

OPERATOR_SHA = "0ce4956641ba105ee47914de187704c07f18ed4f0ed957f0cbf0c2bc5d768741"
REGISTRY_SHA = "8ace6b42893e7929dd984f8be189d918cd04f9133a2d859361c92ca482d495ea"

ACTION = 'ENGURU_SUZGEC_V23_T01_BOUND_FIELD'
ENTRY = {
    'handler': 'ENGURU_SUZGEC_V23_LOCAL_READONLY_TEST_EXECUTOR',
    'authority': 'EXPLICIT_OSi_LOCAL_T01_READONLY',
    'product': 'ENGURU_SUZGEC_V23',
    'mutationScope': 'NONE',
    'remotePush': False,
    'humanThreshold': 'HUMAN_ONLY',
    'failClosed': True,
}
# The exact OSi v2.3 source that passed installation and local regression.
PINS = {
    'tools/enguru_suzgec_v23_execution.py': '871d94f28add0441e00edef9f3ae6e24435d7177ff089bce2af4780c7a2a021a',
    'tools/enguru_suzgec_v23_forecast.py': '5a0cd85cd71aff19f7e2c3f2de45f16c281d4a246cfdd927e80ef6421b1e4c77',
    'tools/enguru_package_execution_guard.py': '3f2c87bc521f0d577487dbca5620151575df4b3454a8fe5fc31668750096f319',
    'governance/work-protocol/ENGURU_SUZGEC_V23_UPFRONT_FINISH_VISIBILITY_CONTRACT_V1.json': '1a6efd52ad42baecd20d8030672e0267eb2348888dce5b5ad2ca77e426ea879e',
    'tests/test_enguru_suzgec_v23_forecast.py': '1ea406a15395b2c21e744095de46bda171f7f5a3d3aa862f0b471628ea66db8c',
    'tests/test_enguru_pre_execution_simulation.py': '3ade3fa5c86ca6074c3a3445069e640b26ece5bee5d5a078d4b79d3447668489',
    'tests/test_enguru_language_pre_send_linter.py': '763ecf6ab6283efa0c003dfe651138bcec3d1af0eaa19f3319710e754f8295db',
    'tools/enguru_suzgec_v23_goal_acceptance.py': '0bddf80ded98478b0b49e46805c99c6ae739366392620d3d71e5f76e023afa84',
    'tests/test_enguru_suzgec_v23_goal_acceptance.py': '93b5fdd2a1da59d62544450dfb1e738d2af76e4026e5f8dd6b7e10f976c3524c',
    'governance/work-protocol/ENGURU_SUZGEC_V23_GOAL_OUTCOME_POLICY_V1.json': 'e0396663b41cc5d87f87014d35ae1bf6018113ff31c2e8ac6e63fe0e3c6c5d8a',
}
TESTS = TESTS = TESTS = TESTS = ('test_enguru_suzgec_v23_forecast.py', 'test_enguru_pre_execution_simulation.py', 'test_enguru_language_pre_send_linter.py')

def _sha_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

def _safe_file(root: Path, rel: str) -> Path:
    # Protect sources from path traversals / symlink substitution.
    root = root.resolve(strict=True)
    p = root / rel
    if not p.is_file() or p.is_symlink() or not p.resolve(strict=True).is_relative_to(root):
        raise ValueError('MISSING_OR_SYMLINK_SOURCE:'+rel)
    return p

def verify_authority(root: Path, registry_path: Path, *, expected_head: str | None = None) -> dict:
    if _sha_bytes(_safe_file(root, 'tools/mac_engineer_operator.py').read_bytes()) != OPERATOR_SHA:
        raise ValueError('OPERATOR_SOURCE_PIN')
    if _sha_bytes(_safe_file(root, 'governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json').read_bytes()) != REGISTRY_SHA:
        raise ValueError('REGISTRY_SOURCE_PIN')
    registry = json.loads(_safe_file(root, 'governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json').read_text('utf-8'))
    if registry.get('schema') != 'enguru.mac-engineer.operator-action-registry/v1':
        raise ValueError('REGISTRY_SCHEMA')
    if (registry.get('actions') or {}).get(ACTION) != ENTRY:
        raise ValueError('REGISTRY_AUTHORITY')
    if registry_path.resolve(strict=True) != _safe_file(root, 'governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json').resolve(strict=True):
        raise ValueError('REGISTRY_PATH')
    for rel, expected in PINS.items():
        if _sha_bytes(_safe_file(root, rel).read_bytes()) != expected:
            raise ValueError('SOURCE_PIN:'+rel)
    branch = subprocess.run(['git', 'rev-parse', 'HEAD'],cwd=root,capture_output=True,text=True,check=False,timeout=15)
    if branch.returncode: raise ValueError('GIT_HEAD_UNAVAILABLE')
    head = branch.stdout.strip()
    if expected_head and head != expected_head: raise ValueError('GIT_HEAD_DRIFT')
    return {'state': 'PASS_T01_AUTHORITY_AND_SOURCE_VERIFIED', 'head': head,
            'verifiedSourceHashes': dict(PINS), 'action': ACTION}

def run_tests(root: Path) -> dict:
    result=[]
    for test in TESTS:
        # No shell, mutable arguments or network; only allowlisted test modules.
        r=subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', test],
                         cwd=root,env={key:value for key,value in os.environ.items() if key!='PYTHONPATH'} | {'PYTHONDONTWRITEBYTECODE':'1'},
                         capture_output=True,text=True,timeout=90,check=False)
        result.append({'test':test,'returnCode':r.returncode,
                       'outputSha256':_sha_bytes((r.stdout+'\n'+r.stderr).encode('utf-8')),
                       'passed':r.returncode==0,
                       'summary': [line for line in r.stderr.splitlines() if line.startswith(('Ran ', 'OK', 'FAILED '))][-2:]})
        if r.returncode:break
    return {'state':'PASS' if len(result)==len(TESTS) and all(x['passed'] for x in result) else 'HOLD', 'results':result}

def field_entry(root: Path, registry_path: Path, *, expected_head: str | None = None,
                task_path: Path | None = None) -> dict:
    """Actual operator callback. Full E01 requires canonical task input; no fake postcheck.

    Runs authorized read-only tests and reports what executed. Missing task input
    leads to HOLD and does not fabricate a canonical project state or DoneCheck.
    """
    record={'schema':'enguru.suzgec.v23.t01.operator-field/v1','state':'HOLD',
            'action':ACTION,'operatorCallerObserved':True,
            'precheckExecuted':False,'callbackExecuted':False,'postcheckExecuted':False,
            't01Binding':'HOLD','t02':'PENDING','t03':'PENDING','t04':'PENDING_HUMAN',
            'p01':'SUSPENDED','verifiedFinish':'HOLD'}
    try:
        authority=verify_authority(root,registry_path,expected_head=expected_head)
        record['authority']=authority
        # A real fixed allowlisted executor is invoked from the production CLI path.
        observed=run_tests(root)
        record['realExecutorRun']=observed
        record['callbackExecuted']=True
        if observed['state'] != 'PASS':
            record['holdReason']='REAL_REGRESSION_HOLD';return record
        if task_path is None:
            # Scope of this field action is authorization + real test callback.
            # Without canonical active task and verified DoneCheck we cannot execute E01.
            record['state']='PASS_T01_OPERATOR_CALLER_AND_EXECUTOR_OBSERVED'
            record['t01Binding']='PASS_SCOPED_READONLY_CALLER_ONLY'
            record['holdReason']='CANONICAL_ACTIVE_TASK_REQUIRED_FOR_E01_PRE_POST'
            return record
        # We do not load task state from arbitrary paths; active task source is fixed.
        trusted = root/'governance/work-protocol/ENGURU_SUZGEC_V23_ACTIVE_TASK.json'
        if task_path.resolve()!=trusted.resolve():
            raise ValueError('TASK_PATH_SCOPE')
        payload=json.loads(_safe_file(root, 'governance/work-protocol/ENGURU_SUZGEC_V23_ACTIVE_TASK.json').read_text('utf-8'))
        if not isinstance(payload,dict) or set(payload) != {'contract','canonicalState','package'}:
            raise ValueError('ACTIVE_TASK_SCHEMA')
        contract, state, package = payload['contract'],payload['canonicalState'],payload['package']
        if not all(isinstance(v, dict) for v in (contract,state,package)):
            raise ValueError('ACTIVE_TASK_TYPES')
        if (contract.get('project') != 'ENGURU_SUZGEC_V23'
                or state.get('project') != 'ENGURU_SUZGEC_V23'
                or contract.get('executorIdentity') != ACTION
                or contract.get('humanThreshold') != 'HUMAN_ONLY'
                or contract.get('allowedMutations') != ['READ_ONLY_TESTS']
                or contract.get('precheckBound') != PINS['tools/enguru_package_execution_guard.py']
                or contract.get('postcheckBound') != PINS['tools/enguru_package_execution_guard.py']
                or contract.get('sourcePins') != PINS
                or package.get('allowedMutationPaths') != ['READ_ONLY_TESTS']):
            raise ValueError('ACTIVE_TASK_UNAUTHORIZED_SCOPE')
        if state.get('sourceHead') != authority['head']:
            raise ValueError('ACTIVE_TASK_SOURCE_HEAD')
        from tools import enguru_suzgec_v23_execution as e01
        from tools import enguru_package_execution_guard as guard
        from tools.enguru_suzgec_v23_forecast import simulate_missing_authority
        forecast = contract.get('finishPathForecast')
        simulated = simulate_missing_authority(forecast, contract, state)
        if simulated.get('state') != 'PASS':
            raise ValueError('NEGATIVE_SIMULATION_HOLD')
        record['negativeSimulation'] = simulated
        # These are computed from actual scoped CLI, pinned sources and real tests;
        # none of the operator ability flags is read from the user task JSON.
        abilities={'authorizedExecutor':True,'realCallerBound':True,
                   'testEnvironmentReady': observed['state']=='PASS',
                   'donecheckAvailable':(root/'tools/mac_engineer_donecheck_v12_bridge.py').is_file(),
                   'scopeAuthorized':True,'sourcePinsMatch':True,
                   'simulationEvidence': simulated,
                   'realCallerEvidence': {'caller':'mac_engineer_operator.suzgec-v23-t01',
                                          'head': authority['head']}}
        # A deliberately bounded callback: actual tests are re-executed, without
        # treating their success as DoneCheck, Progress or Human Threshold acceptance.
        def execute_tests(_package, _state):
            record['callbackExecuted']=True
            actual=run_tests(root)
            return {'STATE':'PASS' if actual['state']=='PASS' else 'HOLD',
                    'CLAIM':'T01 scoped read-only runtime regression was executed',
                    'EVIDENCE':actual,'PRESERVED_VALUE':'Existing canonical project and P01 preserved',
                    'NECESSARY_DIFFERENCE':'Connect verified v2.3 runtime chain',
                    'JUDGMENT':'HOLD_PENDING_DONECHECK_AND_PROGRESS',
                    'NEXT_ACTION':'T02_FIELD_ACCEPTANCE',
                    'PACKAGE_DONECHECK':'HOLD',
                    'PROGRESS_RECONCILIATION':'HOLD',
                    'STATE_DRIFT':'NONE','UNVERIFIED_PASS':0}
        class ObservedGuard:
            @staticmethod
            def precheck(package, canonical_state):
                record['precheckExecuted']=True
                return guard.precheck(package,canonical_state)
            @staticmethod
            def postcheck(result, canonical_state=None):
                record['postcheckExecuted']=True
                return guard.postcheck(result, canonical_state=canonical_state)
        try:
            final = e01.execute_owned(contract, state, abilities, package,
                                      execute_tests, ObservedGuard)
            record['e01Outcome']=final
            record['state']='PASS_E01_TECHNICAL_EXECUTION_OBSERVED'
            record['t01Binding']='PASS_E01_CHAIN_OBSERVED'
            record['holdReason']='INDEPENDENT_DONECHECK_AND_HUMAN_THRESHOLD_PENDING'
        except Exception as exc:
            record['e01Outcome']='HOLD_'+type(exc).__name__+':'+str(exc)[:240]
            record['holdReason']=record['e01Outcome']
        return record
    except Exception as exc:
        record['holdReason']=type(exc).__name__+':'+str(exc)[:240]
        return record
