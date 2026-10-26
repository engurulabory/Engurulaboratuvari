"""Existing DOM engine, exact pinned bytes, disposable PiLive wire recovery proof.

This qualifies a local adapter rehearsal; it cannot close PiLive T01 or P02.
"""
import base64,hashlib,json,sys,tempfile,types,subprocess
from pathlib import Path
PIN='aae470e41a59de981c0c34b81a25ed094f52db6eed8dc0d101124984dd903230'

def qualify(method_file):
    raw=Path(method_file).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('HOLD_DOM_SOURCE_SHA')
    module=types.ModuleType('pilive_pinned_dom');module.__file__=str(method_file);sys.modules[module.__name__]=module
    exec(compile(raw,str(method_file),'exec'),module.__dict__)
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
    from test_pilive_screen_wire_v1 import native_model
    from tools.pilive_screen_wire_v1 import export_wire
    source=Path(__file__).resolve().parents[1]/'tools/pilive_screen_wire_v1.py'
    good=export_wire(native_model());broken=json.loads(good);broken['snapshot']['projects'][10]['done']=9
    start={'wire':base64.b64encode(json.dumps(broken).encode()).decode()}
    contract=module.Contract('ENGURU_PLIVE_P02_USER_SCREEN.DOM_WIRE_REHEARSAL','Existing PiLive wire repair qualification only','T01',('exact_wire','p02_count','official_hold'),hashlib.sha256(source.read_bytes()).hexdigest())
    def assess(state,_):
        wire=base64.b64decode(state['wire']);doc=json.loads(wire);rows=doc['snapshot']['projects']
        p02=next(r for r in rows if r['key']=='plive-p02-user-screen')
        return {'exact_wire':wire==good,'p02_count':p02['done']==0 and p02['total']==12,'official_hold':all(r['officialAcceptance']=='HOLD' and not r['closed'] for r in rows)}
    def repair(state,missing,_):return {'wire':base64.b64encode(good).decode()}
    rounds=[]
    for index in range(3):
        with tempfile.TemporaryDirectory(prefix='pilive-dom-wire-') as folder:
            folder=Path(folder).resolve();artifact=folder/'real-test-output.txt'
            def test(state,_):
                p=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_pilive_live_reader_v1.py','-q'],cwd=source.parents[1],capture_output=True,timeout=45)
                artifact.write_bytes(p.stdout+p.stderr)
                return {'processObserved':True,'exitCode':p.returncode,'scope':'LOCAL_DISPOSABLE_PROOF','artifactSha256':hashlib.sha256(artifact.read_bytes()).hexdigest()}
            def verify(state,c,result):return hashlib.sha256(artifact.read_bytes()).hexdigest()==result['artifactSha256'] and b'Ran 5 tests' in artifact.read_bytes() and all(assess(state,c).values())
            result=module.execute(contract,start,module.LocalJournal(folder),lambda s,c:{'valid':True},assess,repair,test,verify,lambda c:hashlib.sha256(source.read_bytes()).hexdigest()==c['sourcePin'],source_file=source,max_rounds=3)
            if result['state']!='STAGE_100_CANDIDATE_EXTERNAL_REVIEW_REQUIRED' or result['stagePassIssued'] or result['acceptedScore'] is not None:raise ValueError('HOLD_DOM_QUALIFICATION')
            rounds.append({'cycle':index+1,'realSubprocessTests':5,'state':result['state'],'journalHeadSha256':result['journalHeadSha256'],'diagnostic':result['diagnostic'],'officialStagePass':False})
    return {'schema':'enguru.pilive.dom-wire-qualification/v1','methodSourceSha256':PIN,'scope':'DISPOSABLE_WIRE_RECOVERY_ADAPTER_ONLY_NOT_PILIVE_T01_ACCEPTANCE','rounds':rounds,'canonicalWrites':0,'productAcceptance':'HOLD','verifiedFinish':'HOLD'}

if __name__=='__main__':print(json.dumps(qualify(sys.argv[1]),sort_keys=True))
