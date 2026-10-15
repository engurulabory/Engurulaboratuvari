"""Adversarial coverage for v2.3 measurable goal / runtime acceptance."""
import copy, unittest
from tools.enguru_suzgec_v23_goal_acceptance import (SCHEMA,EVIDENCE_SCHEMA,CRITERIA,
    AcceptanceHold,pin,validate_boundary,assess_outcome)
from tools.enguru_suzgec_v23_execution import readiness,ExecutionHold,execute_owned


def case():
    state={'project':'ENGURU_SUZGEC_V23','operatingFramework':{'holisticFinishV22':{'state':'ENFORCE'}}}
    contract={'project':state['project'],'goal':'v2.3 active real runtime', 'sourcePins':{'guard':'pinned'},
       'allowedMutations':['READ_ONLY_TESTS'],'executorIdentity':'source-bound-operator',
       'precheckBound':'pinned','postcheckBound':'pinned','testCommands':['unittest'],
       'donecheckBinding':'DoneCheck-v1.2','githubPlan':'draft-only','humanThreshold':'HUMAN_ONLY'}
    criteria=[]
    for name in CRITERIA:
        criteria.append({'id':name,'required':True,'description':'A measurable outcome for '+name,
           'measurement':{'type':'BOOLEAN','target':True},'environment':'OSi_LOCAL_REAL',
           'evidenceSource':'SOURCE_BOUND_FIELD_PRODUCER', 'holdReason':'HOLD_'+name})
    boundary={'schema':SCHEMA, 'project':state['project'],'goal':contract['goal'],
         'sourcePins':contract['sourcePins'], 'humanScopeAuthority':'HUMAN_ONLY',
         'verifiedFinishAuthority':'HUMAN_ONLY', 'decision':'SCOPE_REVIEWED_NEEDS_AUTHENTICATED_PROOF',
         'criteria':criteria}
    contract['acceptanceCriteria']=criteria
    contract['goalOutcomeAcceptance']=boundary
    observation={'schema':EVIDENCE_SCHEMA,'project':state['project'],'goal':contract['goal'],
        'canonicalSha256':pin(state),'boundarySha256':pin(boundary),'sourcePins':contract['sourcePins'],
        'criteria':[{'id':c['id'],'environment':c['environment'],'observedValue':True,
                 'evidenceRef':'AudiV13/evidence-'+c['id']+'.json','evidenceSha256':'1'*64} for c in criteria]}
    return contract,state,boundary,observation

