#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared_ai.mac_local_commissioning import assess_mac_local_commissioning


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.bundle.read_text(encoding="utf-8"))
    result = assess_mac_local_commissioning(payload)

    output = {
        "state": result.state,
        "reason": result.reason,
        "issues": list(result.issues),
        "evidence_ref_count": len(result.evidence),
        "bundle": str(args.bundle),
        "next_action": (
            "Record final local Evidence in canonical GitHub evidence and close Package 6."
            if result.state == "PASS"
            else "Resolve only the reported Package 6 evidence gaps, then rerun this DoneCheck."
        ),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if result.state == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
