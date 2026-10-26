#!/usr/bin/env python3
"""Zülfikar V1.4.1 DÖM pre-GitHub verification: LOCAL, NOT a GitHub or Mac action.

Compiles, runs distinct real subprocess tests three times, reconciles eight
architecture gates and tests, saves logs. Never issues a product PASS.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent
GATES = ('T01','T02','A01','A02','A03','A04','A05','A06')
NATIVE_SCOPE = 'PRE_GITHUB_PREPARATION_AND_DISPOSABLE_TESTS_ONLY'
BASELINE_TESTS=38
HARDENING_TESTS=21
EXPECTED_TESTS=BASELINE_TESTS+HARDENING_TESTS
HARDENING_REQUIREMENTS = {
    'D01': ('test_39_predecessor_gate_missing_blocks_A01','test_41_predecessor_wrong_goal_blocks',
            'test_45_forged_source_probe_cannot_bypass_real_bytes','test_46_missing_source_path_blocks'),
    'D02': ('test_44_mock_external_verifier_still_not_official_pass',
            'test_55_real_process_test_and_pinned_checkpoint','test_57_all_eight_gates_unchanged'),
    'D03': ('test_47_symlinked_source_file_fails_closed',
            'test_48_hardlinked_source_file_fails_closed','test_55_real_process_test_and_pinned_checkpoint'),
    'D04': ('test_49_journal_symlink_fails','test_50_journal_hardlink_fails',
            'test_51_incomplete_journal_line_fails','test_54_writer_competing_process_rejected'),
    'D05': ('test_42_predecessor_self_claim_without_verifier_blocks','test_43_predecessor_verifier_refuses',
            'test_53_lockfile_symlink_fails','test_56_local_journal_cannot_issue_owner_pass')
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('MISSING_OR_SYMLINK_SOURCE')
    return json.loads(path.read_text(encoding='utf8'))


def architecture_evidence():
    arch=load_json(ROOT/'architecture/zulfikar_v141_8_gate_architecture.json')
    design=load_json(ROOT/'architecture/dom_v10_design.json')
    import dom.engine as engine
    rows=arch['gates']
    names=[x['id'] for x in rows]
    checks={
        'A01_exact_eight_gate_order':tuple(names)==GATES and engine.GATES==GATES,
        'A02_two_separate_foundation_gates':rows[0]['name']!=rows[1]['name'],
        'A03_six_distinct_engineering_gates':names[2:]==list(GATES[2:]),
        'A04_unique_scope_bound_acceptance':len({x['acceptance'] for x in rows})==8,
        'A05_five_distinct_required_outputs_per_gate':all(len(x['requiredOutputs'])==5 and len(set(x['requiredOutputs']))==5 for x in rows),
        'A06_all_ten_shared_capabilities':len(arch['coreTenSharedCapabilities'])==10 and len(set(arch['coreTenSharedCapabilities']))==10,
        'A07_original_user_goal_and_stop':arch['userGoalContract']['id']=='ZF.V141.PREGH.2026-10-26' and arch['userGoalContract']['stopEvent']=='NEXT_ACTION_IS_GITHUB_REGISTRATION_AND_CI',
        'A08_pilive_frozen':arch['frozenPilive']['prohibitEditingPiLive'] is True,
        'A09_field_and_issuer_kept_separate':rows[6]['preGithubStatus']=='NOT_EXECUTED_OWNER_SCOPE_REQUIRED' and 'OfficialDoneCheckIssuance' in arch['prohibitBeforeApproval'],
        'A10_source_and_stage_guards_real':arch['universalIteration']=='dom/engine.py' and arch['phaseNow']=='STOP_BEFORE_GITHUB' and inspect.signature(engine.execute).parameters.get('predecessor_verifier') is not None and inspect.signature(engine.execute).parameters.get('source_file') is not None,
    }
    reqs=design['fiveEqualWeightEngineeringRequirements']
    if (len(reqs)!=5 or [x['id'] for x in reqs]!=['D01','D02','D03','D04','D05'] or
        any(x['weight']!=20 or len(x['evidenceTests'])!=4 or len(x['requirements'])!=4 for x in reqs) or
        design['scope']!=NATIVE_SCOPE or design['stopAt']!='BEFORE_GITHUB_WRITE_OR_ACTIONS' or
        any(v is not True for v in checks.values())):
        raise ValueError('ARCHITECTURE_SOURCE_CONTROL_FAILED')
    return {'controls':checks,'gatesDefined':names,'originalUserGoal':arch['userGoalContract']['id'],
            'tenCapabilitiesReferenced':arch['coreTenSharedCapabilities']},reqs


def run():
    structure,requirements=architecture_evidence()
    testnames=None
    rounds=[]
    for cycle in (1,2,3):
        log=ROOT/'evidence'/f'final_round_{cycle}.log'
        with log.open('wb') as output:
            proc=subprocess.run([sys.executable,'-B','-m','unittest','discover',
                                 '-s','dom','-p','test_*.py','-v'],cwd=ROOT,
                                stdout=output,stderr=subprocess.STDOUT,timeout=45,check=False)
        text=log.read_text(encoding='utf8')
        count=re.search(r'Ran\s+(\d+)\s+tests\s+in',text)
        names=set(re.findall(r'^(test_[A-Za-z0-9_]+)\s+\(',text,re.M))
        if (proc.returncode!=0 or count is None or int(count.group(1))!=EXPECTED_TESTS or
            len(names)!=EXPECTED_TESTS or '\nOK\n' not in text or
            '\nFAILED' in text or '\nERROR:' in text or
            (testnames is not None and testnames!=names)):
            raise RuntimeError(f'TEST_ROUND_FAILED_{cycle}_{proc.returncode}_{len(names)}')
        testnames=names
        rounds.append({'cycle':cycle,'tests':EXPECTED_TESTS,'distinctTests':len(names),
                       'pass':True,'logSha256':digest(log)})
    tested=[]
    for row in requirements:
        rid=row['id']
        baseline=all(name in testnames for name in row['evidenceTests'])
        hardening=all(name in testnames for name in HARDENING_REQUIREMENTS[rid])
        tested.append({'id':rid,'name':row['name'],'points':row['weight'] if baseline and hardening else 0,
                       'baselineCoverage':baseline,'independentAdversarialCoverage':hardening,
                       'sourceRequirements':row['requirements']})
    scored=sum(x['points'] for x in tested)
    if scored!=100:
        raise RuntimeError('INCOMPLETE_PRE_GITHUB_ENGINEERING_COVERAGE')
    proof_files=['dom/engine.py','dom/test_engine.py','dom/test_final_hardening.py',
                 'architecture/dom_v10_design.json','architecture/zulfikar_v141_8_gate_architecture.json',
                 'preflight.py']
    result={
       'schema':'enguru.zulfikar.v141-pregithub-final-engineering-review/v1',
       'utc':dt.datetime.now(dt.timezone.utc).isoformat(),
       'verificationScope':NATIVE_SCOPE,
       'engineerPreparationScore':scored,
       'status':'LOCAL_SOURCE_AND_TEST_PREPARATION_100_PASS',
       'architectureDesignControlsPassed':len(structure['controls']),
       'architectureDesignControlsRequired':10,
       'architecture':structure,
       'fiveEngineeringDomains':tested,
       'threeRealLocalTestRounds':rounds,
       'realLocalUnittestExecutions':sum(x['tests'] for x in rounds),
       'testedRealTaskMechanism':'ISOLATED_DISPOSABLE_ARTIFACT_AND_SEPARATE_OS_PROCESS',
       'portableCommandAvailability':'SHA256SUM_ON_LINUX_SHASUM_ON_MAC_DESIGN_ONLY',
       'sourceHashes':{p:digest(ROOT/p) for p in proof_files},
       'journalAuthority':'LOCAL_UNTRUSTED_UNTIL_EXTERNALLY_PINNED_AND_REVIEWED',
       'tenFullRealCapabilities':'NO_PRODUCT_WIDE_100_ASSERTED',
       'MacOwnerOrNativeField':'NOT_EXECUTED',
       'GitHubCommitOrCI':('ACTION_RUNNER_TEST_SCOPE_ONLY' if os.environ.get('GITHUB_ACTIONS')=='true' else 'NOT_STARTED'),
       'productVerifiedFinish':'NOT_ISSUED',
       'PiLive':'PARKED_UNCHANGED',
       'next':'OWNER_AUTHORIZED_GITHUB_REGISTRATION_AND_CI_AFTER_APPROVAL',
       'stop':'BEFORE_GITHUB_WRITE_OR_ACTIONS'
    }
    (ROOT/'evidence/pre_github_readiness_report.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'preGithubPreparationScore':scored,'rounds':3,'tests':result['realLocalUnittestExecutions'],
                      'architecture':'10/10','next':result['stop']},ensure_ascii=False))
    return result


if __name__=='__main__':
    run()
