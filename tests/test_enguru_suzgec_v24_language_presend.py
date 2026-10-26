"""v2.4 D01–D05 counter-tests; no producer or human acceptance claims."""
from __future__ import annotations
import importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'tools/enguru_suzgec_v24_language_presend.py'
spec=importlib.util.spec_from_file_location('v24pre',PATH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class LanguageV24Tests(unittest.TestCase):
    def test_D01_schema_and_fixed_worklist(self):
        c=mod.load_contract(ROOT)
        self.assertEqual(c['candidateVersion'],'2.4')
        self.assertEqual(len(c['languageRules']['canonicalIds']),18)
        self.assertEqual(len(c['engineeringWorklist']),5)
    def test_D01_preserve_8_stages_4_gates(self):
        c=mod.load_contract(ROOT)
        self.assertEqual(len(c['eightStages']),8)
        self.assertEqual(c['existingFinishGates'],['T01','T02','T03','T04'])
    def test_D02_change_preservation_negative(self):
        o=mod.inspect('Bu kod kaynakları değiştirmez.',ROOT)
        self.assertEqual(o['state'],'HOLD')
        self.assertIn('POSITIVE_PRESERVE',[x['rule'] for x in o['findings']])
    def test_D02_dokunmaz_negative(self):
        o=mod.inspect('Bu araç dosyalara dokunmaz.',ROOT)
        self.assertIn('POSITIVE_PRESERVE',[x['rule'] for x in o['findings']])
    def test_D02_pass_degil_negative(self):
        o=mod.inspect('Bu karar PASS değil.',ROOT)
        self.assertIn('CANONICAL_HOLD',[x['rule'] for x in o['findings']])
    def test_D02_positive_preservation(self):
        o=mod.inspect('Bu uygulama mevcut kaynak bütünlüğünü korur.',ROOT)
        self.assertEqual(o['state'],'PASS_SCOPED_DRAFT_LANGUAGE_GATE')
        self.assertEqual(o['verifiedFinish'],'HOLD')
    def test_D03_existing_linter_reused(self):
        o=mod.inspect('Mevcut kaynakları korur.',ROOT)
        self.assertIn('L13',o['checkedRuleIds'])
        self.assertTrue(o['canonicalLinterSha256'])
    def test_D03_linter_rejects_missing_evidence(self):
        o=mod.inspect('STATE=PASS',ROOT)
        self.assertEqual(o['state'],'HOLD')
    def test_D03_no_linter_holds(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'governance/work-protocol').mkdir(parents=True)
            (r/mod.CONTRACT).write_bytes((ROOT/mod.CONTRACT).read_bytes())
            o=mod.inspect('Kaynakları korur.',r)
            self.assertEqual(o['reason'],'CANONICAL_LINTER_MISSING')
    def test_D03_wrong_linter_sha_holds(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d);(r/'governance/work-protocol').mkdir(parents=True);(r/'tools').mkdir()
            (r/mod.CONTRACT).write_bytes((ROOT/mod.CONTRACT).read_bytes())
            (r/'tools/enguru_language_pre_send_linter.py').write_text('malicious=True')
            o=mod.inspect('Kaynakları korur.',r)
            self.assertEqual(o['reason'],'CANONICAL_LINTER_SOURCE_DRIFT')
    def test_D04_excluded_quote(self):
        o=mod.inspect('> Kaynakları değiştirmez.\n\nKaynak bütünlüğünü korur.',ROOT)
        self.assertEqual(o['state'],'PASS_SCOPED_DRAFT_LANGUAGE_GATE')
    def test_D04_excluded_fenced_code(self):
        o=mod.inspect('```python\nprint("değiştirmez")\n```\nMevcut kaynakları korur.',ROOT)
        self.assertEqual(o['state'],'PASS_SCOPED_DRAFT_LANGUAGE_GATE')
    def test_D04_existing_linter_risk_first(self):
        o=mod.inspect('Bunu bozmadan kullan.',ROOT)
        self.assertEqual(o['state'],'HOLD')
    def test_D04_empty_input_hold(self):
        self.assertEqual(mod.inspect('',ROOT)['reason'],'EMPTY_DRAFT')
    def test_D05_all_surfaces_tech_finish_hold(self):
        for surface in ('OSi','ChatGPT','Work'):
            o=mod.inspect('Kaynakları korur.',ROOT,surface)
            self.assertEqual(o['verifiedFinish'],'HOLD')
            self.assertEqual(o['crossSurfaceAcceptance'],'HOLD')
            self.assertEqual(o['state'],'PASS_SCOPED_DRAFT_LANGUAGE_GATE')
    def test_D05_unsupported_surface(self):
        self.assertEqual(mod.inspect('Kaynakları korur.',ROOT,'UNKNOWN')['reason'],'UNSUPPORTED_SURFACE')
    def test_D05_precheck_cannot_be_forged(self):
        c=mod.load_contract(ROOT)
        self.assertEqual(c['surfaces']['ChatGPT']['preSendRuntimeHook'],'HOLD_SUPPORTED_INTEGRATION_REQUIRED')
        self.assertEqual(c['surfaces']['Work']['preSendRuntimeHook'],'HOLD_SUPPORTED_INTEGRATION_REQUIRED')
    def test_D05_donecheck_scope_preserved(self):
        c=mod.load_contract(ROOT)
        self.assertEqual(c['externalDependencies']['v23AuthorizedDoneCheck'],'HOLD_UNBOUND_V07_A10_ONLY')
        self.assertEqual(c['p01'],'SUSPENDED')
        self.assertEqual(c['verifiedFinish'],'HOLD')

if __name__=='__main__':unittest.main()
