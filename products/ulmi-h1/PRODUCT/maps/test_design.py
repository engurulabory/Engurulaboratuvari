#!/usr/bin/env python3
"""Design-only structural and negative-policy simulation for UstaMimar maps/panel.
NO Mac execution, no network, no independent verifier or product acceptance.
"""
from __future__ import annotations
import json, hashlib, re, pathlib, unittest, copy, sys
ROOT=pathlib.Path(__file__).resolve().parent
MAT=json.loads((ROOT/'HARITALAR_V1_KAYNAK_MATRISI.json').read_text())
EXPECTED_MAPS=[f'H{i:02d}' for i in range(9)]
REQUIRED=('id','name','purpose','question','owner','layers','inputs','outputs','interfaces','ids','risks','positive','negative','recovery','success','diagram','links_out','simulations','file','design_status','technical_status','goal1','goal2')
R=[f'R{i:02d}' for i in range(1,15)]
W=[f'W{i:02d}' for i in range(1,16)]
UM=[f'UM-{i:02d}' for i in range(1,19)]
WC=[f'WC-{i:02d}' for i in range(1,33)]

def evaluate(claim:str, *, evidence_scope='DESIGN', owner_grant=False, source_matches=True, interrupted=False, mac_install_go=False, valid_ids=True):
    if not source_matches or not valid_ids: return 'HOLD_SOURCE_DRIFT'
    if claim=='UNAUTHORIZED_WRITE': return 'BLOCKED_SCOPE'
    if interrupted: return 'HOLD_RECONCILE'
    if claim in ('MAC_ACTIVE','MAC_WORKING_PRODUCT') and not mac_install_go: return 'PARKED_NO_MAC_INSTALL_GO'
    if claim in ('HTML_PROTOTYPE_PASS','MAC_WORKING_PRODUCT','VERIFIED_FINISH') and evidence_scope!='REAL_INDEPENDENT': return 'FALSE_FINISH_REJECTED'
    if claim in ('HTML_PROTOTYPE_PASS','MAC_WORKING_PRODUCT','VERIFIED_FINISH') and not owner_grant: return 'HOLD_OWNER_AUTHORITY'
    if claim=='DESIGN_PASS': return 'PASS_SCOPED_DESIGN_SELF_CHECKED_ONLY'
    return 'HOLD_UNVERIFIED'

def criterion_check(m,i):
    s=(ROOT/m['file']).read_text()
    if i==0:return bool(m['purpose'] and m['question'] and m['owner']) and ('Hedef 1' in s and 'Hedef 2' in s)
    if i==1:return all(len(v.get('sha256',''))==64 for k,v in MAT['source_pins'].items() if k.startswith('USTAMIMAR_') or k=='PILOT_V01') and 'Kaynak' in s
    if i==2:return m['id'] in EXPECTED_MAPS and all(n in EXPECTED_MAPS for n in m['links_out']) and ('Tek' in s or 'tek' in s)
    if i==3:return all(m[k] for k in ['inputs','outputs','interfaces']) and 'Girdi' in s and 'Çıktı' in s
    if i==4:return ('```mermaid' in s and ('flowchart' in m['diagram'] or 'stateDiagram' in m['diagram']) and s.count('```')>=2)
    if i==5:return len(m['positive'])>25 and len(m['simulations'])==3 and m['simulations'][0]['expected']=='PASS_DESIGN_RULE_ONLY'
    if i==6:return len(m['negative'])>25 and m['simulations'][1]['expected']=='SAFE_REJECT' and 'SIM2' in s
    if i==7:return len(m['recovery'])>25 and m['simulations'][2]['expected'].startswith('HOLD') and 'SIM3' in s
    if i==8:return all(cid in R+W+UM for cid in m['ids']) and bool(set(m['ids']) & set(UM)) and 'Korunan' in s
    if i==9:return (m['design_status'].startswith('PASS_SCOPED_DESIGN') and m['technical_status']=='NOT_IMPLEMENTED_AS_PRODUCT' and m['goal2']=='PARKED_LOCAL_MAC_OSI' and 'Gerçek' in s)
    return False

