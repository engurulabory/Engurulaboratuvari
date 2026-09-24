#!/usr/bin/env python3
# ENGÜRÜ Mac Engineering™ v0.8 Gate 6 — Existing Product Change Scenario.
#
# One bounded existing-product presentation change:
# Gate 5 exact product truth
# -> Gate 3 UX/Aesthetic contract implementation
# -> regression
# -> local product commit
# -> native package/install
# -> fresh runtime verification
# -> Evidence
# -> Human Artistic Authority™.

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any


HOME = Path.home()
CONTROL = Path(__file__).resolve().parents[1]
PRODUCT = HOME / "Enguru/Projects/enguru-mac-engineer"

SESSION = CONTROL / "governance/mac-engineer/SESSION_STATE_V1.json"
UX_CONTRACT = (
    CONTROL
    / "governance/mac-engineer/V08_UX_AESTHETIC_PRODUCT_CONTRACT_V1.md"
)
GATE5_MODULE = CONTROL / "tools/mac_engineer_v08_native_app_productization.py"

EVIDENCE_ROOT = (
    HOME
    / "Enguru/Evidence/MacEngineer/v0.8/existing-product-change"
)

GATE5_COMMIT = "8bd62a2bd8c288b07d51f78ab2164444962bf7c4"
PRODUCT_BASELINE = "5432b9b135499cea18273c0e003877b864af92c6"
PRODUCT_BRANCH = "feat/v08-native-productization-provenance"
PRODUCT_VERSION = "0.8"

DONECHECK_EXACT_MAIN = "8b90a8fc93453dd8a84994195d28d14b15e261cb"

AUTHORIZED_PATHS = (
    "runtime/static/index.html",
    "runtime/tests/test_v08_existing_product_change.py",
)

MARKER = "ENGURU_V08_GATE6_PRIMARY_SURFACE_V1_START"


SPEC = importlib.util.spec_from_file_location(
    "enguru_v08_gate5_reuse",
    GATE5_MODULE,
)
if not SPEC or not SPEC.loader:
    raise RuntimeError("GATE5_REUSE_MODULE_LOAD_REQUIRED")

gate5 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate5)


PRIMARY_SURFACE_HTML = r'''
    <section
      id="enguruV08PrimaryState"
      class="enguruV08PrimaryState"
      aria-live="polite"
      aria-label="Üretim durumu"
    >
      <button
        class="enguruV08StateButton"
        type="button"
        onclick="toggleDrawer(true)"
        aria-label="Durum ayrıntılarını aç"
      >
        <span class="enguruV08StateDot" aria-hidden="true"></span>
        <span class="enguruV08StateCopy">
          <small>Durum</small>
          <strong id="enguruV08OverallState">Hazır</strong>
        </span>
      </button>

      <div
        id="enguruV08Attention"
        class="enguruV08Attention"
        hidden
      >
        <small>Dikkat</small>
        <strong id="enguruV08AttentionText">—</strong>
      </div>

      <div class="enguruV08Next">
        <small>Şimdi</small>
        <strong id="enguruV08NextAction">Mac Engineer’a yaz.</strong>
      </div>

      <button
        id="enguruV08NewProduction"
        class="enguruV08NewProduction"
        type="button"
        onclick="newWork()"
      >＋ Yeni Üretim</button>
    </section>
'''


