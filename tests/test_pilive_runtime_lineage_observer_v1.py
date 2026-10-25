import io,json,os,plistlib,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from tools import pilive_runtime_lineage_observer_v1 as p

def archive(name,body=b"TASK='ENGURU_MK_BRIDGE_PILOT_V1'\n",size=None):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:z.writestr(name,body)
    return out.getvalue()

class RuntimeLineageTests(unittest.TestCase):
    def test_source_constants_without_execution(self):
        raw=b"raise RuntimeError('never execute')\nTASK='PILOT'\n"
        self.assertEqual(p.constants(raw),{'TASK':'PILOT'})
    def test_archive_scope_task_preserved(self):
        r=p.zip_sources(archive('tools/enguru_mk_bridge_v1.py'))
        self.assertEqual(r[0]['scopeConstants']['TASK'],'ENGURU_MK_BRIDGE_PILOT_V1')
    def test_zip_traversal_rejected(self):
        with self.assertRaises(ValueError):p.zip_sources(archive('../tools/enguru_mk_escape.py'))
    def test_zip_symlink_rejected(self):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:
            i=zipfile.ZipInfo('tools/enguru_mk_link.py');i.external_attr=0o120777<<16;z.writestr(i,'target')
        with self.assertRaises(ValueError):p.zip_sources(out.getvalue())
    def test_zip_member_limit(self):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:
            for i in range(501):z.writestr(str(i),b'')
        with self.assertRaises(ValueError):p.zip_sources(out.getvalue())
    def test_runtime_expected_path_and_pin(self):
        with tempfile.TemporaryDirectory() as d:
            h=Path(d).resolve(strict=True);f=h/p.ROOT/'pilot/a.zip';f.parent.mkdir(parents=True);raw=archive('tools/enguru_mk_bridge_v1.py');f.write_bytes(raw)
            self.assertEqual(p.runtime_record(h,str(f),p.safe.digest(raw))['installedPinState'],'PASS_PIN_MATCH')
            self.assertEqual(p.runtime_record(h,str(f),'a'*64)['installedPinState'],'HOLD_PIN_UNVERIFIED')
    def test_runtime_outside_scope(self):
        with self.assertRaises(ValueError):p.runtime_record('/unit/home','/other/archive.zip')
    def test_runtime_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            h=Path(d).resolve(strict=True);root=h/p.ROOT;root.mkdir(parents=True);(root/'real.zip').write_bytes(archive('tools/enguru_mk_a.py'));(root/'link.zip').symlink_to(root/'real.zip')
            with self.assertRaises(OSError):p.runtime_record(h,str(root/'link.zip'))
    def test_launch_environment_not_exported(self):
        with tempfile.TemporaryDirectory() as d:
            h=Path(d).resolve(strict=True);folder=h/'Library/LaunchAgents';folder.mkdir(parents=True)
            name='com.enguru.mk.bridge.pilot-v5.plist';(folder/name).write_bytes(plistlib.dumps({'Label':name[:-6],'ProgramArguments':['/python','--cycle'],'EnvironmentVariables':{'UNRELATED_VALUE':'private-fixture-value'}}))
            result=type('R',(),{'returncode':0,'stdout':'state = running\npid = 42\nUNRELATED_VALUE = private-fixture-value\n'})()
            with patch.object(p.subprocess,'run',return_value=result):r=p.agent_record(h,name)
            self.assertNotIn('private-fixture-value',json.dumps(r));self.assertEqual(r['launchd']['fields']['pid'],'42')
    def test_names_match_only_known_namespace(self):
        with tempfile.TemporaryDirectory() as d:
            h=Path(d).resolve(strict=True);folder=h/'Library/LaunchAgents';folder.mkdir(parents=True)
            for n in ['com.enguru.mk.bridge.pilot-v5.plist','unrelated.plist']:(folder/n).write_bytes(b'')
            self.assertEqual(p.read_launch_agents(h),['com.enguru.mk.bridge.pilot-v5.plist'])
    def test_scan_symlink_and_budget(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve(strict=True);(root/'ok.py').write_bytes(b'x');(root/'alias').symlink_to(root,target_is_directory=True)
            self.assertEqual(list(p.bounded_names(root)),['ok.py'])
            with self.assertRaises(ValueError):list(p.bounded_names(root,entry_limit=1))
    def test_depth_limit_visible(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve(strict=True);(root/'deep').mkdir()
            with self.assertRaisesRegex(ValueError,'SEARCH_DEPTH_LIMIT'):list(p.bounded_names(root,depth_limit=0))

if __name__=='__main__':unittest.main()