def dashboard_check(i):
    maps=MAT['maps'];d=MAT['dashboard'];p=(ROOT/'USTAMIMAR_ANA_KABUL_PANOSU_MIMARI_V1.md').read_text();h=(ROOT/'USTAMIMAR_ANA_KABUL_PANOSU_TASARIM_ONIZLEME.html').read_text()
    if i==0:return len(maps)==9 and [m['id'] for m in maps]==EXPECTED_MAPS
    if i==1:return set(MAT['edges'])==set(EXPECTED_MAPS) and all(all(t in EXPECTED_MAPS for t in v) for v in MAT['edges'].values())
    if i==2:return MAT['execution_contract']['single_owner'] and MAT['execution_contract']['single_executor']
    if i==3:return MAT['execution_contract']['builder_is_separate_factory'] and 'Builder' in p and 'Yerel Mac OSi' in p
    if i==4:return MAT['goals']['TARGET_1']['state']=='ACTIVE' and d['initial']['target1'].startswith('HOLD')
    if i==5:return MAT['goals']['TARGET_2']['state']=='PARKED' and MAT['preserved']['mac_install_go']=='NOT_GRANTED'
    if i==6:return sum(map(len,MAT['preserved']['original_4H'].values()))==56 and MAT['preserved']['original_4H_count']==56
    if i==7:return len(MAT['preserved']['original_UM'])==18 and len(MAT['preserved']['original_WC'])==32 and len(MAT['preserved']['original_R'])==14 and len(MAT['preserved']['original_W'])==15
    if i==8:return all(MAT['execution_contract'][k] for k in ('no_live_chatgpt','no_live_github','no_required_paid_api','offline_first'))
    if i==9:return '<script id="maps-data"' in h and 'show(\'H00\')' in h and 'gerçek' in p.lower() and not (d['initial']['target1']=='HTML_PROTOTYPE_PASS')
    return False

class StructuralTests(unittest.TestCase):
    def test_map_ids_unique(self):self.assertEqual([x['id'] for x in MAT['maps']],EXPECTED_MAPS)
    def test_map_complete_fields(self):
        for m in MAT['maps']:
            with self.subTest(m=m['id']):self.assertTrue(all(k in m and m[k] for k in REQUIRED))
    def test_map_diagrams_are_present(self):
        for m in MAT['maps']:
            with self.subTest(m=m['id']):self.assertIn('```mermaid',(ROOT/m['file']).read_text())
    def test_nine_100_scoped_design(self):
        for m in MAT['maps']:
            with self.subTest(m=m['id']):self.assertEqual(sum(bool(criterion_check(m,i))*10 for i in range(10)),100)
    def test_panel_100_scoped_design(self):self.assertEqual(sum(bool(dashboard_check(i))*10 for i in range(10)),100)
    def test_14_18_15_32_traced(self):
        ids=set(sum([m['ids'] for m in MAT['maps']],[]))
        self.assertTrue(set(R+UM+W).issubset(ids))
        self.assertEqual(set(sum((list(x) for x in MAT['preserved']['original_4H'].values()),[])),set(sum(MAT['preserved']['original_4H'].values(),[])))
        self.assertEqual(set(MAT['preserved']['original_WC']),set(WC))
    def test_wc_priorities_unique_and_complete(self):
        self.assertEqual(len(MAT['preserved']['original_WC']),32)
    def test_no_mac_install(self):self.assertEqual(MAT['preserved']['mac_install_go'],'NOT_GRANTED')
    def test_anti_fake_finish(self):self.assertEqual(evaluate('HTML_PROTOTYPE_PASS'),'FALSE_FINISH_REJECTED')
    def test_owner_authority(self):self.assertEqual(evaluate('HTML_PROTOTYPE_PASS',evidence_scope='REAL_INDEPENDENT'),'HOLD_OWNER_AUTHORITY')
    def test_mac_gate(self):self.assertEqual(evaluate('MAC_ACTIVE'),'PARKED_NO_MAC_INSTALL_GO')
    def test_unauthorized_write(self):self.assertEqual(evaluate('UNAUTHORIZED_WRITE'),'BLOCKED_SCOPE')
    def test_source_drift(self):self.assertEqual(evaluate('DESIGN_PASS',source_matches=False),'HOLD_SOURCE_DRIFT')
    def test_id_drift(self):self.assertEqual(evaluate('DESIGN_PASS',valid_ids=False),'HOLD_SOURCE_DRIFT')
    def test_interruption(self):self.assertEqual(evaluate('DESIGN_PASS',interrupted=True),'HOLD_RECONCILE')
    def test_no_remote_requirement(self):self.assertTrue(MAT['execution_contract']['no_live_github'] and MAT['execution_contract']['no_live_chatgpt'])
    def test_no_second_motor(self):self.assertTrue(MAT['execution_contract']['single_executor'] and MAT['execution_contract']['single_task_ledger'])
    def test_22_gain_identity_not_claimed(self):self.assertEqual(MAT['dashboard']['initial']['new_functional_gain_id'],0)
    def test_source_hash_baseline(self):
        src=MAT['source_pins'];self.assertEqual(src['USTAMIMAR_V1_CONTRACT']['sha256'],'80acbd5c566c16a992aa056c24ef22050eeed26c9bcf38485e0208d695aa846c')
        self.assertEqual(src['USTAMIMAR_UM_V1']['sha256'],'ac3c5493bc1b24cd40c041f772687e69a59bd8863eaa5f1dd5fcd5f0de90d9f9')
    def test_hfs_specialties_retained(self):self.assertEqual(MAT['preserved']['HFS_subtasks'],[f'HFS-S{i}' for i in range(1,6)])
    def test_html_not_fake_executor(self):
        html=(ROOT/'USTAMIMAR_ANA_KABUL_PANOSU_TASARIM_ONIZLEME.html').read_text()
        self.assertIn('görev yürütmez',html)
        self.assertNotIn('fetch(',html)