PRESENTATION_BLOCK = r'''
<!-- ENGURU_V08_GATE6_PRIMARY_SURFACE_V1_START -->

<style id="enguru-v08-gate6-primary-surface">
/*
  Gate 6 canonical direction:
  one compact state surface + one natural-language production surface.
*/

#statusPill{
  display:none !important;
}

.sidebar,
body.enguru-world-flow [data-enguru-role="sidebar"]{
  display:none !important;
}

.shell,
body.enguru-world-flow [data-enguru-role="layout"]{
  display:block !important;
  grid-template-columns:1fr !important;
  gap:0 !important;
  width:100% !important;
  max-width:none !important;
  min-width:0 !important;
  height:auto !important;
  padding-inline:0 !important;
}

.main,
body.enguru-world-flow [data-enguru-role="main"]{
  width:100% !important;
  min-width:0 !important;
  max-width:none !important;
}

.enguruV08PrimaryState{
  position:sticky;
  top:72px;
  z-index:70;

  display:flex;
  align-items:center;
  gap:18px;
  flex-wrap:wrap;

  width:100%;
  min-width:0;

  padding:
    10px
    max(20px,calc((100% - 1120px)/2));

  border-bottom:1px solid var(--line);

  background:rgba(11,17,15,.94);

  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
}

.enguruV08StateButton{
  display:flex;
  align-items:center;
  gap:9px;

  flex:0 0 auto;

  border:0;
  border-radius:10px;

  background:transparent;
  color:var(--text);

  padding:5px 2px;

  text-align:left;
}

.enguruV08StateButton:focus-visible,
.enguruV08NewProduction:focus-visible{
  outline:2px solid var(--green);
  outline-offset:3px;
}

.enguruV08StateDot{
  width:9px;
  height:9px;

  flex:0 0 auto;

  border-radius:999px;

  background:var(--green);

  box-shadow:
    0 0 10px rgba(111,211,161,.42);
}

.enguruV08StateCopy,
.enguruV08Attention,
.enguruV08Next{
  min-width:0;
}

.enguruV08StateCopy{
  display:grid;
  gap:1px;
}

.enguruV08PrimaryState small{
  display:block;

  margin:0 0 1px;

  color:#7f9188;

  font-size:10px;
  font-weight:760;

  letter-spacing:.07em;
  text-transform:uppercase;
}

.enguruV08PrimaryState strong{
  display:block;

  min-width:0;

  color:#edf3ef;

  font-size:13px;
  line-height:1.3;
}

.enguruV08Attention{
  min-width:0;
  max-width:320px;
}

.enguruV08Attention[hidden]{
  display:none !important;
}

.enguruV08Attention strong{
  color:#e6d9a4;
}

.enguruV08Next{
  flex:1 1 280px;

  min-width:180px;

  overflow:hidden;
}

.enguruV08Next strong{
  overflow:hidden;

  text-overflow:ellipsis;
  white-space:nowrap;
}

.enguruV08NewProduction{
  flex:0 0 auto;

  border:1px solid #33483e;
  border-radius:10px;

  background:#e8efe9;
  color:#122019;

  padding:8px 12px;

  font-weight:750;
}

#enguruFixedScrollRail{
  top:146px !important;
}

@media(max-width:860px){
  .enguruV08PrimaryState{
    position:relative;
    top:auto;

    gap:10px 14px;

    padding:10px 16px;
  }

  .enguruV08Next{
    flex-basis:100%;
    order:4;
  }

  #enguruFixedScrollRail{
    top:112px !important;
  }
}
</style>

<script id="enguru-v08-gate6-primary-surface-script">
(() => {
  const value = id => {
    const el=document.getElementById(id);
    return (el?.textContent || "").trim();
  };

  function updatePrimarySurface(){
    const state=
      document.getElementById(
        "enguruV08OverallState"
      );

    const attention=
      document.getElementById(
        "enguruV08Attention"
      );

    const attentionText=
      document.getElementById(
        "enguruV08AttentionText"
      );

    const next=
      document.getElementById(
        "enguruV08NextAction"
      );

    if(
      !state
      || !attention
      || !attentionText
      || !next
    ){
      return;
    }

    const pill=
      value("statusPill")
        .toLocaleUpperCase("tr-TR");

    const system=
      value("dSystem")
        .toLocaleUpperCase("tr-TR");

    const ai=
      value("dAI")
        .toLocaleUpperCase("tr-TR");

    const steward=
      value("dSteward")
        .toLocaleUpperCase("tr-TR");

    const github=
      value("dGitHub")
        .toLocaleUpperCase("tr-TR");

    const issues=[];

    if(system==="HOLD"){
      issues.push("Sistem");
    }

    if(ai==="BAĞLANMADI"){
      issues.push("Yerel AI");
    }

    if(steward==="BAĞLANMADI"){
      issues.push("Steward");
    }

    if(github==="BAĞLANMADI"){
      issues.push("GitHub");
    }

    const working=
      pill==="ÇALIŞIYOR";

    state.textContent=
      working
        ?"Çalışıyor"
        :issues.length
          ?"Dikkat gerekiyor"
          :"Hazır";

    attention.hidden=
      issues.length===0;

    attentionText.textContent=
      issues.length
        ?issues.join(" · ")
        :"—";

    next.textContent=
      working
        ?"Üretim sürüyor."
        :issues.length
          ?"Durum ayrıntılarını aç."
          :"Mac Engineer’a yaz.";
  }

  [
    "statusPill",
    "dSystem",
    "dAI",
    "dSteward",
    "dGitHub"
  ].forEach(id=>{
    const el=
      document.getElementById(id);

    if(el){
      new MutationObserver(
        updatePrimarySurface
      ).observe(
        el,
        {
          childList:true,
          subtree:true,
          characterData:true
        }
      );
    }
  });

  window.addEventListener(
    "load",
    updatePrimarySurface
  );

  document.addEventListener(
    "visibilitychange",
    updatePrimarySurface
  );

  requestAnimationFrame(
    updatePrimarySurface
  );
})();
</script>

<!-- ENGURU_V08_GATE6_PRIMARY_SURFACE_V1_END -->
'''


