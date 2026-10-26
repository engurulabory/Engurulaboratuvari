"""Materialize byte-pinned existing source into a disposable Git checkout, with explicit patch."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent

def prepare(task,repo,repaired=False):
 src=HERE/'upstream'/('harvest' if task=='S03' else 'core');shutil.copytree(src,repo,dirs_exist_ok=True)
 # Do not copy previous experiments or generated state; these inputs are vendored immutable bytes.
 if repaired:
  patch=HERE/'patches'/f'{task}.patch'
  subprocess.run(['git','apply',str(patch)],cwd=repo,check=True,capture_output=True)
 for args in [('init','-q'),('config','user.name','ENGURU disposable test'),('config','user.email','disposable@localhost'),('add','.'),('commit','-qm','Isolated existing-source test checkout; no owner acceptance')]:
  subprocess.run(['git',*args],cwd=repo,check=True,capture_output=True)
 return subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
if __name__=='__main__':print(prepare(sys.argv[1],Path(sys.argv[2]).resolve(),len(sys.argv)>3 and sys.argv[3]=='repaired'))
