"""Trusted local audit entrypoint; no model or generated-code invocation."""
import collections
import datetime
import hashlib
import io
import json
from pathlib import Path
import platform
import unittest
import zipfile
from deterministic_verifier import review_model, repetition_metrics

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
def save(name, data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

class Result(unittest.TextTestResult):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.passed=[]
    def addSuccess(self,test):
        super().addSuccess(test)
        self.passed.append(test.id())

if __name__ == '__main__':
    log=io.StringIO()
    suite=unittest.defaultTestLoader.discover(str(OUT), pattern='test*.py')
    result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
    (OUT/'TEST_STDOUT.txt').write_text(log.getvalue())
    sources={p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir())
             if p.suffix in {'.py','.swift'} or p.name in {'cases.json','context.json'}}
    save('TEST_RECEIPT.json',dict(schema='enguru.v014.real-code-tests/v1',
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        scope='REVIEWER_AUTHORED_FIXTURE_CODE_NOT_QWEN_GENERATED_PROGRAMS_NOT_MAC',
        tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        successful=result.wasSuccessful(),passed_ids=result.passed,
        stdout_sha256=sha((OUT/'TEST_STDOUT.txt').read_bytes()),sources=sources,
        host=platform.system(),model_calls=0,swift_compile='NOT_TESTED',
        real_mac_model_exam='NOT_EXECUTED',production_integration='NOT_PERFORMED'))
    assert result.wasSuccessful(), log.getvalue()
    zpath=ROOT/'upload/ENGURU_QWEN40_V013_KANIT_20261030_204634_761315.zip'
    assert sha(zpath.read_bytes())=='4a8bb3cd3d7f450051c44e1c31c3c91c271e8a52307ef287bd821f621db03bbe'
    cases=json.loads((OUT/'cases.json').read_text())['items']
    assert sha((OUT/'cases.json').read_bytes())=='2db70257410da6fcbe31ce0d5edead0d1c3b4ab38131d976a9a368099ae11e32'
    old=json.loads((ROOT/'work_v013/context.json').read_text())
    new=json.loads((OUT/'context.json').read_text())
    assert old['task_details']==new['task_details']
    rows=[]
    with zipfile.ZipFile(zpath) as z:
        for c in cases:
            b=z.read('receipts/'+c['id']+'.json')
            r=json.loads(b)
            v=review_model(r['raw_response'],r['done_reason'])
            assert v['execution_authorized'] is False
            rows.append(dict(id=c['id'],role=c['role'],original_judge=r['judge'],
                source_receipt_sha256=sha(b),v014_verdict=v,
                eval_count=r['eval_count'],prompt_eval_count=r['prompt_eval_count'],
                repetition=repetition_metrics(r['raw_response']),done_reason=r['done_reason']))
    save('V013_REPLAY_RECEIPT.json',dict(schema='enguru.v014.offline-replay/v1',
        scope='ORIGINAL_V013_RESPONSES_NOT_NEW_MODEL_EXAM',rows=rows,
        cases=40,execution_authorized=0,professional_acceptance='HOLD',
        gates=dict(collections.Counter(r['v014_verdict']['gate'] for r in rows)),
        model_calls=0,fixtures_unchanged=True,original_case_bytes_unchanged=True))
    print('V014_REAL_CODE_TESTS=%d/%d_PASS'%(result.testsRun,result.testsRun))
    print('V013_OFFLINE_REPLAY=40/40_NON_AUTHORIZING; NOT_NEW_MODEL_EXAM')
    print('GATES',collections.Counter(r['v014_verdict']['gate'] for r in rows))
    for r in rows:
        if r['id'] in {'E-P05','E-P08'}: print(json.dumps(r,ensure_ascii=False))
