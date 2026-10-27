from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.enguru_evidence_receipt_io import write_new_json
from tools import enguru_p06_runtime_task_adapter as native
from tools import enguru_steward_operator as steward

class TestP06ReceiptOutputAuthority(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='p06-evidence-guard-')
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.root = self.home/'Enguru'/'Evidence'/'MacEngineer'
        self.root.mkdir(parents=True)

    def write(self, path):
        return write_new_json(path, {'state':'PASS'}, evidence_root=self.root)

    def test_evidence_writes_new_file(self):
        dest = self.root/'P06'/'test'/'receipt.json'
        self.assertEqual(self.write(dest), dest)
        self.assertEqual(json.loads(dest.read_text())['state'], 'PASS')

    def test_existing_receipt_is_immutable(self):
        dest = self.root/'P06'/'receipt.json'
        dest.parent.mkdir()
        dest.write_text('existing receipt')
        with self.assertRaises(FileExistsError): self.write(dest)
        self.assertEqual(dest.read_text(), 'existing receipt')

    def test_canonical_source_outside_evidence_rejected(self):
        dest = self.home/'Enguru'/'Projects'/'Engurulaboratuvari'/'SESSION_STATE_V1.json'
        with self.assertRaisesRegex(ValueError,'OUT_OF_SCOPE'): self.write(dest)
        self.assertFalse(dest.exists())

    def test_directory_escape_rejected(self):
        dest = self.root/'P06'/'..'/'safe.json'
        with self.assertRaisesRegex(ValueError,'TRAVERSAL'): self.write(dest)

    def test_symlink_directory_rejected(self):
        other = self.home/'outside'; other.mkdir()
        (self.root/'P06').symlink_to(other, target_is_directory=True)
        with self.assertRaises(OSError): self.write(self.root/'P06'/'receipt.json')
        self.assertFalse((other/'receipt.json').exists())

    def test_symlink_final_rejected(self):
        dest = self.root/'P06'/'receipt.json'
        dest.parent.mkdir()
        original = self.home/'sentinel'; original.write_text('keep')
        dest.symlink_to(original)
        with self.assertRaises(FileExistsError): self.write(dest)
        self.assertEqual(original.read_text(), 'keep')

    def test_raw_relative_path_rejected(self):
        with self.assertRaisesRegex(ValueError,'ABSOLUTE'): self.write(Path('tmp/receipt.json'))

    def test_native_invalid_task_receipt_fails_closed_at_output_path(self):
        wrong = self.home/'Enguru'/'Projects'/'Engurulaboratuvari'/'canonical.json'
        task = self.home/'bad-task.json'; task.write_text('{}')
        with patch.object(native, 'write_new_json', side_effect=lambda p,d: write_new_json(p,d,evidence_root=self.root)):
            with self.assertRaisesRegex(ValueError,'OUT_OF_SCOPE'):
                native.main([str(task),str(wrong)])
        self.assertFalse(wrong.exists())

    def test_steward_output_uses_shared_guard(self):
        wrong = self.home/'Enguru'/'Runtime'/'MacEngineer'/'state'/'acceptance.json'
        with patch.object(steward, 'write_new_json', side_effect=lambda p,d: write_new_json(p,d,evidence_root=self.root)):
            with self.assertRaisesRegex(ValueError,'OUT_OF_SCOPE'):
                steward.atomic_json(wrong,{'state':'PASS'})
        self.assertFalse(wrong.exists())

    def test_legacy_task_shim_preserved_general_path_held(self):
        from tools import enguru_p06_pilot_handler_adapter as legacy
        self.assertTrue((Path(__file__).resolve().parents[1]/'tools/enguru_p06_pilot_handler_adapter.py').is_file())
        with self.assertRaisesRegex(ValueError,'P06_LEGACY_ACTION_BINDING_SOURCE_UNAVAILABLE'):
            legacy.qualify()

    def test_legacy_registered_action_missing_command_explicit_hold(self):
        from tools import enguru_p06_pilot_handler_adapter as legacy
        gov=self.home/'mock-repo'/'governance'/'mac-engineer';gov.mkdir(parents=True)
        base=gov.parents[1]
        c={ 'capabilityRegistry':'governance/mac-engineer/caps.json',
            'actionRegistry':'governance/mac-engineer/actions.json',
            'actionBinding':'governance/mac-engineer/bind.json',
            'profiles':[{'PILOT_ID':name,'CAPABILITY_IDS':['CAP']} for name in legacy.PILOTS] }
        (gov/'contract.json').write_text(json.dumps(c))
        (gov/'caps.json').write_text('{}')
        (gov/'bind.json').write_text('{}')
        (gov/'actions.json').write_text(json.dumps({'actions':{
            'ACTION':{'command':'governance/mac-engineer/missing.command','authority':'EXPLICIT'}}}))
        (gov/'CAPABILITY_EXECUTION_BINDING_V1.json').write_text(json.dumps({
            'bindings':[{'CAPABILITY_ID':'CAP','ACTION':'ACTION'}]}))
        with patch.object(legacy,'CONTROL',base),patch.object(legacy,'GOV',gov),patch.object(legacy,'CONTRACT',gov/'contract.json'):
            mapped=legacy.qualify()
        self.assertEqual(set(mapped),set(legacy.PILOTS))
        for pilot in legacy.PILOTS:
            self.assertEqual(mapped[pilot]['capabilities'][0]['state'],
                             'HOLD_REGISTERED_ACTION_SOURCE_MISSING')

if __name__ == '__main__': unittest.main()
