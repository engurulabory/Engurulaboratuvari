from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared_ai.aggregate_closeout import TARGETS, assess_v06_aggregate


SCORECARD = ROOT / "evidence" / "mac-engineer" / "V06_PACKAGE5_AGGREGATE_SCORECARD.json"


def main() -> int:
    payload = json.loads(SCORECARD.read_text(encoding="utf-8"))
    result = assess_v06_aggregate(payload)
    if result.state != "PASS":
        raise AssertionError({"reason": result.reason, "issues": result.issues})

    domains = {
        name: {
            "target": TARGETS[name],
            "score": payload["domains"][name]["score"],
            "basis": payload["domains"][name]["basis"],
        }
        for name in TARGETS
    }

    operating_dimensions = payload["operatingCharacterDimensions"]
    operating_mean = round(
        sum(float(item["score"]) for item in operating_dimensions) / len(operating_dimensions),
        1,
    )
    if operating_mean != payload["domains"]["operating_character"]["score"]:
        raise AssertionError("operating character mean drift")

    if payload["criticalFailures"]["unresolved"] != 0:
        raise AssertionError("unresolved critical failure")

    print(
        json.dumps(
            {
                "state": "PASS",
                "claim": "ENGURU Mac Engineer v0.6 Package 5 aggregate evidence satisfies the locked GitHub engineering closeout targets; Mac Local Final Commissioning remains required for product final.",
                "scoreType": payload["scoreType"],
                "domains": domains,
                "operatingCharacterMean": operating_mean,
                "criticalFailures": 0,
                "packageStates": {
                    key: value["state"] for key, value in payload["packages"].items()
                },
                "doneCheckCount": len(payload["mandatoryDoneCheck"]),
                "evidenceRefCount": len(result.evidence),
                "truthBoundary": payload["truthBoundary"],
                "productFinalState": payload["productFinalState"],
                "nextRequiredGate": payload["nextRequiredGate"],
                "next_action": "Verify exact-head CI, reconcile Package 5 WORKLIST, merge, verify exact-main, then run Package 6 Mac Local Final Commissioning before product-level v0.6 VERIFIED FINAL / LOCKED.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
