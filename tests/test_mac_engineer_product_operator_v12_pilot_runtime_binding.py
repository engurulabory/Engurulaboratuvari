import unittest

from tools.mac_engineer_product_operator_v12_pilot_runtime_binding import (
    resolve_pilot_execution,
)


class ProductOperatorV12PilotRuntimeBindingTests(unittest.TestCase):

    def test_unknown_pilot_holds(self):
        result = resolve_pilot_execution(
            work_id="W1",
            pilot_id="UNKNOWN",
            capability_id="BUILD",
            producer_id="FORGE",
            verifier_id="SENTINEL",
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["reason"], "UNKNOWN_PILOT")

    def test_zeku_cannot_inherit_unassigned_build(self):
        result = resolve_pilot_execution(
            work_id="W1",
            pilot_id="ZEKU",
            capability_id="BUILD",
            producer_id="FORGE",
            verifier_id="SENTINEL",
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(
            result["reason"],
            "PILOT_CAPABILITY_NOT_APPROVED",
        )

    def test_producer_verifier_collision_holds(self):
        result = resolve_pilot_execution(
            work_id="W1",
            pilot_id="ZEKU",
            capability_id="CURRENT_TECHNICAL_TRUTH_READ",
            producer_id="ZEKU",
            verifier_id="ZEKU",
        )
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(
            result["reason"],
            "PRODUCER_VERIFIER_COLLISION",
        )

    def test_read_only_capability_inherits_graph_authority(self):
        result = resolve_pilot_execution(
            work_id="W1",
            pilot_id="ZEKU",
            capability_id="CURRENT_TECHNICAL_TRUTH_READ",
            producer_id="ZEKU",
            verifier_id="SENTINEL",
        )

        self.assertEqual(result["state"], "PASS")

        execution = result["execution"]

        self.assertEqual(
            execution["AUTHORITY"],
            "GREEN",
        )

        self.assertEqual(
            execution["BINDING_TYPE"],
            "DIRECT_RUNTIME",
        )

        self.assertFalse(
            execution["EXECUTION_AUTHORITY_CREATED"]
        )

    def test_forge_build_resolves_existing_registered_action(self):
        result = resolve_pilot_execution(
            work_id="W2",
            pilot_id="FORGE",
            capability_id="BUILD",
            producer_id="FORGE",
            verifier_id="SENTINEL",
        )

        self.assertEqual(result["state"], "PASS")

        execution = result["execution"]

        self.assertEqual(
            execution["BINDING_TYPE"],
            "REGISTERED_ACTION",
        )

        self.assertTrue(execution["ACTION"])
        self.assertTrue(execution["HANDLER"])

        self.assertFalse(
            execution["EXECUTION_AUTHORITY_CREATED"]
        )

    def test_material_mutation_requires_single_writer_owner(self):
        result = resolve_pilot_execution(
            work_id="W3",
            pilot_id="FORGE",
            capability_id="ROOT_CAUSE_REPAIR",
            producer_id="FORGE",
            verifier_id="SENTINEL",
        )

        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(
            result["reason"],
            "SINGLE_WRITER_OWNER_REQUIRED",
        )

    def test_material_mutation_rejects_writer_mismatch(self):
        result = resolve_pilot_execution(
            work_id="W3",
            pilot_id="FORGE",
            capability_id="ROOT_CAUSE_REPAIR",
            producer_id="FORGE",
            verifier_id="SENTINEL",
            writer_owner="ZEKU",
        )

        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(
            result["reason"],
            "SINGLE_WRITER_OWNER_MISMATCH",
        )

    def test_forge_repair_handoff_preserves_scope_and_separation(self):
        result = resolve_pilot_execution(
            work_id="W3",
            pilot_id="FORGE",
            capability_id="ROOT_CAUSE_REPAIR",
            producer_id="FORGE",
            verifier_id="SENTINEL",
            writer_owner="FORGE",
        )

        self.assertEqual(result["state"], "PASS")

        handoff = result["handoff"]

        self.assertEqual(handoff["WORK_ID"], "W3")
        self.assertEqual(handoff["PILOT"], "FORGE")
        self.assertEqual(
            handoff["CAPABILITY"],
            "ROOT_CAUSE_REPAIR",
        )

        self.assertNotEqual(
            handoff["PRODUCER"],
            handoff["VERIFIER"],
        )

        self.assertFalse(
            result["execution"]["EXECUTION_AUTHORITY_CREATED"]
        )


if __name__ == "__main__":
    unittest.main()
