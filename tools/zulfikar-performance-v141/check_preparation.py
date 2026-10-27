"""Frozen T01/T02 control checker, separate from task runner."""
import hashlib,json,sys
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/'governance/enguru-suzgeci').exists() or (p/'source/governance/enguru-suzgeci').exists());src=root if (root/'governance').exists() else root/'source'
p=json.loads(Path(__file__).with_name('PLAN.json').read_text())
assert len(p['tasks'])==5 and len({x['family'] for x in p['tasks']})==5
assert [x['id'] for x in p['tasks']]==['R01','R02','R03','R04','R05']
assert p['phases']==['BASELINE','ADVERSARIAL','REPAIR_RETEST']
assert len(p['simulation'])==3 and all(x['expected'] for x in p['simulation'])
assert len(p['perTaskCriteria'])==4
assert p['sourceCommit']=='8fbd40c8fde34e7f8d77d5079c4da86a1baa8dad'
assert all(x in p['protected'] for x in ['main','PiLive PR 241','Mac OSi','canonical V3','existing DoneCheck and Human Threshold'])
for lock,field in [('ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json','canonical_path'),('ENGURU_KALICI_CALISMA_DISIPLINI_V1_LOCK.json','source_path')]:
 d=json.loads((src/'governance/enguru-suzgeci'/lock).read_text());assert hashlib.sha256((src/d[field]).read_bytes()).hexdigest()==d['sha256']
assert set(p['T01'])=={'goalIdentity','sourceInventory','ownerScope','protectedAssets','initialRisks'}
assert set(p['T02'])=={'fixedGoalContract','acceptanceIds','testAndEvidenceNeeds','dependencies','stopConditions'}
assert all(x.get('outcome') and x.get('fault') for x in p['tasks'])
assert p['executor'] and p['proof'] and p['authority'] and p['stop'] and p['dependencies']
assert (Path(__file__).with_name('run_campaign.py')).is_file() and (Path(__file__).with_name('verify_campaign.py')).is_file()
print('T01 5/5; T02 5/5; fixed criteria, 3 logical simulations, exact canonical locks: PASS_PREPARATION_ONLY')