class TestAcceptance(unittest.TestCase):
    def test_valid_structured_contract_only(self):
        c,s,b,o=case();r=validate_boundary(b,c,s);self.assertEqual(r['state'],'PASS_ACCEPTANCE_BOUNDARY_STRUCTURE_ONLY');self.assertFalse(r['fieldVerified'])
    def test_empty_missing(self):
        c,s,b,o=case()
        with self.assertRaisesRegex(AcceptanceHold,'BOUNDARY_TYPE'):validate_boundary(None,c,s)
    def test_meaningless_string(self):
        c,s,b,o=case();c['acceptanceCriteria']=['ANY_STRING'];
        with self.assertRaisesRegex(AcceptanceHold,'CRITERIA_MISMATCH'):validate_boundary(b,c,s)
    def test_criterion_missing(self):
        c,s,b,o=case();b['criteria'].pop()
        with self.assertRaisesRegex(AcceptanceHold,'CRITERIA_COUNT'):validate_boundary(b,c,s)
    def test_duplicate_criterion(self):
        c,s,b,o=case();b['criteria'][3]['id']=b['criteria'][0]['id']
        with self.assertRaisesRegex(AcceptanceHold,'CRITERIA_ORDER'):validate_boundary(b,c,s)
    def test_optional_criterion(self):
        c,s,b,o=case();b['criteria'][3]['required']=False
        with self.assertRaisesRegex(AcceptanceHold,'CRITERION_OPTIONAL'):validate_boundary(b,c,s)
    def test_target_must_exist(self):
        c,s,b,o=case();b['criteria'][0]['measurement']['target']=None
        with self.assertRaisesRegex(AcceptanceHold,'MEASUREMENT_TARGET'):validate_boundary(b,c,s)
    def test_environment_required(self):
        c,s,b,o=case();b['criteria'][2]['environment']=''
        with self.assertRaisesRegex(AcceptanceHold,'TARGET_ENVIRONMENT'):validate_boundary(b,c,s)
    def test_project_drift(self):
        c,s,b,o=case();b['project']='OTHER'
        with self.assertRaisesRegex(AcceptanceHold,'PROJECT_DRIFT'):validate_boundary(b,c,s)
    def test_boundary_digest_drift(self):
        c,s,b,o=case();o['boundarySha256']='0'*64
        with self.assertRaisesRegex(AcceptanceHold,'BOUNDARY_DRIFT'):assess_outcome(b,c,s,o,lambda *args:True,lambda *args:True)
    def test_canonical_digest_drift(self):
        c,s,b,o=case();o['canonicalSha256']='0'*64
        with self.assertRaisesRegex(AcceptanceHold,'CANONICAL_STATE_DRIFT'):assess_outcome(b,c,s,o,lambda *args:True,lambda *args:True)
    def test_unverified_scope_holds(self):
        c,s,b,o=case();r=assess_outcome(b,c,s,o,lambda *args:True)
        self.assertEqual(r['reason'],'HOLD_HUMAN_SCOPE_APPROVAL_UNVERIFIED')
    def test_scope_rejection_holds(self):
        c,s,b,o=case();r=assess_outcome(b,c,s,o,lambda *args:True,lambda *args:False)
        self.assertEqual(r['reason'],'HOLD_HUMAN_SCOPE_APPROVAL_UNVERIFIED')
    def test_unverified_evidence_holds(self):
        c,s,b,o=case();r=assess_outcome(b,c,s,o,None,lambda *args:True)
        self.assertEqual(r['reason'],'HOLD_TRUSTED_EVIDENCE_VERIFIER_UNBOUND')
    def test_failure_detected(self):
        c,s,b,o=case();o['criteria'][2]['observedValue']=False
        r=assess_outcome(b,c,s,o,lambda *args:True,lambda *args:True)
        self.assertEqual(r['reason'],'HOLD_K03_RUNTIME_OPERABLE')
    def test_evidence_digest_malformed(self):
        c,s,b,o=case();o['criteria'][2]['evidenceSha256']='not-sha'
        with self.assertRaisesRegex(AcceptanceHold,'MISSING_EVIDENCE_SHA256'):assess_outcome(b,c,s,o,lambda *args:True,lambda *args:True)
    def test_wrong_environment(self):
        c,s,b,o=case();o['criteria'][2]['environment']='TEST_ONLY'
        with self.assertRaisesRegex(AcceptanceHold,'ENVIRONMENT_MISMATCH'):assess_outcome(b,c,s,o,lambda *args:True,lambda *args:True)
    def test_evidence_provenance_rejection(self):
        c,s,b,o=case();r=assess_outcome(b,c,s,o,lambda *args:False,lambda *args:True)
        self.assertEqual(r['reason'],'HOLD_EVIDENCE_PROVENANCE:K01_GOAL_ACHIEVED')
    def test_all_measured_still_requires_donecheck_and_human(self):
        c,s,b,o=case();r=assess_outcome(b,c,s,o,lambda *args:True,lambda *args:True)
        self.assertEqual(r['state'],'PASS_PACKAGE_OUTCOME_MEASURED');self.assertEqual(r['criteriaPassed'],7)
        self.assertEqual(r['verifiedFinish'],'HOLD');self.assertIn('DONECHECK',r['technicalFinish'])
    def test_scope_state_pending_never_pass(self):
        c,s,b,o=case();b['decision']='SCOPE_REVIEW_PENDING'
        o['boundarySha256']=pin(b)
        self.assertEqual(assess_outcome(b,c,s,o,lambda *args:True,lambda *args:True)['reason'],'HOLD_HUMAN_SCOPE_APPROVAL_UNVERIFIED')
    def test_source_pin_mismatch(self):
        c,s,b,o=case();c['sourcePins']={'other':'pin'}
        with self.assertRaisesRegex(AcceptanceHold,'SOURCE_DRIFT'):validate_boundary(b,c,s)
    def test_metric_minimum(self):
        c,s,b,o=case();b['criteria'][0]['measurement']={'type':'MINIMUM','target':10}
        c['acceptanceCriteria']=b['criteria'];o['boundarySha256']=pin(b);o['criteria'][0]['observedValue']=11
        self.assertEqual(assess_outcome(b,c,s,o,lambda *a:True,lambda *a:True)['state'],'PASS_PACKAGE_OUTCOME_MEASURED')
        o['criteria'][0]['observedValue']=9
        self.assertEqual(assess_outcome(b,c,s,o,lambda *a:True,lambda *a:True)['reason'],'HOLD_K01_GOAL_ACHIEVED')
    def test_metric_exact(self):
        c,s,b,o=case();b['criteria'][6]['measurement']={'type':'EXACT','target':'PASS'}
        c['acceptanceCriteria']=b['criteria'];o['boundarySha256']=pin(b);o['criteria'][6]['observedValue']='PASS'
        self.assertEqual(assess_outcome(b,c,s,o,lambda *a:True,lambda *a:True)['criteriaPassed'],7)
        o['criteria'][6]['observedValue']='PASSISH'
        self.assertEqual(assess_outcome(b,c,s,o,lambda *a:True,lambda *a:True)['reason'],'HOLD_K07_TECHNICAL_GATES_PASS')
    def test_e01_acceptance_boundary_required_for_v23(self):
        c,s,b,o=case();c['goalOutcomeAcceptance']=None
        c['finishPathForecast']=_fake_forecast(c,s)
        a=_abilities()
        with self.assertRaisesRegex(ExecutionHold,'ACCEPTANCE_BOUNDARY_TYPE'):readiness(c,s,a)
    def test_e01_post_requires_actual_outcome(self):
        c,s,b,o=case();c['finishPathForecast']=_fake_forecast(c,s)
        class Guard:
            def precheck(self,*args):return {'decision':'EXECUTE'}
            def postcheck(self,*args,**kwargs):return {'decision':'ADVANCE'}
        with self.assertRaisesRegex(ExecutionHold,'GOAL_OUTCOME_OBSERVATION_MISSING'):
            execute_owned(c,s,_abilities(),{},lambda *a: {'STATE':'PASS'},Guard())

