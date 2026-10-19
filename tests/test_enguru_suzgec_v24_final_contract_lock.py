"""ENGURU Süzgeci v2.4 technical contract freeze guard; never asserts field acceptance."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"governance/work-protocol/ENGURU_SUZGEC_V24_LANGUAGE_ALIGNMENT_CONTRACT_V1.json"
EXPECTED_STAGES=["Hakikati gör","Değeri koru","Eksikleri ve ihtiyaçları tespit et","Gerekli farkı üret","Eksikleri tamamla, ihtiyaçları karşıla","Kanıtla","Bir sonraki ihtiyaçları belirle","İlerlet"]
EXPECTED_SEQUENCE=["HEDEF","KABUL_SINIRLARI","MEVCUT_SEKIZ_ASAMA","GERCEK_KANIT","YETKILI_VERIFIED_FINISH","BITTI_DUR"]
class FinalCandidateContractLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads(PATH.read_text(encoding="utf-8"))
    def test_version_and_eight_stages(self):
        c=self.c
        self.assertEqual(c["candidateVersion"],"2.4")
        self.assertEqual(c["eightStages"],EXPECTED_STAGES)
        self.assertEqual(c["existingFinishGates"],["T01","T02","T03","T04"])
        self.assertTrue(c["eightStageGoalAcceptanceLoop"]["noNinthStage"])
        self.assertTrue(c["eightStageGoalAcceptanceLoop"]["noNewCore"])
        self.assertTrue(c["eightStageGoalAcceptanceLoop"]["noNewGate"])
    def test_final_sequence_and_goal_outcomes(self):
        c=self.c
        self.assertEqual(c["eightStageGoalAcceptanceLoop"]["finalSequence"],EXPECTED_SEQUENCE)
        self.assertEqual(c["goalOutcomeAcceptance"],["K01_GOAL_ACHIEVED","K02_SCOPE_COMPLETED","K03_RUNTIME_OPERABLE","K04_BEHAVIOR_VERIFIED","K05_EXISTING_VALUE_PRESERVED","K06_EVIDENCE_VERIFIED","K07_TECHNICAL_GATES_PASS"])
    def test_all_integrated_final_additions_exist(self):
        c=self.c
        f=c["finishVerdictStop"]
        self.assertTrue(f["noNinthStage"] and f["noNewCore"] and f["noNewFinishGate"])
        self.assertTrue(f["nestedAcceptanceStop"]["itemPackageProjectBoundariesSeparate"])
        self.assertTrue(f["passNextFlow"]["noAutomaticGrantOrSelfApproval"])
        self.assertTrue(f["nextExecutableUnifiedPackage"]["fieldArtifactBundle"]["reuseExistingProgressCoreOnly"])
        self.assertTrue(f["macOwnerPositiveOperation"]["noAutomaticGrant"])
        w=c["workProgressClosure"]
        self.assertTrue(w["noSyntheticPromotion"])
        self.assertTrue(w["noNewCore"] and w["noNinthStage"] and w["noNewFinishGate"])
        self.assertEqual(w["officialAuthority"],"HOLD_UNTIL_REAL_ISSUER_GRANT_VERIFIER_WRITER_AND_FIELD_PROOF")
    def test_language_governance_and_field_boundary(self):
        c=self.c
        self.assertEqual(c["languageRules"]["canonicalIds"],[f"L{i:02}" for i in range(1,19)])
        self.assertEqual(c["canonicalInstalledVersion"],"2.3")
        self.assertEqual(c["state"],"ENGINEERING_CANDIDATE_FIELD_ACCEPTANCE_HOLD")
        self.assertEqual(c["verifiedFinish"],"HOLD")
        self.assertEqual(c["humanThreshold"],"PENDING")
        self.assertEqual(c["surfaces"]["ChatGPT"]["preSendRuntimeHook"],"HOLD_SUPPORTED_INTEGRATION_REQUIRED")
        self.assertEqual(c["surfaces"]["Work"]["preSendRuntimeHook"],"HOLD_SUPPORTED_INTEGRATION_REQUIRED")
    def test_no_unapproved_native_claim(self):
        c=self.c
        self.assertEqual(c["sourceAuthority"],"OSi_CANONICAL")
        self.assertEqual(c["projectTechnicalFinish"],"HOLD")
        self.assertTrue(c["finishVerdictStop"]["simulatedTestsNotOfficialPass"])
        self.assertTrue(c["finishVerdictStop"]["documentsNotIssuerGrant"])
if __name__=="__main__": unittest.main()
