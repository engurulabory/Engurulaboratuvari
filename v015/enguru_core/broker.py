"""Closed tool gateway: executes only release-pinned, reviewer-authored fixtures.

This is NOT a sandbox for arbitrary Python. Model code is never submitted here.
No shell interpretation or tools supplied by model/user text are supported.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from .contracts import Rejected, file_sha, digest, encoded
from .storage import read_private, write_new, private_root

RELEASE = Path(__file__).resolve().parents[1]


def fixture_pin():
    return digest({n:file_sha(RELEASE/'fixtures'/n) for n in
                  ('unique_jobs_broken.py','unique_jobs_fixed.py','test_unique_jobs.py')})


def checked_fixture(name):
    manifest=json.loads((RELEASE/'SOURCE_MANIFEST.json').read_text())
    path=RELEASE/'fixtures'/name
    if file_sha(path)!=manifest['files']['fixtures/'+name]:raise Rejected('FIXTURE_SOURCE_DRIFT')
    return path.read_bytes()


def run_tests(directory):
    """Only trusted harness with fixed file names and known source can reach this."""
    harness=checked_fixture('test_unique_jobs.py')
    # -I/-S drops PYTHONPATH, site packages and cwd. Bootstrap adds only the owned
    # fixture directory to load known unique_jobs; no model output is imported.
    bootstrap=('import sys,runpy;sys.path.insert(0,sys.argv[1]);'
               'sys.argv=[sys.argv[2]];runpy.run_path(sys.argv[0],run_name="__main__")')
    p=subprocess.run([sys.executable,'-I','-S','-B','-c',bootstrap,str(directory),
                      str(directory/'test_unique_jobs.py')],cwd=directory,
                     env={'PATH':os.defpath,'PYTHONHASHSEED':'0'},
                     capture_output=True,timeout=30)
    return dict(exit_code=p.returncode,stdout=p.stdout.decode('utf-8','replace'),
                stderr=p.stderr.decode('utf-8','replace'),test_sha256=hashlib.sha256(harness).hexdigest())


class Broker:
    def __init__(self,profile,authority):self.profile=profile;self.authority=authority

    def execute(self,plan,command):
        if plan.source!=fixture_pin():raise Rejected('SOURCE_SHA_MISMATCH')
        # command is an opaque caller ID; digest prevents path traversal.
        workspace=private_root(self.profile/'jobs')/digest(command)
        if workspace.exists() or workspace.is_symlink():raise Rejected('EXISTING_WORKSPACE_HOLD')
        workspace.mkdir(mode=0o700)
        broken=checked_fixture('unique_jobs_broken.py');fixed=checked_fixture('unique_jobs_fixed.py')
        tests=checked_fixture('test_unique_jobs.py')
        source=workspace/'unique_jobs.py'
        write_new(source,broken);write_new(workspace/'test_unique_jobs.py',tests)
        red=run_tests(workspace)
        if red['exit_code']==0:raise Rejected('RED_WITNESS_NOT_REPRODUCED')
        # Preserve broken source, install known patch through a new regular file.
        os.rename(source,workspace/'unique_jobs.before.py')
        write_new(source,fixed)
        green=run_tests(workspace)
        operation=dict(command=command,task=plan.task,plan=plan.sha,source=plan.source,
           scope=plan.scope,operation='pilot.unique_jobs',workspace=str(workspace),
           output_sha256=file_sha(source),harness_sha256=file_sha(workspace/'test_unique_jobs.py'),
           red=red,green=green,created_ns=time.time_ns())
        receipt={'operation':operation,'signature':self.authority.sign(operation)}
        write_new(workspace/'operation.json',encoded(receipt))
        return receipt


class Verifier:
    """Distinct code path; trusts only broker signature + exact files/test results."""
    def __init__(self,profile,authority):self.profile=profile;self.authority=authority

    def verify(self,receipt,plan,command,*,rerun=True):
        import hmac
        if not isinstance(receipt,dict) or set(receipt)!={'operation','signature'}:raise Rejected('RECEIPT_FORMAT')
        op=receipt['operation']
        if not isinstance(op,dict) or not isinstance(receipt['signature'],str):raise Rejected('RECEIPT_FORMAT')
        if not hmac.compare_digest(self.authority.sign(op),receipt['signature']):raise Rejected('FORGED_RECEIPT')
        expected={'command':command,'task':plan.task,'plan':plan.sha,'source':plan.source,
                  'scope':plan.scope,'operation':'pilot.unique_jobs',
                  'workspace':str(self.profile/'jobs'/digest(command))}
        if any(op.get(k)!=v for k,v in expected.items()):raise Rejected('RECEIPT_BINDING')
        if plan.source!=fixture_pin():raise Rejected('STALE_RECEIPT_SOURCE')
        w=Path(expected['workspace'])
        if read_private(w/'unique_jobs.py')!=checked_fixture('unique_jobs_fixed.py'):
            raise Rejected('OUTPUT_DRIFT')
        if read_private(w/'test_unique_jobs.py')!=checked_fixture('test_unique_jobs.py'):
            raise Rejected('TEST_TAMPER')
        if op.get('output_sha256')!=file_sha(w/'unique_jobs.py') or op.get('harness_sha256')!=file_sha(w/'test_unique_jobs.py'):
            raise Rejected('RECEIPT_FILE_HASH')
        red,green=op.get('red',{}),op.get('green',{})
        if type(red.get('exit_code')) is not int or red['exit_code']==0:raise Rejected('NO_RED')
        if type(green.get('exit_code')) is not int or green['exit_code']!=0:raise Rejected('TEST_FAILED')
        # Independently rerun the immutable harness: signed text alone isn't PASS.
        independent=run_tests(w) if rerun else None
        if not rerun:
            return dict(command=command,task=plan.task,plan=plan.sha,source=plan.source,
                        output_sha256=op['output_sha256'],receipt_sha256=digest(receipt))
        if independent['exit_code']!=0 or 'Ran 4 tests' not in independent['stderr'] or '\nOK\n' not in independent['stderr']:
            raise Rejected('INDEPENDENT_TEST_FAILED')
        return dict(command=command,task=plan.task,plan=plan.sha,source=plan.source,
                    output_sha256=op['output_sha256'],receipt_sha256=digest(receipt),
                    independent_test=independent,verifier='enguru.deterministic.v015/1')
