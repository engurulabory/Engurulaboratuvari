import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from package_io import extract_verified

def archive(files):
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:
        for n,b in files.items():z.writestr(n,b)
        z.writestr('PACKAGE_MANIFEST.json',json.dumps({'files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()}}))
    return data.getvalue()

class ArchiveTests(unittest.TestCase):
    def test_verified_package_extracts_exact_bytes_new_area_only(self):
        b=archive({'source/a.py':b'example data'})
        with tempfile.TemporaryDirectory() as d:
            target=extract_verified(b,hashlib.sha256(b).hexdigest(),Path(d)/'new')
            self.assertEqual((target/'source/a.py').read_bytes(),b'example data')
            with self.assertRaises(ValueError):extract_verified(b,hashlib.sha256(b).hexdigest(),target)
    def test_wrong_sha_does_not_create_directory(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'new'
            with self.assertRaises(ValueError):extract_verified(archive({'a':b'x'}),'0'*64,p)
            self.assertFalse(p.exists())
    def test_path_escape_is_rejected_before_write(self):
        for name in ['../outside','/absolute','a/../../outside','a\\outside']:
            b=archive({name:b'x'})
            with tempfile.TemporaryDirectory() as d:
                with self.assertRaises(ValueError):extract_verified(b,hashlib.sha256(b).hexdigest(),Path(d)/'new')
                self.assertFalse((Path(d)/'new').exists())
    def test_nonmatching_manifest_rejected(self):
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w') as z:z.writestr('x',b'changed');z.writestr('PACKAGE_MANIFEST.json',json.dumps({'files':{'x':'0'*64}}))
        b=data.getvalue()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):extract_verified(b,hashlib.sha256(b).hexdigest(),Path(d)/'new')
