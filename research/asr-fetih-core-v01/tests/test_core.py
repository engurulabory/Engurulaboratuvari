import copy,hashlib,json,pathlib,shutil,tempfile,threading,unittest,urllib.request,urllib.error
from fetih_core.core import Core,ValidationError,canonical,DATA,read_json
from fetih_core.api import Server
from fetih_core.experiment import plan

class SourceTests(unittest.TestCase):
    def setUp(self):self.c=Core()
    def test_29_verse_identity(self):self.assertEqual([v['id'] for v in self.c.verses],[f'48:{i}' for i in range(1,30)])
    def test_source_verbatim(self):
        for r in self.c.records:self.assertEqual(r['source_text'],self.c.by_verse[r['source_verse']])
    def test_determinism(self):self.assertEqual(canonical(self.c.export()),canonical(Core().export()))
    def test_graph_query(self):
        g=self.c.graph('bilgi sınırı');self.assertEqual(len(g['edges']),2)
        self.assertTrue(all('bilgi sınırı' in [e['from'],e['to']] for e in g['edges']))
    def test_unknown_graph(self):self.assertEqual(self.c.graph('<script>')['edges'],[])
    def test_human_queue(self):self.assertTrue(all(r['verification_status']=='PENDING_HUMAN_REVIEW' for r in self.c.records))
    def test_model_trace(self):
        ids={r['id'] for r in self.c.records}
        for x in self.c.models():self.assertIn(x['source_record'],ids);self.assertEqual(x['epistemic_level'],'K4')
    def test_hypothesis_trace(self):
        self.assertTrue(set(self.c.hypothesis['source_records']).issubset({r['rule_id'] for r in self.c.records}))
        self.assertIs(self.c.hypothesis['religious_truth_claim'],False)
    def test_generated_hypothesis_requires_grounding(self):
        h=self.c.hypotheses()[0]
        self.assertEqual(h['grounding_records'],['F01-R07'])
        self.c.records=[r for r in self.c.records if r['rule_id']!='R07']
        self.assertEqual(self.c.hypotheses(),[]);self.assertEqual(self.c.models(),[])
    def test_tamper_each_pinned_file(self):
        lock=read_json(DATA/'source_lock.json')
        for name in lock['files']:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as td:
                d=pathlib.Path(td)/'data';shutil.copytree(DATA,d);(d/name).write_bytes((d/name).read_bytes()+b' ')
                with self.assertRaises(ValidationError):Core(d)
    def test_missing_source(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)/'data';shutil.copytree(DATA,d);(d/'verses.json').unlink()
            with self.assertRaises(ValidationError):Core(d)
    def test_symlink_source(self):
        with tempfile.TemporaryDirectory() as td:
            d=pathlib.Path(td)/'data';shutil.copytree(DATA,d);(d/'verses.json').unlink();(d/'verses.json').symlink_to(DATA/'verses.json')
            with self.assertRaises(ValidationError):Core(d)
    def test_unsupported_interpretation(self):
        r=copy.deepcopy(self.c.records[0]);r['interpretation']='This proves a universal scheduling algorithm'
        with self.assertRaises(ValidationError):self.c.validate_record(r)
    def test_record_adversarial_mutations(self):
        bad={'confidence':[True,float('nan'),float('inf'),-1,1.01,'0.5',None],
             'source_verse':['103:1','48:0','48:30',None,25],
             'source_text':['changed','',[],None],
             'source_reference':[[],['fabricated'],None,['tanzil-uthmani-1.1','diyanet-tefsir-48','tafsir:4720']],
             'verification_status':['VERIFIED','PASS','OWNER_APPROVED',False],
             'schema_version':['2.0',1],'epistemic_level':['K1','K2','K4'],
             'rule_id':['R99','R02'],'id':['F01-R02','forged'],'concept':['unattributed'],
             'relationship_type':['causes'], 'related_concept':['arbitrary']}
        count=0
        for k,values in bad.items():
            for value in values:
                with self.subTest(k=k,value=value):
                    r=copy.deepcopy(self.c.records[0]);r[k]=value
                    with self.assertRaises(ValidationError):self.c.validate_record(r)
                    count+=1
        self.assertEqual(count,36)
    def test_extra_and_missing_fields(self):
        for k in list(self.c.records[0]):
            r=copy.deepcopy(self.c.records[0]);r.pop(k)
            with self.assertRaises(ValidationError):self.c.validate_record(r)
        r=copy.deepcopy(self.c.records[0]);r['authority']='divine'
        with self.assertRaises(ValidationError):self.c.validate_record(r)
    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'x';p.write_text('{"id":1,"id":2}')
            with self.assertRaises(ValidationError):read_json(p)
    def test_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'x';p.write_text('{"confidence":NaN}')
            with self.assertRaises(ValidationError):read_json(p)

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=Server(('127.0.0.1',0));cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def get(self,path):
        with urllib.request.urlopen(self.base+path,timeout=3) as r:return r.status,json.load(r)
    def rejected(self,path,code,**kw):
        with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(urllib.request.Request(self.base+path,**kw),timeout=3)
        self.assertEqual(cm.exception.code,code)
    def test_routes(self):
        for p in ['/health','/verses','/sources','/concepts','/graph','/models','/hypotheses','/export','/review-queue']:
            self.assertEqual(self.get(p)[0],200)
    def test_verse_query(self):self.assertEqual(self.get('/verses?id=48%3A25')[1]['text'],Core().by_verse['48:25'])
    def test_export_parity(self):self.assertEqual(self.get('/export')[1],Core().export())
    def test_repeated_request_determinism(self):self.assertEqual(self.get('/export'),self.get('/export'))
    def test_invalid_queries(self):
        for p in ['/export?promote=PASS','/graph?concept=a&concept=b','/health?id=x']:self.rejected(p,400)
    def test_missing_route_and_verse(self):
        for p in ['/missing','/../source_lock.json','/verses?id=103%3A1']:self.rejected(p,404)
    def test_no_writes(self):
        for verb in ['POST','PUT','PATCH','DELETE']:self.rejected('/concepts',405,method=verb,data=b'{}')
    def test_browser_origin_rejected(self):self.rejected('/export',403,headers={'Origin':'https://untrusted.example'})
    def test_rebinding_host_rejected(self):self.rejected('/export',403,headers={'Host':'untrusted.example'})
    def test_external_binding_rejected(self):
        with self.assertRaises(ValueError):Server(('0.0.0.0',0))
    def test_long_uri(self):self.rejected('/graph?concept='+'a'*2100,414)