PRODUCT_TEST = r'''from pathlib import Path
import unittest


RUNTIME = Path(__file__).resolve().parents[1]
INDEX = RUNTIME / "static" / "index.html"


class V08ExistingProductChangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = INDEX.read_text(encoding="utf-8")

    def test_one_canonical_primary_surface_exists(self) -> None:
        self.assertEqual(
            self.source.count(
                "ENGURU_V08_GATE6_PRIMARY_SURFACE_V1_START"
            ),
            1,
        )
        self.assertEqual(
            self.source.count(
                'id="enguruV08PrimaryState"'
            ),
            1,
        )

    def test_persistent_sidebar_is_secondary_not_primary(self) -> None:
        self.assertIn(
            'body.enguru-world-flow [data-enguru-role="sidebar"]',
            self.source,
        )
        self.assertIn(
            "display:none !important;",
            self.source,
        )
        self.assertIn(
            "grid-template-columns:1fr !important;",
            self.source,
        )

    def test_three_primary_questions_have_surface_answers(self) -> None:
        for expected in (
            'id="enguruV08OverallState"',
            'id="enguruV08Attention"',
            'id="enguruV08NextAction"',
            ">Durum<",
            ">Dikkat<",
            ">Şimdi<",
        ):
            self.assertIn(
                expected,
                self.source,
            )

    def test_natural_language_composer_remains_primary(self) -> None:
        for expected in (
            'class="composer"',
            'id="q"',
            'placeholder="Mac Engineer’a yaz…"',
        ):
            self.assertIn(
                expected,
                self.source,
            )

    def test_new_production_remains_direct(self) -> None:
        self.assertIn(
            'id="enguruV08NewProduction"',
            self.source,
        )
        self.assertIn(
            'onclick="newWork()"',
            self.source,
        )

    def test_advanced_capabilities_remain_on_demand(self) -> None:
        for expected in (
            'id="drawer"',
            "showRepoDetails()",
            "showDoneCheck()",
            "enguruHistoryShade",
        ):
            self.assertIn(
                expected,
                self.source,
            )

    def test_attention_is_conditional(self) -> None:
        self.assertIn(
            'id="enguruV08Attention"',
            self.source,
        )
        self.assertIn(
            "attention.hidden=",
            self.source,
        )
        self.assertIn(
            "issues.length===0",
            self.source,
        )

    def test_overflow_resilience_contract_is_encoded(self) -> None:
        for expected in (
            "flex-wrap:wrap;",
            "min-width:0;",
            "text-overflow:ellipsis;",
            "overflow-x:hidden",
        ):
            self.assertIn(
                expected,
                self.source,
            )

    def test_primary_focus_contract_is_encoded(self) -> None:
        self.assertIn(
            ":focus-visible",
            self.source,
        )

    def test_runtime_functions_remain_present(self) -> None:
        for expected in (
            "async function send()",
            "async function loadStatus()",
            "function renderSidebar()",
            "function toggleDrawer(on)",
        ):
            self.assertIn(
                expected,
                self.source,
            )


if __name__ == "__main__":
    unittest.main()
'''


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def stamp() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def load_json(
    path: Path,
    label: str,
) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(
            f"{label}_REQUIRED:{path}"
        )

    value = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(value, dict):
        raise RuntimeError(
            f"{label}_OBJECT_REQUIRED"
        )

    return value


def git(*args: str) -> str:
    return gate5.git(*args)


def changed_between(
    base: str,
    head: str,
) -> list[str]:
    return sorted(
        item
        for item in git(
            "diff",
            "--name-only",
            f"{base}...{head}",
        ).splitlines()
        if item
    )