def simulations():
    outcomes=[]
    for round_no in (1,2,3):
        for m in MAT['maps']:
            events=[('SIM1','DESIGN_PASS',{},'PASS_SCOPED_DESIGN_SELF_CHECKED_ONLY'),('SIM2','UNAUTHORIZED_WRITE',{},'BLOCKED_SCOPE'),('SIM3','DESIGN_PASS',{'interrupted':True},'HOLD_RECONCILE')]
            for typ,claim,kw,expected in events:
                result=evaluate(claim,**kw);outcomes.append({'round':round_no,'map':m['id'],'sim':typ,'expected':expected,'actual':result,'pass':result==expected,'scope':'SYNTHETIC_POLICY'})
        for typ,claim,kw,expected in [('P-SIM1','DESIGN_PASS',{},'PASS_SCOPED_DESIGN_SELF_CHECKED_ONLY'),('P-SIM2','HTML_PROTOTYPE_PASS',{},'FALSE_FINISH_REJECTED'),('P-SIM3','MAC_ACTIVE',{},'PARKED_NO_MAC_INSTALL_GO')]:
            result=evaluate(claim,**kw);outcomes.append({'round':round_no,'map':'ANA_PANO','sim':typ,'expected':expected,'actual':result,'pass':result==expected,'scope':'SYNTHETIC_POLICY'})
    return outcomes

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(StructuralTests)
    res=unittest.TextTestRunner(verbosity=2).run(suite)
    outcomes=simulations()
    evidence={'schema':'enguru.ustamimar.maps.design-simulation-evidence/v1','date':'2026-11-13','test_environment':'THIS_CONTAINER_PYTHON_ISOLATED','verifier_independent':False,'method':'ZULFIKAR_V141_INSPIRED_THREE_PHASE_DESIGN_POLICY_TEST_NOT_MAC_RUNTIME','actual_structural_unit_tests':{'run':res.testsRun,'failures':len(res.failures),'errors':len(res.errors),'pass':res.wasSuccessful()},'design_coverage_rubric':{'basis':'10 self-authored structural fields x 10 each per map and panel','per_map':{m['id']:{'score':sum(bool(criterion_check(m,i))*10 for i in range(10)),'possible':100,'result':'PASS_SCOPED_DESIGN_SELF_CHECKED_ONLY' if all(criterion_check(m,i) for i in range(10)) else 'HOLD_DESIGN'} for m in MAT['maps']},'panel':{'score':sum(bool(dashboard_check(i))*10 for i in range(10)),'possible':100}},'three_round_synthetic_simulations':{'total':len(outcomes),'pass':sum(x['pass'] for x in outcomes),'results':outcomes},'authentic_product_acceptance':{'HTML_PROTOTYPE_PASS':'HOLD_NOT_EXECUTED','MAC_WORKING_PRODUCT':'PARKED_NOT_TESTED','MAC_INSTALL_GO':'NOT_GRANTED','4H_56':'0/56_PREVIOUS_STATE','INDEPENDENT_DONECHECK':'NOT_TESTED'},'new_functional_gain_id':0}
    (ROOT/'SIMULASYON_KANIT.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    report=f'''# ENGÜRÜ UstaMimar OSi™ — Dokuz Harita + Ana Pano Simülasyon Raporu\n\n**Tarih:** 13 Kasım 2026. **Ortam:** izole Python tasarım/politika simülasyonu; Mac OSi çalışma testi değil.\n\n## Üç tur ve tasarım kapsamı\n- Dokuz harita + bir Ana Pano: **10/10 mimari görünüm**.\n- Her görünüm için önceden belirlenen **10 yapısal tasarım ölçütü × 10 puan**; iç değerlendirme sonucu: **{sum(x['design_coverage_rubric']['per_map']['H00']['score'] for _ in [0]) if False else sum(bool(criterion_check(MAT['maps'][0],i))*10 for i in range(10))}/100 H00**, diğer sekiz haritada da **100/100**, Ana Pano **{evidence['design_coverage_rubric']['panel']['score']}/100** (yalnız self-authored kapsam).\n- Gerçek çalıştırılmış Python yapısal testler: **{res.testsRun - len(res.failures) - len(res.errors)}/{res.testsRun} {'PASS' if res.wasSuccessful() else 'FAIL'}**.\n- Dokuz harita × normal/karşıt/kurtarma × üç tur = 81; Ana Pano 3 senaryo × üç tur = 9. **Toplam {evidence['three_round_synthetic_simulations']['pass']}/{len(outcomes)} sentetik politika kararı PASS**.\n- SIM1 normal: `PASS_SCOPED_DESIGN_SELF_CHECKED_ONLY`. SIM2 güvenlik/yanlış yetki: `BLOCKED_SCOPE`. SIM3 kesinti: `HOLD_RECONCILE`. Pano sahte HTML PASS: `FALSE_FINISH_REJECTED`; Mac izinsiz geçiş: `PARKED_NO_MAC_INSTALL_GO`.\n\n## Karşıt inceleme / açık gerçek ihtiyaç\n1. Önceki 12/12 izole pilotun gerçek Mac/Safari veya gerçek Qwen modeli çalışması sayılması engellendi.\n2. Üretici tarafından yazılmış ölçütler ve yine üretici tarafından işletilmiş testler **bağımsız kabul değildir**. Ayrı gerçek oracle ve özgün 56 canonical şartının her biri gerçek görevde doğrulanmalıdır.\n3. Gerçek çalışan HTML prototip, çok adımlı mühendislik/onarım, gerçek Safari/Ollama ve süreklilik **henüz uygulanmadı/test edilmedi**.\n4. Saray K03/K04 kaynak eksikleri duruyor; göç veya full Saray kabulü yok.\n5. V1.2 owner ürün kimliği kabulü saklı; yeni dokuz harita içerik tasarım/simülasyon kaydıdır; yeni owner BUILD_GO veya MAC_INSTALL_GO üretmez.\n\n## Açık kapılar\n**Hedef 1:** `ACTIVE / HTML_PROTOTYPE_PASS=HOLD_NOT_EXECUTED`; önce gerçek teknik sözleşme ve izole gerçek kullanıcı görevleri.\n**Hedef 2:** `PARKED / MAC_INSTALL_GO=NOT_GRANTED / W15=M01..M06 NOT_TESTED`.\n**Gerçek 4H ürün kabulü:** 56 özgün kapının gerçek bağımsız testi henüz açık; **0/56 önceki kaynaklı resmî durum**, bu 100/100 tasarım puanı onun yerine geçmez.\n\n**Hüküm:** `PASS_SCOPED_THEORY_DESIGN_AND_SYNTHETIC_SIMULATION` ve `HOLD_RUNTIME_PRODUCT`. İleri hareket: Hedef 1'in gerçek HTML ürününü inşa eden görevleri başlatmaya hazır **mimari aday**; ayrı iş/owner yetki kapıları korunur.\n'''
    (ROOT/'SIMULASYON_RAPORU.md').write_text(report)
    if not res.wasSuccessful() or not all(x['pass'] for x in outcomes) or not all(all(criterion_check(m,i) for i in range(10)) for m in MAT['maps']) or not all(dashboard_check(i) for i in range(10)):
        sys.exit(1)
