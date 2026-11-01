from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fetih_core.experiment import plan
P=Path(__file__).resolve();root=P.parents[1]
protocol=root/'experiment/protocol.json'
lock=json.loads((root/'evidence/PRE_EXECUTION_LOCK.json').read_text())
assert hashlib.sha256(protocol.read_bytes()).hexdigest()==lock['experiment/protocol.json']
def job(i,d,v=1,deps=None):return {'id':i,'duration':d,'value':v,'dependencies':deps or [],'resource':1}
cases=[{'id':'S01','jobs':[job('a',8),job('b',2),job('c',2)],'budget':8,'resource':3},
       {'id':'S02','jobs':[job('high',8,10),job('low1',2),job('low2',2)],'budget':8,'resource':3},
       {'id':'S03','jobs':[job('a',2),job('b',3,1,['a']),job('c',1)],'budget':6,'resource':3},
       {'id':'S04','jobs':[job('a',5,5),job('b',1),job('c',1)],'budget':5,'resource':1},
       {'id':'S05','jobs':[job('prereq',4),job('goal',1,10,['prereq']),job('small',2)],'budget':5,'resource':3}]
def independent_check(case, result):
    seen=set();duration=0;resource=0;value=0;errors=0
    by_id={j['id']:j for j in case['jobs']}
    for id_ in result['order']:
        if id_ not in by_id or id_ in seen: errors+=1;continue
        j=by_id[id_]
        errors+=int(not set(j['dependencies']).issubset(seen))
        seen.add(id_);duration+=j['duration'];resource+=j['resource'];value+=j['value']
    assert duration<=case['budget'] and resource<=case['resource']
    assert value==result['goal_value'] and errors==result['dependency_errors']
    return {'goal_value':value,'dependency_errors':errors,'duration':duration,'resource':resource}
results=[]
for x in cases:
 a=plan(x['jobs'],x['budget'],x['resource'],'A');b=plan(x['jobs'],x['budget'],x['resource'],'B')
 checks={'A':independent_check(x,a),'B':independent_check(x,b)}
 results.append({'case':x,'A':a,'B':b,'independent_feasibility':checks,'net_benefit':(b['goal_value']-a['goal_value'])/max(1,a['goal_value'])})
out={'protocol_sha256':lock['experiment/protocol.json'],'type':'SYNTHETIC_PRETEST','cases':results,
     'mean_net_benefit':sum(x['net_benefit'] for x in results)/len(results),
     'real_examples':0,'owner_authorization_for_real_data':None,'human_effort_seconds':None,'real_benefit_acceptance':'NOT_TESTED',
     'conclusion':'Universal superiority falsified by explicit counterexamples; shortest-first is not a general project strategy.'}
(root/'evidence/SYNTHETIC_EXPERIMENT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='cases'},ensure_ascii=False))
