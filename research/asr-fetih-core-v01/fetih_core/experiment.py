"""Pure shadow planner for one preregistered synthetic A/B pretest."""
import math
import time
from .core import ValidationError

def validate(jobs,budget,resource):
    if not isinstance(jobs,list) or not 1<=len(jobs)<=100:raise ValidationError('jobs count')
    for v in (budget,resource):
        if type(v) not in (int,float) or not math.isfinite(v) or v<0:raise ValidationError('budget')
    ids=[]
    for j in jobs:
        if not isinstance(j,dict) or set(j)!={'id','duration','resource','value','dependencies'}:raise ValidationError('job shape')
        if not isinstance(j['id'],str) or not j['id']:raise ValidationError('id')
        ids.append(j['id'])
        for k in ('duration','resource','value'):
            v=j[k]
            if type(v) not in (int,float) or not math.isfinite(v) or v<0 or (k=='duration' and v==0):raise ValidationError('job number')
        if not isinstance(j['dependencies'],list) or any(not isinstance(x,str) for x in j['dependencies']):raise ValidationError('deps type')
        if len(j['dependencies'])!=len(set(j['dependencies'])):raise ValidationError('duplicate dep')
    if len(ids)!=len(set(ids)):raise ValidationError('duplicate job')
    graph={j['id']:j['dependencies'] for j in jobs};done=set();active=set()
    def visit(x):
        if x not in graph or x in active:raise ValidationError('cycle/missing dep')
        if x in done:return
        active.add(x)
        for y in graph[x]:visit(y)
        active.remove(x);done.add(x)
    for x in ids:visit(x)

def plan(jobs,budget,resource,method):
    validate(jobs,budget,resource)
    if method not in ('A','B'):raise ValidationError('method')
    start=time.perf_counter_ns();done=[];used=0;elapsed=0;value=0
    while True:
        ready=[(i,j) for i,j in enumerate(jobs) if j['id'] not in done and set(j['dependencies']).issubset(done)
               and elapsed+j['duration']<=budget and used+j['resource']<=resource]
        if not ready:break
        _,j=min(ready,key=lambda x:(x[0],) if method=='A' else (x[1]['duration'],x[0]))
        done.append(j['id']);used+=j['resource'];elapsed+=j['duration'];value+=j['value']
    # Independent feasibility scoring is in tests; output never performs the jobs.
    return {'method':method,'order':done,'goal_value':value,'planned_time_used':elapsed,
            'resource_used':used,'runtime_ns':time.perf_counter_ns()-start,
            'human_effort_seconds':None,'corrections':None,'dependency_errors':0,
            'execution':'SYNTHETIC_SHADOW_ONLY'}