def write_hold(
    run_dir: Path,
    reason: str,
    details: dict[str, Any] | None = None,
) -> int:
    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = run_dir / "evidence.json"

    payload = {
        "schema":
            "enguru.mac-engineer.v08-existing-product-change/v1",
        "observedAt": utc_now(),
        "state": "HOLD",
        "implementationState": "HOLD",
        "gate": "V08-06",
        "reason": reason,
        "details": details or {},
        "remotePush": False,
        "secondCanonicalTruth": False,
        "nextAction": "RECOVERY_REQUIRED",
    }

    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("STATE=HOLD")
    print("V08_GATE_06=HOLD")
    print(
        "EXISTING_PRODUCT_CHANGE_IMPLEMENTATION=HOLD"
    )
    print(f"HOLD={reason}")
    print(f"EVIDENCE={path}")
    print("NEXT_ACTION=RECOVERY_REQUIRED")

    return 2


def ensure_preconditions() -> dict[str, Any]:
    session = load_json(
        SESSION,
        "SESSION_STATE",
    )

    if session.get("currentVersion") != "v0.8":
        raise RuntimeError(
            "CURRENT_VERSION_V08_REQUIRED"
        )

    if (
        session.get("currentObjective")
        != "V08_EXISTING_PRODUCT_CHANGE_SCENARIO"
    ):
        raise RuntimeError(
            "V08_GATE6_OBJECTIVE_REQUIRED"
        )

    v08 = session.get("currentV08") or {}

    gate5_state = v08.get("gate5") or {}

    if gate5_state.get("state") != "PASS":
        raise RuntimeError(
            "V08_GATE5_CANONICAL_PASS_REQUIRED"
        )

    if (
        gate5_state.get("productLocalCommit")
        != GATE5_COMMIT
    ):
        raise RuntimeError(
            "V08_GATE5_EXACT_PRODUCT_COMMIT_REQUIRED"
        )

    if (v08.get("gate3") or {}).get("state") != "PASS":
        raise RuntimeError(
            "V08_GATE3_UX_CONTRACT_PASS_REQUIRED"
        )

    dc = v08.get("doneCheckAuthority") or {}

    if (
        dc.get("exactMain")
        != DONECHECK_EXACT_MAIN
    ):
        raise RuntimeError(
            "DONECHECK_V1_2_EXACT_MAIN_REQUIRED"
        )

    if not UX_CONTRACT.is_file():
        raise RuntimeError(
            "V08_UX_CONTRACT_REQUIRED"
        )

    if (
        not PRODUCT.is_dir()
        or not (PRODUCT / ".git").exists()
    ):
        raise RuntimeError(
            "PRODUCT_REPOSITORY_REQUIRED"
        )

    if (
        git("branch", "--show-current")
        != PRODUCT_BRANCH
    ):
        raise RuntimeError(
            "PRODUCT_GATE6_WORKING_BRANCH_REQUIRED"
        )

    if (
        git("rev-parse", "origin/main")
        != PRODUCT_BASELINE
    ):
        raise RuntimeError(
            "PRODUCT_ORIGIN_MAIN_BASELINE_DRIFT"
        )

    if (
        git(
            "rev-parse",
            f"origin/{PRODUCT_BRANCH}",
        )
        != PRODUCT_BASELINE
    ):
        raise RuntimeError(
            "PRODUCT_REMOTE_WORKING_BRANCH_BASELINE_REQUIRED"
        )

    if (
        git(
            "merge-base",
            "HEAD",
            PRODUCT_BASELINE,
        )
        != PRODUCT_BASELINE
    ):
        raise RuntimeError(
            "PRODUCT_BASELINE_ANCESTRY_REQUIRED"
        )

    if git("status", "--porcelain"):
        raise RuntimeError(
            "PRODUCT_WORKTREE_CLEAN_REQUIRED"
        )

    if (
        gate5.plist_version(
            PRODUCT
            / "execution_prep/native_app/Info.plist"
        )
        != PRODUCT_VERSION
    ):
        raise RuntimeError(
            "PRODUCT_VERSION_V08_REQUIRED"
        )

    if shutil.which("safaridriver") is None:
        raise RuntimeError(
            "SAFARI_WEBKIT_RENDER_AUTHORITY_REQUIRED"
        )

    return session


def backup_sources(
    run_dir: Path,
) -> dict[str, str]:
    root = run_dir / "source-backup"

    refs: dict[str, str] = {}

    for rel in AUTHORIZED_PATHS:
        source = PRODUCT / rel

        if source.exists():
            target = root / rel

            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source,
                target,
            )

            refs[rel] = str(target)

    return refs


