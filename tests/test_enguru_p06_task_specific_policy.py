import unittest
from tools import enguru_p06_task_specific_policy as p
class TestP06TaskSpecificPolicy(unittest.TestCase):
    def test_seven_distinct_objectives(self):
        self.assertEqual(len(p.POLICY),7)
        self.assertEqual(len({p.objective(x) for x in p.POLICY}),7)
    def test_unknown_pilot_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'UNQUALIFIED_PILOT'):
            p.objective('SPOOF')
    def test_all_valid_task_result_shapes(self):
        for name,(intent,op,fields) in p.POLICY.items():
            with self.subTest(name=name):
                obj={'operation':op}
                for field in fields:
                    obj[field]=False if field=='externalNetworkUsed' else (7 if field=='profileCount' else
                        {'control':'a'*40,'product':'b'*40} if field=='heads' else
                        [] if field in ('functions','classes') else 'f'*64)
                self.assertTrue(p.qualify_native_result(name,obj,{'PILOT_ID':name}))
    def test_each_wrong_operation_rejected(self):
        for name,(_,op,fields) in p.POLICY.items():
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'TASK_NATIVE_OPERATION_MISMATCH'):
                p.qualify_native_result(name,{'operation':'ANOTHER_HANDLER'},{'PILOT_ID':name})
    def test_each_missing_field_rejected(self):
        for name,(_,op,fields) in p.POLICY.items():
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'TASK_NATIVE_EVIDENCE_GAP'):
                p.qualify_native_result(name,{'operation':op},{'PILOT_ID':name})
    def test_pilot_profile_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'TASK_PROFILE_BINDING'):
            p.qualify_native_result('ATLAS',{'operation':'ARCHITECTURE_AST_REVIEW'},{'PILOT_ID':'ZEKU'})
    def test_astra_network_rejected(self):
        with self.assertRaisesRegex(ValueError,'TASK_NATIVE_NETWORK_AUTHORITY'):
            p.qualify_native_result('ASTRA',{'operation':'OFFLINE_CAPABILITY_PROVENANCE',
                'registrySha256':'e'*64,'externalNetworkUsed':True},{'PILOT_ID':'ASTRA'})
    def test_canonical_general_authority_remains_hold(self):
        from tools import enguru_p06_runtime_task_adapter as r
        text=(r.ROOT/'tools/enguru_p06_runtime_task_adapter.py').read_text()
        self.assertIn("'canonicalPilotAccepted':False",text)
        self.assertIn("'generalTaskExecutionAuthorized':False",text)