def _fake_forecast(c,s):
    from tools.enguru_suzgec_v23_forecast import SCHEMA,MANDATORY_SCENARIOS,sha256_json
    steps=[]
    for i,gate in enumerate(('T01','T02','T03','T04')):
        steps.append({'id':gate,'owner':'HUMAN_ONLY' if i==3 else 'existing-authorized-operator',
            'dependencies':[] if i==0 else ['T0'+str(i)],'holdConditions':['hold'],
            'passEvidence':['sha-reference'],'authorizedRecovery':'bounded',
            'status':'PENDING_HUMAN' if i==3 else 'HOLD'})
    return {'schema':SCHEMA,'project':s['project'],'version':'2.3','goal':c['goal'],
       'sourcePins':c['sourcePins'],'canonicalStateSha256':sha256_json(s),
       'humanThreshold':'HUMAN_ONLY','steps':steps,'predictionVsObservation':'REQUIRED_POST_EXECUTION',
       'simulations':[{'scenario':x,'expectedState':'HOLD'} for x in MANDATORY_SCENARIOS]}

def _abilities():
    return {'authorizedExecutor':True,'realCallerBound':True,'testEnvironmentReady':True,
         'donecheckAvailable':True,'scopeAuthorized':True,'sourcePinsMatch':True,
         'simulationEvidence':'source-pinned-caller','realCallerEvidence':'source-pinned-caller'}

if __name__=='__main__':unittest.main()
