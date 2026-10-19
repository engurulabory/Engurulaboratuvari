import unittest
from tools.enguru_suzgec_v24_recovery_fixture import run_recovery_fixture

class RecoveryFixtureTests(unittest.TestCase):
    def test_actual_kill_and_idempotent_resume(self):
        r=run_recovery_fixture()
        self.assertEqual(r["state"],"PASS_FIXTURE_INTERRUPTION_RECOVERY")
        self.assertEqual(r["resume_runs"],2)
        self.assertEqual(r["scope"],"TEMP_FIXTURE_ONLY")

if __name__=="__main__": unittest.main()
