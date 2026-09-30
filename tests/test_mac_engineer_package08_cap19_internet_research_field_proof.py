from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import mac_engineer_package08_cap19_internet_research_harvest_astra_field_proof as cap19


MISSING = object()


class Capability19FieldProofTests(unittest.TestCase):
    @staticmethod
    def provider_chat_result(output):
        captured = {}

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                payload = {
                    "state": "PASS",
                    "route_evidence": {"provider": "local_runtime"},
                }
                if output is not MISSING:
                    payload["output"] = output
                return json.dumps(payload).encode()

        def open_request(request, timeout):
            captured["payload"] = json.loads(request.data.decode())
            captured["timeout"] = timeout
            return Response()

        with patch.object(cap19.urllib.request, "urlopen", side_effect=open_request):
            result = cap19.provider_chat("bounded capsule")
        return result, captured

    @staticmethod
    def fetcher(url: str) -> dict:
        if "iana.org" in url:
            body = b"IANA example domains include example.com and example.org for documentation."
        else:
            body = b"RFC 2606 Reserved Top Level DNS Names includes example.com."
        return {"status": 200, "finalUrl": url, "contentType": "text/plain", "body": body}

    @staticmethod
    def provider(_capsule: str) -> dict:
        return {
            "output": (
                "SOURCED_FACTS: example.com is reserved for examples "
                "[IANA_EXAMPLE_DOMAINS]; RFC 2606 governs the reservation [RFC2606].\n"
                "INTERPRETATION: the reserved names provide safe documentation examples."
            ),
            "routeEvidence": {
                "provider": "local_runtime",
                "model": "qwen3:14b",
                "reason": "verified_execution",
            },
            "attempts": 1,
        }

    def test_bounded_fresh_field_proof_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "capability-19"
            result = cap19.execute_field_proof(root, self.fetcher, self.provider)
            seal_path = Path(result["sealPath"])
            self.assertTrue(seal_path.is_file())
            seal = json.loads(seal_path.read_text(encoding="utf-8"))
            self.assertEqual(seal["state"], "PASS")
            self.assertTrue(all(seal["acceptance"].values()))
            self.assertTrue(seal["execution"]["networkAccessPerformed"])
            self.assertFalse(seal["execution"]["networkMutation"])
            self.assertFalse(seal["execution"]["generalBrowserAuthority"])
            self.assertEqual(seal["provider"], "local_runtime")
            self.assertEqual(seal["model"], "qwen3:14b")
            self.assertEqual(len(seal["sourceBindings"]), 2)
            self.assertTrue(all(item["url"] and item["sha256"] for item in seal["sourceBindings"]))
            donecheck = json.loads(
                Path(seal["mandatoryDoneCheck"]["path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(donecheck["criterionCount"], len(cap19.DONECHECK_CRITERIA))
            self.assertTrue(all(item["state"] == "PASS" for item in donecheck["criteria"].values()))
            field = json.loads(
                Path(seal["fieldEvidence"]["path"]).read_text(encoding="utf-8")
            )
            self.assertTrue(all(source["accessedAt"].endswith("Z") for source in field["sources"]))
            self.assertTrue(field["astra"]["checks"]["factInterpretationSeparated"])
            criteria = cap19.evaluate_acceptance_criteria(
                field,
                Path(seal["fieldEvidence"]["path"]),
            )
            self.assertEqual(set(criteria), {item[0] for item in cap19.DONECHECK_CRITERIA})
            self.assertTrue(all(criteria.values()))

    def test_any_nonpassing_acceptance_criterion_prevents_donecheck_and_seal(self) -> None:
        criterion_ids = [item[0] for item in cap19.DONECHECK_CRITERIA]
        held = {criterion_id: True for criterion_id in criterion_ids}
        held["citation_grounding"] = False
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "capability-19"
            with patch.object(cap19, "evaluate_acceptance_criteria", return_value=held):
                with self.assertRaisesRegex(
                    cap19.VerificationHold,
                    "CAP19_ACCEPTANCE_CRITERION_HOLD",
                ):
                    cap19.execute_field_proof(root, self.fetcher, self.provider)
            self.assertFalse((root / "mandatory-donecheck.json").exists())
            self.assertFalse((root / "field-verification-seal.json").exists())

    def test_provider_and_model_route_are_exact(self) -> None:
        def wrong_route(_capsule: str) -> dict:
            result = self.provider(_capsule)
            result["routeEvidence"] = {
                "provider": "local_runtime",
                "model": "unsupported-model",
            }
            return result

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "capability-19"
            with self.assertRaisesRegex(cap19.VerificationHold, "QWEN3_14B_ROUTE_REQUIRED"):
                cap19.execute_field_proof(root, self.fetcher, wrong_route)
            self.assertFalse((root / "field-verification-seal.json").exists())

    def test_disallowed_host_fails_before_fetch(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "SOURCE_HOST_NOT_ALLOWLISTED"):
            cap19.validate_url("https://example.com/source")

    def test_retry_is_bounded_to_two_attempts(self) -> None:
        calls = 0

        def fail(_url: str) -> dict:
            nonlocal calls
            calls += 1
            raise TimeoutError("controlled")

        with self.assertRaisesRegex(cap19.VerificationHold, "SOURCE_FETCH_RETRY_EXHAUSTED"):
            cap19.bounded_fetch(dict(cap19.SOURCES[0]), fail)
        self.assertEqual(calls, 2)

    def test_missing_citation_holds(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "IANA_CITATION_MISSING"):
            cap19.validate_synthesis("example.com is mentioned by RFC 2606")

    def test_fact_interpretation_separation_is_required(self) -> None:
        text = (
            "example.com [IANA_EXAMPLE_DOMAINS] is governed by RFC 2606 [RFC2606]."
        )
        with self.assertRaisesRegex(cap19.VerificationHold, "SOURCED_FACTS_SECTION_MISSING"):
            cap19.validate_synthesis(text)

    def test_failure_path_proves_all_required_fail_closed_controls(self) -> None:
        result = cap19.failure_path_proof()
        self.assertEqual(result["retryAttempts"], cap19.MAX_ATTEMPTS)
        self.assertEqual(result["providerUnavailableAttempts"], cap19.MAX_ATTEMPTS)
        self.assertTrue(all(
            value is True
            for key, value in result.items()
            if key not in {"retryAttempts", "providerUnavailableAttempts"}
        ))

    def test_third_attempt_is_rejected(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "RETRY_BUDGET_EXCEEDED"):
            cap19.require_attempt_within_budget(cap19.MAX_ATTEMPTS + 1)

    def test_provider_unavailable_retries_twice_then_holds(self) -> None:
        attempts = 0

        def unavailable(*_args, **_kwargs):
            nonlocal attempts
            attempts += 1
            raise TimeoutError("controlled")

        with self.assertRaisesRegex(
            cap19.VerificationHold,
            "ASTRA_PROVIDER_UNAVAILABLE_RETRY_EXHAUSTED",
        ):
            cap19.provider_chat("bounded capsule", opener=unavailable)
        self.assertEqual(attempts, cap19.MAX_ATTEMPTS)

    def test_unregistered_and_policy_mismatched_actions_do_not_execute(self) -> None:
        actions = cap19.load_json(cap19.ACTION_REGISTRY)
        bindings = cap19.load_json(cap19.BINDING_REGISTRY)
        self.assertFalse(cap19.registered_action_allowed({"actions": {}}, bindings))
        mismatched = json.loads(json.dumps(actions))
        mismatched["actions"][cap19.ACTION]["readOnlyNetwork"] = False
        self.assertFalse(cap19.registered_action_allowed(mismatched, bindings))

    def test_source_record_validation_holds_on_missing_authority_digest_and_material(self) -> None:
        base = [
            {
                "url": source["url"],
                "authority": source["authority"],
                "accessedAt": cap19.now(),
                "httpStatus": 200,
                "attempts": 1,
                "sha256": "0" * 64,
                "path": "/definitely/not/materialized",
            }
            for source in cap19.SOURCES
        ]
        missing_authority = json.loads(json.dumps(base))
        missing_authority[0].pop("authority")
        with self.assertRaisesRegex(cap19.VerificationHold, "PRIMARY_SOURCE_AUTHORITY_REQUIRED"):
            cap19.validate_source_records(missing_authority)
        missing_digest = json.loads(json.dumps(base))
        missing_digest[0].pop("sha256")
        with self.assertRaisesRegex(cap19.VerificationHold, "SOURCE_DIGEST_REQUIRED"):
            cap19.validate_source_records(missing_digest)
        with self.assertRaisesRegex(cap19.VerificationHold, "MATERIAL_STEP_EVIDENCE_REQUIRED"):
            cap19.validate_source_records(base)

    def test_provider_chat_accepts_direct_non_empty_string(self) -> None:
        result, _captured = self.provider_chat_result("  verified synthesis  ")
        self.assertEqual(result["output"], "verified synthesis")

    def test_provider_chat_accepts_governed_output_answer(self) -> None:
        result, _captured = self.provider_chat_result({
            "answer": "  governed synthesis  ",
            "facts": [],
            "inferences": [],
            "proposals": [],
            "uncertainties": [],
            "language": "EN",
            "length": "CONCISE",
            "structure": "PLAIN",
        })
        self.assertEqual(result["output"], "governed synthesis")

    def test_governed_output_is_not_misclassified_as_empty(self) -> None:
        result, _captured = self.provider_chat_result({"answer": "present"})
        self.assertEqual(result["output"], "present")

    def test_provider_chat_holds_when_answer_is_missing(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "ASTRA_OUTPUT_EMPTY"):
            self.provider_chat_result({})

    def test_provider_chat_holds_when_output_is_missing(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "ASTRA_OUTPUT_EMPTY"):
            self.provider_chat_result(MISSING)

    def test_provider_chat_holds_when_output_is_none(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "ASTRA_OUTPUT_EMPTY"):
            self.provider_chat_result(None)

    def test_provider_chat_holds_when_answer_is_none(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "ASTRA_OUTPUT_EMPTY"):
            self.provider_chat_result({"answer": None})

    def test_provider_chat_holds_when_answer_is_non_string(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "ASTRA_OUTPUT_EMPTY"):
            self.provider_chat_result({"answer": ["unsupported"]})

    def test_provider_chat_holds_when_answer_is_blank(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "ASTRA_OUTPUT_EMPTY"):
            self.provider_chat_result({"answer": "   "})

    def test_provider_chat_holds_when_direct_string_is_blank(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "ASTRA_OUTPUT_EMPTY"):
            self.provider_chat_result("   ")

    def test_provider_chat_holds_for_unsupported_output_shape(self) -> None:
        with self.assertRaisesRegex(cap19.VerificationHold, "ASTRA_OUTPUT_EMPTY"):
            self.provider_chat_result(["unsupported"])

    def test_provider_payload_binds_authoritative_provenance(self) -> None:
        _result, captured = self.provider_chat_result(
            "example.com [IANA_EXAMPLE_DOMAINS] is governed by RFC 2606 [RFC2606]."
        )

        self.assertEqual(
            captured["payload"]["authoritative_provenance"],
            [source["url"] for source in cap19.SOURCES],
        )


if __name__ == "__main__":
    unittest.main()