class ExperimentTests(unittest.TestCase):
    def j(self,i,d,v=1,deps=None):return dict(id=i,duration=d,value=v,resource=1,dependencies=deps or [])
    def test_independent_feasibility(self):
        jobs=[self.j('a',4),self.j('b',1,3,['a']),self.j('c',2)]
        for m in ['A','B']:
            r=plan(jobs,5,3,m);seen=set();time=0;resource=0;value=0
            for id_ in r['order']:
                j=next(x for x in jobs if x['id']==id_);self.assertTrue(set(j['dependencies']).issubset(seen))
                seen.add(id_);time+=j['duration'];resource+=j['resource'];value+=j['value']
            self.assertLessEqual(time,5);self.assertLessEqual(resource,3);self.assertEqual(value,r['goal_value'])
    def test_advantage_and_counterexample(self):
        jobs=[self.j('a',8),self.j('b',2),self.j('c',2)]
        self.assertGreater(plan(jobs,8,3,'B')['goal_value'],plan(jobs,8,3,'A')['goal_value'])
        jobs[0]['value']=10
        self.assertLess(plan(jobs,8,3,'B')['goal_value'],plan(jobs,8,3,'A')['goal_value'])
    def test_cycles_and_unknown_dependencies(self):
        for jobs in [[self.j('a',1,1,['b'])],[self.j('a',1,1,['b']),self.j('b',1,1,['a'])]]:
            with self.assertRaises(ValidationError):plan(jobs,4,4,'B')
    def test_boolean_nonfinite_duplicate_rejected(self):
        for key in ['duration','value','resource']:
            for value in [True,-1,float('nan'),float('inf'),'1']:
                jobs=[self.j('a',1)];jobs[0][key]=value
                with self.assertRaises(ValidationError):plan(jobs,4,4,'B')
        with self.assertRaises(ValidationError):plan([self.j('a',1),self.j('a',1)],4,4,'B')
    def test_zero_budget(self):self.assertEqual(plan([self.j('a',1)],0,1,'B')['order'],[])
    def test_plan_does_not_mutate(self):
        jobs=[self.j('a',2),self.j('b',1)];before=copy.deepcopy(jobs);plan(jobs,4,2,'B');self.assertEqual(jobs,before)
    def test_human_time_not_fabricated(self):self.assertIsNone(plan([self.j('a',1)],2,2,'A')['human_effort_seconds'])

if __name__=='__main__':unittest.main()
