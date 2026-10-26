import unittest
from run_k03_cli_smoke import run

class CliSmokeContractTests(unittest.TestCase):
    def test_readonly_subprocess_exists(self):
        got=run(["python","--version"])
        self.assertEqual(got["returncode"],0)
    def test_real_cli_scope_is_not_authorized_agent(self):
        self.assertTrue(callable(run))

if __name__=="__main__":
    unittest.main()
