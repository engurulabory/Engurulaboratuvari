#!/usr/bin/env python3
"""Zülfikar V1.2: five isolated project design/theory/fixture gates.

Measures THIS proposed adapter only, never canonical 5x100 or official finish.
Source hash and built-in policy test checks are real; field observations remain HOLD.
"""
from __future__ import annotations
import copy, hashlib, io, json, unittest
from pathlib import Path
from zulfikar_v1_2_engine import (CHECKS, FROZEN_SCORE_93, CHAIN, assess,
    canonical_digest, evaluate_design_coverage)
from test_zulfikar_v1_2 import golden, MUTATIONS, design_contract, TestSchemaResistance, TestSim3Stress

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2] if ROOT.name == 'zulfikar-v12' else None
SHA_V3 = '11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc'
IDS = ('Z02_EVENT','Z03_TRANSFER','Z04_LINEAGE','Z05_BENCHMARK',
       'Z08_IMPACT','Z10_CONCURRENCY','Z10_SAFE_FIN')


def review(repo_root: Path | None = None) -> dict:
    root = Path(repo_root) if repo_root else REPO_ROOT
    contract = json.loads((ROOT/'zulfikar_v1_2_design_contract.json').read_text(encoding='utf8'))
    valid_repo = root is not None and (root/'AGENTS.md').is_file()
    v3 = (root/'governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md').read_bytes() if valid_repo else b''
    agents = (root/'AGENTS.md').read_text(encoding='utf8') if valid_repo else ''
    discipline = (root/'governance/enguru-suzgeci/ENGURU_KALICI_CALISMA_DISIPLINI_V1.md').read_text(encoding='utf8') if valid_repo else ''
    lock = json.loads((root/'governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json').read_text(encoding='utf8')) if valid_repo else {}
    stages = ['Hakikati gör','Değeri koru','Eksikleri ve ihtiyaçları tespit et',
              'Gerekli farkı üret','Eksikleri tamamla','Kanıtla','Sonraki ihtiyaçları belirle','İlerlet']
    theory = {
      'T01_CANONICAL_SHA_BYTES':hashlib.sha256(v3).hexdigest()==SHA_V3,
      'T02_LOCK_MATCH':lock.get('sha256')==SHA_V3,
      'T03_AGENTS_SOURCE_LINK':'ENGÜRÜ Evrensel Kanıtlı Tamamlama Talimatı' in agents,
      'T04_AGENTS_HUMAN':'Human Threshold' in agents,
      'T05_EIGHT_STAGES':valid_repo and all(t in discipline for t in stages)
            and [discipline.index(t) for t in stages]==sorted(discipline.index(t) for t in stages),
      'T06_FIXED_BASELINE':tuple(contract.get('base_score',[]))==FROZEN_SCORE_93 and sum(FROZEN_SCORE_93)==93,
      'T07_SEVEN_UNIQUE_CONTROLS':set(contract.get('closure_ids',[]))==set(IDS) and len(contract.get('closure_ids',[]))==7,
      'T08_NO_NEW_AUTHORITY':contract.get('new_core_created') is False and contract.get('new_owner_created') is False,
      'T09_UNMEASURED_PEERS':contract.get('benchmark_state')=='FEATURE_REFERENCES_ONLY / REAL_PEER_TRIALS_NOT_MEASURED',
      'T10_NO_AUTO_SIGNER':assess(golden())['eligible_for_automatic_signature'] is False and assess(golden())['official_verdict']=='NOT_EVALUATED',
    }
    mapping = contract.get('proof_mapping',{})
    design={key:bool(key in CHECKS and key in mapping and mapping[key].get('positive_case')
                     and mapping[key].get('negative_case') and mapping[key].get('oracle')
                     and any(mut[0]==key for mut in MUTATIONS)) for key in IDS}
    design_total=evaluate_design_coverage(contract,True)
    design['D00_FIXED_COVERAGE_SCORE']=design_total.get('provisional')==100
    fixture=golden()
    sim1={cid:CHECKS[cid](fixture[cid])==[] for cid in IDS}
    verdict=assess(fixture)
    sim1['S01_NO_FAKE_OFFICIAL_VERDICT']=verdict['official_verdict']=='NOT_EVALUATED' and verdict['state']=='SIMULATED_DESIGN_READY_TO_REQUEST_REVIEW'
    sim2={}
    for index,(cid,mutation,_) in enumerate(MUTATIONS,1):
        test=copy.deepcopy(fixture)
        mutation(test[cid])
        result=assess(test)
        sim2[f'M{index:02d}_{cid}']=bool(result['state']=='SIMULATED_HOLD'
                                    and result['eligible_for_automatic_signature'] is False
                                    and cid in result['holds'])
    suite=unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestSchemaResistance))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestSim3Stress))
    result=unittest.TextTestRunner(stream=io.StringIO(),verbosity=0).run(suite)
    sim3={'S301_512_MALFORMED_TEST':result.wasSuccessful() and result.testsRun==3,
          'S302_FULL_FIXED_STRESS':result.wasSuccessful() and result.testsRun==3,
          'S303_REPLAY_DETERMINISTIC':canonical_digest(assess(fixture))==canonical_digest(assess(copy.deepcopy(fixture))),
          'S304_SIGNER_REMAINS_EXTERNAL':verdict['eligible_for_automatic_signature'] is False}
    groups={'THEORY':theory,'DESIGN':design,'SIM1':sim1,'SIM2':sim2,'SIM3':sim3}
    scores={name:round(100*sum(bool(v) for v in checks.values())/len(checks),6)
            for name,checks in groups.items()}
    return {'schema':'enguru.zulfikar.v1.2.local-five-gate/v1',
            'state':'LOCAL_FIVE_GATE_CANDIDATE_PASS' if all(v==100 for v in scores.values()) else 'HOLD_UNMET_CONTROLS',
            'scores':scores,'groups':groups,
            'design_rubric_93_plus_7':design_total.get('provisional'),
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('zulfikar_v1_2_engine.py','test_zulfikar_v1_2.py','zulfikar_v1_2_design_contract.json')},
            'not_proven':['EXACT_HEAD_CI','OFFICIAL_PROJECT_5X100','REAL_BENCHMARK','REAL_USER_IMPACT','REAL_OSI_FIELD','HUMAN_ACCEPTANCE','VERIFIED_FINISH'],
            'official_verified_finish':'HOLD'}

if __name__=='__main__':
    evidence=review()
    print(json.dumps(evidence,ensure_ascii=False,sort_keys=True,indent=2))
    raise SystemExit(0 if evidence['state']=='LOCAL_FIVE_GATE_CANDIDATE_PASS' else 2)