def restore_precommit_sources(
    backups: dict[str, str],
) -> None:
    for rel in AUTHORIZED_PATHS:
        target = PRODUCT / rel
        backup = backups.get(rel)

        if backup:
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            shutil.copy2(
                Path(backup),
                target,
            )
        elif target.exists():
            target.unlink()


def existing_gate6_commit() -> dict[str, Any] | None:
    head = git(
        "rev-parse",
        "HEAD",
    )

    if head == GATE5_COMMIT:
        return None

    if (
        git(
            "rev-list",
            "--count",
            f"{GATE5_COMMIT}..{head}",
        )
        != "1"
    ):
        raise RuntimeError(
            "GATE6_SINGLE_PRODUCT_COMMIT_REQUIRED"
        )

    changed = changed_between(
        GATE5_COMMIT,
        head,
    )

    if changed != sorted(AUTHORIZED_PATHS):
        raise RuntimeError(
            "GATE6_EXISTING_COMMIT_SCOPE_MISMATCH:"
            + ",".join(changed)
        )

    if (
        git(
            "rev-list",
            "--count",
            f"origin/{PRODUCT_BRANCH}..HEAD",
        )
        != "2"
    ):
        raise RuntimeError(
            "PRODUCT_LOCAL_AHEAD_TWO_REQUIRED"
        )

    index = (
        PRODUCT / AUTHORIZED_PATHS[0]
    ).read_text(
        encoding="utf-8"
    )

    test = (
        PRODUCT / AUTHORIZED_PATHS[1]
    ).read_text(
        encoding="utf-8"
    )

    if MARKER not in index:
        raise RuntimeError(
            "GATE6_PRIMARY_SURFACE_MARKER_REQUIRED"
        )

    if test != PRODUCT_TEST:
        raise RuntimeError(
            "GATE6_PRODUCT_TEST_CONTRACT_MISMATCH"
        )

    return {
        "head": head,
        "changedPaths": changed,
        "aheadRemoteWorkingBranch": 2,
        "reusedExistingCommit": True,
    }


def apply_product_change() -> None:
    index_path = PRODUCT / AUTHORIZED_PATHS[0]
    test_path = PRODUCT / AUTHORIZED_PATHS[1]

    source = index_path.read_text(
        encoding="utf-8"
    )

    if MARKER in source:
        raise RuntimeError(
            "GATE6_PRIMARY_SURFACE_ALREADY_PRESENT"
        )

    main_anchor = '  <main class="main">'

    if main_anchor not in source:
        raise RuntimeError(
            "PRODUCT_MAIN_SURFACE_ANCHOR_REQUIRED"
        )

    source = source.replace(
        main_anchor,
        main_anchor + PRIMARY_SURFACE_HTML,
        1,
    )

    body_anchor = "</body>"

    if body_anchor not in source:
        raise RuntimeError(
            "PRODUCT_BODY_CLOSE_REQUIRED"
        )

    source = source.replace(
        body_anchor,
        PRESENTATION_BLOCK
        + "\n\n"
        + body_anchor,
        1,
    )

    index_path.write_text(
        source,
        encoding="utf-8",
    )

    test_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    test_path.write_text(
        PRODUCT_TEST,
        encoding="utf-8",
    )


def verify_worktree_scope() -> list[str]:
    paths = sorted(
        item
        for item in set(
            git(
                "diff",
                "--name-only",
            ).splitlines()
            + git(
                "ls-files",
                "--others",
                "--exclude-standard",
            ).splitlines()
        )
        if item
    )

    if paths != sorted(AUTHORIZED_PATHS):
        raise RuntimeError(
            "GATE6_PRODUCT_MUTATION_SCOPE_MISMATCH:"
            + ",".join(paths)
        )

    return paths


