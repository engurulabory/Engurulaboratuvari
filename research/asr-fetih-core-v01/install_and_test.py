#!/usr/bin/env python3
"""Isolated install + real localhost requests. No admin, no download, no prior app writes."""
from pathlib import Path
import argparse,hashlib,json,os,platform,shutil,subprocess,sys,sysconfig,tempfile,time,urllib.request,venv
ROOT=Path(__file__).resolve().parent

def integrity():
    if any(p.is_symlink() for p in ROOT.rglob('*')):raise ValueError('package symlink rejected')
    manifest=json.loads((ROOT/'SHA256_MANIFEST.json').read_text())
    files={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.relative_to(ROOT).as_posix()!='SHA256_MANIFEST.json'}
    if files!=set(manifest):raise ValueError('manifest coverage mismatch')
    for name,digest in manifest.items():
        p=ROOT/name
        if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('integrity mismatch: '+name)
    return len(manifest)

def main():
    p=argparse.ArgumentParser();p.add_argument('--target',required=True);args=p.parse_args()
    if sys.version_info<(3,10):raise SystemExit('Python 3.10+ required')
    count=integrity();target=Path(args.target).expanduser().absolute()
    # Fresh directory only; deletion/overwrite never inferred.
    target.mkdir(parents=False,exist_ok=False)
    try:
        venv.create(target/'venv',with_pip=False)
        py=target/'venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        purelib=Path(subprocess.check_output([str(py),'-I','-c','import sysconfig; print(sysconfig.get_path("purelib"))'],text=True).strip())
        shutil.copytree(ROOT/'fetih_core',purelib/'fetih_core',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        verify=subprocess.run([str(py),'-I','-B','-m','fetih_core','verify'],capture_output=True,text=True,check=True)
        suite=subprocess.run([str(py),'-I','-B','-m','unittest','discover','-s',str(ROOT/'tests'),'-v'],capture_output=True,text=True)
        (target/'test_log.txt').write_text(suite.stdout+suite.stderr)
        if suite.returncode:raise RuntimeError('tests failed; see test_log.txt')
        out=target/'export.json';subprocess.run([str(py),'-I','-B','-m','fetih_core','export','--output',str(out)],check=True,capture_output=True)
        # Start installed package in a separate process, OS-selected port, real TCP socket.
        ready=target/'ready.txt'
        script='from fetih_core.api import Server; from pathlib import Path; s=Server(("127.0.0.1",0)); Path('+repr(str(ready))+').write_text(str(s.server_port)); s.serve_forever()'
        server=subprocess.Popen([str(py),'-I','-B','-c',script],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        requests=[]
        try:
            for _ in range(100):
                if ready.exists():break
                if server.poll() is not None:raise RuntimeError(server.communicate()[1].decode())
                time.sleep(.05)
            if not ready.exists():raise RuntimeError('server start timeout')
            port=int(ready.read_text())
            for route in ['/health','/verses?id=48%3A25','/concepts','/graph','/models','/hypotheses','/review-queue','/export']:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}'+route,timeout=5) as r:
                    b=r.read();value=json.loads(b);requests.append({'route':route,'status':r.status,'sha256':hashlib.sha256(b).hexdigest()})
                    if route=='/export':
                        if b+b'\n'!=out.read_bytes():raise RuntimeError('CLI/API mismatch')
        finally:
            server.terminate()
            try:server.wait(timeout=5)
            except subprocess.TimeoutExpired:server.kill();server.wait()
        receipt={'status':'PASS','scope':'ISOLATED_INSTALL_AND_LOCALHOST_RUNTIME','platform':platform.platform(),'python':sys.version,
                 'source_code_sha256':{f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'fetih_core').rglob('*')) if f.is_file() and '__pycache__' not in f.parts},'tested_manifest_sha256':hashlib.sha256((ROOT/'SHA256_MANIFEST.json').read_bytes()).hexdigest(),'manifest_files':count,'source_verify':json.loads(verify.stdout),'tests_exit_code':suite.returncode,
                 'requests':requests,'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
                 'human_effort_seconds':None,'real_benefit':'NOT_TESTED','mac_field':'PASS_RUNTIME_ONLY' if sys.platform=='darwin' else 'NOT_TESTED',
                 'rollback':'Remove only this newly created target directory after retaining receipts. Source package and old projects remain separate.'}
        (target/'RUNTIME_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'status':'PASS','receipt':str(target/'RUNTIME_RECEIPT.json'),'serve':[str(py),'-I','-B','-m','fetih_core','serve']},ensure_ascii=False))
    except BaseException:
        print('Installation evidence retained at '+str(target),file=sys.stderr);raise
if __name__=='__main__':main()
