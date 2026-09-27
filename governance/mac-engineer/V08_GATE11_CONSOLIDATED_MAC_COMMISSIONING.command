#!/bin/zsh
set -u
export PYTHONDONTWRITEBYTECODE=1

PRODUCT="${ENGURU_GATE11_PRODUCT_REPO:-$HOME/Enguru/Projects/enguru-mac-engineer}"

EXPECTED_HEAD="${ENGURU_GATE11_EXPECTED_PRODUCT_HEAD:-5c636cdd14247ee320fb08f4a312573918f63df1}"

EXPECTED_BRANCH="${ENGURU_GATE11_EXPECTED_PRODUCT_BRANCH:-feat/v08-native-productization-provenance}"

TARGET="runtime/tests/test_python_test_replacement_policy.py"

cd "$PRODUCT" || exit 20

HEAD="$(git rev-parse HEAD)"
BRANCH="$(git branch --show-current)"
STATUS="$(git status --porcelain=v1 --untracked-files=all)"

if [ "$HEAD" != "$EXPECTED_HEAD" ]; then
  printf 'STATE=HOLD\n'
  printf 'HOLD=PRODUCT_HEAD_PRECONDITION\n'
  exit 2
fi

if [ "$BRANCH" != "$EXPECTED_BRANCH" ]; then
  printf 'STATE=HOLD\n'
  printf 'HOLD=PRODUCT_BRANCH_PRECONDITION\n'
  exit 2
fi

if [ -n "$STATUS" ]; then
  printf 'STATE=HOLD\n'
  printf 'HOLD=PRODUCT_WORKTREE_PRECONDITION\n'
  exit 2
fi

if [ -e "$TARGET" ]; then
  printf 'STATE=HOLD\n'
  printf 'HOLD=TARGET_ALREADY_EXISTS_RECONCILE\n'
  exit 2
fi

cat > "$TARGET" <<'PYTEST'
import inspect
import sys
import tempfile
import unittest
from pathlib import Path


RUNTIME = Path(__file__).resolve().parents[1]

if str(RUNTIME) not in sys.path:
    sys.path.insert(0, str(RUNTIME))

import engineering_actions


class PythonTestReplacementPolicyTests(unittest.TestCase):
    def call_validator(
        self,
        root,
        path,
        policy=None,
    ):
        fn = (
            engineering_actions
            ._validated_relative_source_path
        )

        parameters = list(
            inspect.signature(
                fn
            ).parameters.values()
        )

        if policy is None:
            return fn(
                root,
                path,
            )

        self.assertEqual(
            len(parameters),
            3,
        )

        parameter = parameters[2]

        if parameter.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            return fn(
                root,
                path,
                policy,
            )

        return fn(
            root,
            path,
            **{
                parameter.name:
                    policy
            },
        )

    def test_python_test_scope_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()

            _, relative = self.call_validator(
                root,
                "runtime/tests/test_example.py",
                "python_test",
            )

            self.assertEqual(
                relative,
                "runtime/tests/test_example.py",
            )

            with self.assertRaises(ValueError):
                self.call_validator(
                    root,
                    "runtime/tests/helper.py",
                    "python_test",
                )

            with self.assertRaises(ValueError):
                self.call_validator(
                    root,
                    "runtime/app.py",
                    "python_test",
                )

            with self.assertRaises(ValueError):
                self.call_validator(
                    root,
                    "../test_escape.py",
                    "python_test",
                )

    def test_default_swift_scope_remains_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()

            _, relative = self.call_validator(
                root,
                "Sources/App/main.swift",
            )

            self.assertEqual(
                relative,
                "Sources/App/main.swift",
            )


if __name__ == "__main__":
    unittest.main()
PYTEST

TARGETED_LOG="$(mktemp)"
FULL_LOG="$(mktemp)"

python3 -B -m unittest discover \
  -s runtime/tests \
  -p 'test_python_test_replacement_policy.py' \
  -v >"$TARGETED_LOG" 2>&1

TARGETED_RC=$?

cat "$TARGETED_LOG"

if [ "$TARGETED_RC" -ne 0 ]; then
  printf 'STATE=HOLD\n'
  printf 'HOLD=TARGETED_TEST_FAILED\n'
  exit 2
fi

python3 -B -m unittest discover \
  -s runtime/tests \
  -v >"$FULL_LOG" 2>&1

FULL_RC=$?

tail -n 100 "$FULL_LOG"

if [ "$FULL_RC" -ne 0 ]; then
  printf 'STATE=HOLD\n'
  printf 'HOLD=FULL_RUNTIME_REGRESSION_FAILED\n'
  exit 2
fi

git diff --check || {
  printf 'STATE=HOLD\n'
  printf 'HOLD=DIFF_CHECK_FAILED\n'
  exit 2
}

CHANGED="$(
  {
    git diff --name-only
    git ls-files --others --exclude-standard
  } |
  sed '/^$/d' |
  sort -u
)"

if [ "$CHANGED" != "$TARGET" ]; then
  printf 'STATE=HOLD\n'
  printf 'HOLD=EXPECTED_SCOPE_MISMATCH\n'
  printf 'OBSERVED_SCOPE=%s\n' "$CHANGED"
  exit 2
fi

git add "$TARGET"

git \
  -c user.name="ENGURU Mac Engineer" \
  -c user.email="local@enguru.invalid" \
  commit \
  -m "test(mac-engineer): lock Python test replacement policy" \
  >/dev/null || {
    printf 'STATE=HOLD\n'
    printf 'HOLD=LOCAL_FIXTURE_COMMIT_FAILED\n'
    exit 2
  }

NEW_HEAD="$(git rev-parse HEAD)"

printf 'STATE=PASS\n'
printf 'REAL_ENGINEERING_OBJECTIVE_COMPLETE=PASS\n'
printf 'MISSION=LOCK_PYTHON_TEST_REPLACEMENT_POLICY_WITH_DURABLE_REGRESSION\n'
printf 'EXPECTED_SCOPE_MATCH_PASS=PASS\n'
printf 'TARGETED_TEST_PASS=PASS\n'
printf 'FULL_RUNTIME_REGRESSION=PASS\n'
printf 'PRODUCT_MUTATION_PATHS=1\n'
printf 'PRODUCT_MUTATION_PATH=%s\n' "$TARGET"
printf 'PRODUCT_PRE_HEAD=%s\n' "$EXPECTED_HEAD"
printf 'PRODUCT_POST_HEAD=%s\n' "$NEW_HEAD"
printf 'PRODUCT_REMOTE_MUTATION=false\n'
printf 'NEXT_ACTION=P08\n'