def run_regression(
    run_dir: Path,
) -> dict[str, Any]:
    logs = run_dir / "logs"

    logs.mkdir(
        parents=True,
        exist_ok=True,
    )

    env = {
        **os.environ,
        "PYTHONPATH": str(PRODUCT / "runtime"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }

    checks: list[dict[str, Any]] = []

    def checked(
        name: str,
        args: list[str],
        timeout: int = 1800,
    ) -> None:
        result = gate5.run(
            args,
            cwd=PRODUCT,
            timeout=timeout,
            env=env,
        )

        log = logs / f"{name}.log"

        log.write_text(
            (
                result["stdout"]
                + "\n"
                + result["stderr"]
            ).strip()
            + "\n",
            encoding="utf-8",
        )

        if result["code"] != 0:
            raise RuntimeError(
                f"REGRESSION_FAILED:{name}"
            )

        checks.append({
            "name": name,
            "state": "PASS",
            "log": str(log),
        })

    checked(
        "targeted-v08-existing-product-change",
        [
            "python3",
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "runtime/tests",
            "-p",
            "test_v08_existing_product_change.py",
            "-v",
        ],
    )

    checked(
        "full-runtime-regression",
        [
            "python3",
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "runtime/tests",
            "-v",
        ],
        timeout=2400,
    )

    checked(
        "native-prep-syntax",
        [
            "zsh",
            "-n",
            "execution_prep/native_app/prepare_native_app.command",
        ],
        timeout=120,
    )

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "EnguruMacEngineer"

        checked(
            "native-swift-build",
            [
                "xcrun",
                "swiftc",
                "-parse-as-library",
                "execution_prep/native_app/EnguruMacEngineerApp.swift",
                "-o",
                str(out),
                "-framework",
                "SwiftUI",
                "-framework",
                "WebKit",
                "-framework",
                "AppKit",
            ],
            timeout=900,
        )

    checked(
        "diff-check",
        [
            "git",
            "diff",
            "--check",
        ],
        timeout=120,
    )

    return {
        "state": "PASS",
        "checks": checks,
    }


def commit_product_change(
    scope: list[str],
) -> dict[str, Any]:
    result = gate5.run(
        [
            "git",
            "add",
            *AUTHORIZED_PATHS,
        ],
        cwd=PRODUCT,
        timeout=120,
    )

    if result["code"] != 0:
        raise RuntimeError(
            "GATE6_PRODUCT_STAGE_FAILED"
        )

    staged = sorted(
        item
        for item in git(
            "diff",
            "--cached",
            "--name-only",
        ).splitlines()
        if item
    )

    if staged != sorted(AUTHORIZED_PATHS):
        raise RuntimeError(
            "GATE6_STAGED_SCOPE_MISMATCH:"
            + ",".join(staged)
        )

    result = gate5.run(
        [
            "git",
            "commit",
            "-m",
            "Mac Engineer v0.8: implement Gate 6 primary product surface",
        ],
        cwd=PRODUCT,
        timeout=300,
    )

    if result["code"] != 0:
        raise RuntimeError(
            "GATE6_PRODUCT_COMMIT_FAILED"
        )

    if git("status", "--porcelain"):
        raise RuntimeError(
            "GATE6_POST_COMMIT_CLEAN_REQUIRED"
        )

    head = git(
        "rev-parse",
        "HEAD",
    )

    changed = changed_between(
        GATE5_COMMIT,
        head,
    )

    if changed != sorted(AUTHORIZED_PATHS):
        raise RuntimeError(
            "GATE6_COMMIT_SCOPE_MISMATCH:"
            + ",".join(changed)
        )

    if (
        git(
            "rev-list",
            "--count",
            f"{GATE5_COMMIT}..{head}",
        )
        != "1"
    ):
        raise RuntimeError(
            "GATE6_SINGLE_COMMIT_REQUIRED"
        )

    ahead = git(
        "rev-list",
        "--count",
        f"origin/{PRODUCT_BRANCH}..HEAD",
    )

    if ahead != "2":
        raise RuntimeError(
            "GATE6_PRODUCT_AHEAD_TWO_REQUIRED"
        )

    return {
        "head": head,
        "changedPaths": changed,
        "mutationScopeBeforeCommit": scope,
        "aheadRemoteWorkingBranch": 2,
        "reusedExistingCommit": False,
    }


def verify_source_contract() -> dict[str, Any]:
    source = (
        PRODUCT / AUTHORIZED_PATHS[0]
    ).read_text(
        encoding="utf-8"
    )

    checks = {
        "singleCanonicalDirection":
            source.count(MARKER) == 1,

        "persistentSidebarPrimaryFalse":
            (
                'body.enguru-world-flow '
                '[data-enguru-role="sidebar"]'
                in source
                and "display:none !important;"
                in source
            ),

        "singleColumnPrimaryLayout":
            "grid-template-columns:1fr !important;"
            in source,

        "primaryStateSurface":
            'id="enguruV08OverallState"'
            in source,

        "conditionalAttention":
            (
                'id="enguruV08Attention"'
                in source
                and "attention.hidden="
                in source
                and "issues.length===0"
                in source
            ),

        "visibleNextAction":
            'id="enguruV08NextAction"'
            in source,

        "naturalLanguageComposerPreserved":
            (
                'class="composer"'
                in source
                and 'id="q"'
                in source
            ),

        "newProductionDirect":
            (
                'id="enguruV08NewProduction"'
                in source
                and 'onclick="newWork()"'
                in source
            ),

        "advancedControlsSecondary":
            (
                'id="drawer"'
                in source
                and "showRepoDetails()"
                in source
                and "enguruHistoryShade"
                in source
            ),

        "overflowResilienceEncoded":
            (
                "flex-wrap:wrap;"
                in source
                and "min-width:0;"
                in source
                and "text-overflow:ellipsis;"
                in source
                and "overflow-x:hidden"
                in source
            ),

        "primaryFocusContract":
            ":focus-visible"
            in source,

        "runtimeFunctionsPreserved":
            (
                "async function send()"
                in source
                and "async function loadStatus()"
                in source
                and "function toggleDrawer(on)"
                in source
            ),
    }

    failed = [
        key
        for key, value in checks.items()
        if not value
    ]

    if failed:
        raise RuntimeError(
            "GATE6_SOURCE_CONTRACT_HOLD:"
            + ",".join(failed)
        )

    return {
        "state": "PASS",
        "checks": checks,
    }


def package_install_verify(
    product_head: str,
) -> dict[str, Any]:
    gate5.stop_old_runtime()

    result = gate5.run(
        [
            "zsh",
            "execution_prep/native_app/prepare_native_app.command",
        ],
        cwd=PRODUCT,
        timeout=1800,
        env={
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )

    if result["code"] != 0:
        raise RuntimeError(
            "GATE6_NATIVE_PACKAGE_INSTALL_FAILED:"
            + (
                result["stderr"]
                or result["stdout"]
            )[-1200:]
        )

    installed = gate5.verify_installed(
        product_head
    )

    readiness = gate5.fresh_launch_ready()

    installed_after_launch = (
        gate5.verify_installed(
            product_head
        )
    )

    return {
        "state": "PASS",
        "stdoutTail":
            result["stdout"][-5000:],
        "stderrTail":
            result["stderr"][-3000:],
        "installed":
            installed_after_launch,
        "readiness":
            readiness,
    }


def main() -> int:
    run_dir = EVIDENCE_ROOT / stamp()

    backups: dict[str, str] = {}
    product_commit_created = False

    try:
        ensure_preconditions()

        run_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        backups = backup_sources(
            run_dir
        )

        existing = existing_gate6_commit()

        if existing is None:
            apply_product_change()

            scope = verify_worktree_scope()

            regression = run_regression(
                run_dir
            )

            commit = commit_product_change(
                scope
            )

            product_commit_created = True
        else:
            regression = run_regression(
                run_dir
            )

            commit = existing

        product_head = commit["head"]

        if (
            git(
                "rev-parse",
                f"origin/{PRODUCT_BRANCH}",
            )
            != PRODUCT_BASELINE
        ):
            raise RuntimeError(
                "PRODUCT_REMOTE_BRANCH_DRIFT"
            )

        if git("status", "--porcelain"):
            raise RuntimeError(
                "PRODUCT_CLEAN_BEFORE_PACKAGE_REQUIRED"
            )

        source_contract = (
            verify_source_contract()
        )

        package = package_install_verify(
            product_head
        )

        installed = package["installed"]
        release = installed["release"]

        if (
            release.get("sourceCommit")
            != product_head
        ):
            raise RuntimeError(
                "GATE6_RELEASE_COMMIT_MISMATCH"
            )

        if (
            release.get("sourceBranch")
            != PRODUCT_BRANCH
        ):
            raise RuntimeError(
                "GATE6_RELEASE_BRANCH_MISMATCH"
            )

        path = run_dir / "evidence.json"

        payload = {
            "schema":
                "enguru.mac-engineer.v08-existing-product-change/v1",

            "observedAt": utc_now(),

            "state": "HOLD",

            "implementationState": "PASS",

            "gate": "V08-06",

            "claim": (
                "One bounded existing-product change "
                "has been built, tested, packaged and "
                "verified on the real Mac. "
                "Human Artistic Authority™ review "
                "remains open."
            ),

            "product": {
                "repository":
                    "engurulabory/enguru-mac-engineer",

                "baselineExactMain":
                    PRODUCT_BASELINE,

                "gate5ExactCommit":
                    GATE5_COMMIT,

                "workingBranch":
                    PRODUCT_BRANCH,

                "gate6LocalCommit":
                    product_head,

                "remoteWorkingBranchHead":
                    PRODUCT_BASELINE,

                "remotePush":
                    False,

                "changedPaths":
                    commit["changedPaths"],

                "aheadRemoteWorkingBranch":
                    commit[
                        "aheadRemoteWorkingBranch"
                    ],
            },

            "stages": {
                "discovery":
                    "PASS",

                "architecture":
                    "PASS_EXISTING_PRESENTATION_LAYER",

                "build":
                    "PASS",

                "test":
                    "PASS",

                "repair":
                    "NOT_REQUIRED_AFTER_CLEAN_REGRESSION",

                "package":
                    "PASS",

                "verification":
                    "PASS",

                "visualFieldReview":
                    "PENDING_HUMAN_ARTISTIC_AUTHORITY",
            },

            "sourceBackups":
                backups,

            "sourceContract":
                source_contract,

            "regression":
                regression,

            "packageInstall":
                package,

            "sourceBundleVersion":
                PRODUCT_VERSION,

            "installedBundleVersion":
                installed["bundleVersion"],

            "runtimeParity":
                installed["runtimeParity"],

            "releaseManifest":
                release,

            "codesign":
                installed["codesign"],

            "authorizedMutationPaths":
                list(AUTHORIZED_PATHS),

            "mutationPathCount":
                len(AUTHORIZED_PATHS),

            "renderAuthority":
                "SAFARI_WEBKIT_AVAILABLE",

            "humanArtisticAuthority":
                "REQUIRED",

            "humanArtisticDecision":
                "PENDING",

            "unnecessaryNewCoreCount":
                0,

            "secondCanonicalTruth":
                False,

            "remotePush":
                False,

            "doneCheckAuthority": {
                "product":
                    "DoneCheck™ v1.2",

                "version":
                    "1.2.0",

                "exactMain":
                    DONECHECK_EXACT_MAIN,
            },

            "hold":
                "HUMAN_ARTISTIC_AUTHORITY_REQUIRED",

            "nextAction":
                "HUMAN_ARTISTIC_AUTHORITY_REVIEW",
        }

        payload["evidencePath"] = str(path)

        path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        print("STATE=HOLD")
        print("V08_GATE_06=HOLD")
        print(
            "V08_GATE_06_IMPLEMENTATION=PASS"
        )
        print(
            "EXISTING_PRODUCT_CHANGE_IMPLEMENTATION=PASS"
        )
        print(
            f"PRODUCT_BRANCH={PRODUCT_BRANCH}"
        )
        print(
            f"PRODUCT_GATE6_LOCAL_COMMIT={product_head}"
        )
        print("PRODUCT_REMOTE_PUSH=false")
        print("PRODUCT_MUTATION_PATHS=2")
        print("SOURCE_CONTRACT=PASS")
        print("FULL_RUNTIME_REGRESSION=PASS")
        print(
            "SOURCE_INSTALLED_RUNTIME_PARITY=PASS"
        )
        print("RELEASE_PROVENANCE=PASS")
        print("CODESIGN=PASS")
        print(
            "FRESH_APP_RUNTIME_READINESS=PASS"
        )
        print(
            "RENDER_AUTHORITY=SAFARI_WEBKIT_AVAILABLE"
        )
        print(
            "HUMAN_ARTISTIC_AUTHORITY=REQUIRED"
        )
        print(
            "HOLD=HUMAN_ARTISTIC_AUTHORITY_REQUIRED"
        )
        print(f"EVIDENCE={path}")
        print(
            "NEXT_ACTION=HUMAN_ARTISTIC_AUTHORITY_REVIEW"
        )

        return 2

    except Exception as exc:
        if (
            not product_commit_created
            and backups
        ):
            try:
                gate5.run(
                    [
                        "git",
                        "reset",
                    ],
                    cwd=PRODUCT,
                    timeout=60,
                )

                restore_precommit_sources(
                    backups
                )
            except Exception:
                pass

        return write_hold(
            run_dir,
            f"{type(exc).__name__}:{exc}",
            {
                "gate5ExactCommit":
                    GATE5_COMMIT,

                "productBranch":
                    PRODUCT_BRANCH,

                "authorizedPaths":
                    list(AUTHORIZED_PATHS),

                "productCommitCreated":
                    product_commit_created,
            },
        )


if __name__ == "__main__":
    raise SystemExit(main())
