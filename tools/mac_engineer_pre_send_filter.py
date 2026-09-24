#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import re
import subprocess
from pathlib import Path

HOME = Path.home()
PRODUCT = HOME / "Enguru/Projects/enguru-mac-engineer"

REQUIRED = (
    "# ENGURU_PRE_SEND_PACKAGE_V1",
    "# ACTIVE_OBJECTIVE=",
    "# NECESSARY_DIFFERENCE=",
    "# LANGUAGE=POSITIVE_CONSTRUCTIVE_TRUTHFUL",
    "# SECOND_LOOK=REQUIRED",
    "# EXPECTED_SCOPE=",
    "# RECOVERY=",
    "# DONECHECK=V1.2_REQUIRED",
)

RISK_PATTERNS = (
    r"\bgit\s+push\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\brm\s+-rf\b",
    r"\bgit\s+clean\s+-[a-zA-Z]*f",
    r"\bdeploy\b",
)


def python_heredocs(source: str) -> list[str]:
    pattern = re.compile(
        r"<<['\"]?(PY|PYTHON)['\"]?\n(.*?)\n\1(?=\n|$)",
        re.DOTALL,
    )
    return [match.group(2) for match in pattern.finditer(source)]


def check_text(source: str) -> dict[str, bool]:
    checks = {
        "canonicalMarkers":
            all(marker in source for marker in REQUIRED),

        "decisionOutput":
            all(
                marker in source
                for marker in (
                    "STATE=",
                    "CLAIM=",
                    "NEXT_ACTION=",
                )
            ),

        "pythonHeredocSyntax": True,

        "authorityBoundary": True,
    }

    try:
        for block in python_heredocs(source):
            ast.parse(block)
    except SyntaxError:
        checks["pythonHeredocSyntax"] = False

    risk = any(
        re.search(pattern, source)
        for pattern in RISK_PATTERNS
    )

    if risk:
        checks["authorityBoundary"] = (
            "# HUMAN_THRESHOLD=REQUIRED"
            in source
        )

    return checks


def runtime_binding(
    product: Path = PRODUCT,
) -> dict[str, bool]:
    governance = product / "runtime/governance.py"
    app = product / "runtime/app.py"
    tests = product / "runtime/tests/test_operating_character.py"

    if not (
        governance.is_file()
        and app.is_file()
        and tests.is_file()
    ):
        return {
            "programmerAgentIdentity": False,
            "steelCharacter": False,
            "runtimeBinding": False,
            "operatingCharacterTests": False,
        }

    g = governance.read_text(encoding="utf-8")
    a = app.read_text(encoding="utf-8")

    return {
        "programmerAgentIdentity":
            "ENGÜRÜ Programmer Agent™ v0.1" in g,

        "steelCharacter":
            "STEEL OPERATING CHARACTER" in g,

        "runtimeBinding":
            (
                "SYSTEM_PROMPT" in a
                and "operating_character_prompt()" in a
                and "response_policy()" in a
            ),

        "operatingCharacterTests":
            tests.is_file(),
    }


def check_package(path: Path) -> tuple[str, dict]:
    source = path.read_text(encoding="utf-8")

    checks = check_text(source)

    syntax = subprocess.run(
        ["zsh", "-n", str(path)],
        capture_output=True,
        text=True,
    )

    checks["shellSyntax"] = syntax.returncode == 0
    checks.update(runtime_binding())

    state = (
        "PASS"
        if all(checks.values())
        else "HOLD"
    )

    return state, checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="?")
    parser.add_argument(
        "--self-check",
        action="store_true",
    )
    args = parser.parse_args()

    if args.self_check:
        checks = runtime_binding()
        state = (
            "PASS"
            if all(checks.values())
            else "HOLD"
        )
    else:
        if not args.package:
            parser.error(
                "package path or --self-check required"
            )
        state, checks = check_package(
            Path(args.package)
        )

    for key, value in checks.items():
        print(
            f"{key}={'PASS' if value else 'HOLD'}"
        )

    print(f"STATE={state}")

    if state == "PASS":
        print(
            "CLAIM=PROGRAMMER_AGENT_PRE_SEND_FILTER_PASS"
        )
        print(
            "NEXT_ACTION=EXECUTE_VERIFIED_PACKAGE"
        )
        return 0

    print(
        "CLAIM=PROGRAMMER_AGENT_PRE_SEND_FILTER_HOLD"
    )
    print(
        "NEXT_ACTION=CORRECT_REQUIRED_DIFFERENCE"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
