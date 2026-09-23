#!/bin/zsh
set -euo pipefail

RUNNER_HOME="${ENGURU_GITHUB_RUNNER_HOME:-$HOME/Enguru/Runtime/GitHubRunner/enguru-mac-engineer}"
REPO_URL="${ENGURU_GITHUB_RUNNER_REPO_URL:-https://github.com/engurulabory/enguru-mac-engineer}"
RUNNER_NAME="${ENGURU_GITHUB_RUNNER_NAME:-OSi-M5-Pro}"
LABELS="${ENGURU_GITHUB_RUNNER_LABELS:-enguru-mac}"

[[ "$(uname -s)" == "Darwin" ]] || {
  print "STATE=HOLD"
  print "HOLD=MACOS_REQUIRED"
  exit 2
}

[[ "$(uname -m)" == "arm64" ]] || {
  print "STATE=HOLD"
  print "HOLD=ARM64_REQUIRED"
  exit 3
}

command -v python3 >/dev/null || {
  print "STATE=HOLD"
  print "HOLD=PYTHON3_REQUIRED"
  exit 4
}

mkdir -p "$RUNNER_HOME"

if [[ ! -f "$RUNNER_HOME/config.sh" ]]; then
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT INT TERM HUP

  python3 - "$TMP" <<'PY'
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import urllib.request

target = Path(sys.argv[1])
api = "https://api.github.com/repos/actions/runner/releases/latest"
request = urllib.request.Request(
    api,
    headers={"Accept": "application/vnd.github+json", "User-Agent": "enguru-mac-engineer"},
)
with urllib.request.urlopen(request, timeout=30) as response:
    release = json.load(response)

assets = release.get("assets") or []
asset = next(
    (
        item for item in assets
        if str(item.get("name", "")).startswith("actions-runner-osx-arm64-")
        and str(item.get("name", "")).endswith(".tar.gz")
    ),
    None,
)
if not asset:
    raise SystemExit("RUNNER_OSX_ARM64_ASSET_NOT_FOUND")

digest = str(asset.get("digest") or "")
if not digest.startswith("sha256:"):
    raise SystemExit("RUNNER_ASSET_SHA256_DIGEST_REQUIRED")

archive = target / asset["name"]
request = urllib.request.Request(
    asset["browser_download_url"],
    headers={"User-Agent": "enguru-mac-engineer"},
)
with urllib.request.urlopen(request, timeout=120) as response, archive.open("wb") as handle:
    while True:
        chunk = response.read(1024 * 1024)
        if not chunk:
            break
        handle.write(chunk)

actual = hashlib.sha256(archive.read_bytes()).hexdigest()
expected = digest.split(":", 1)[1]
if actual != expected:
    raise SystemExit("RUNNER_ASSET_DIGEST_MISMATCH")

print(str(archive))
PY

  ARCHIVE="$(find "$TMP" -maxdepth 1 -name 'actions-runner-osx-arm64-*.tar.gz' -print -quit)"
  [[ -n "$ARCHIVE" ]] || {
    print "STATE=HOLD"
    print "HOLD=RUNNER_ARCHIVE_REQUIRED"
    exit 5
  }

  tar -xzf "$ARCHIVE" -C "$RUNNER_HOME"
fi

if [[ ! -f "$RUNNER_HOME/.runner" ]]; then
  print "GitHub runner registration tokenını yalnız bu gizli alana yapıştır."
  print "Token ekrana veya Evidence dosyasına yazılmaz."
  read -s "RUNNER_TOKEN?Runner token: "
  print
  [[ -n "$RUNNER_TOKEN" ]] || {
    print "STATE=HOLD"
    print "HOLD=RUNNER_REGISTRATION_TOKEN_REQUIRED"
    exit 6
  }

  (
    cd "$RUNNER_HOME"
    ./config.sh       --url "$REPO_URL"       --token "$RUNNER_TOKEN"       --name "$RUNNER_NAME"       --labels "$LABELS"       --work "_work"       --unattended       --replace
  )
  unset RUNNER_TOKEN
fi

(
  cd "$RUNNER_HOME"
  if [[ -x ./svc.sh ]]; then
    ./svc.sh install >/dev/null 2>&1 || true
    ./svc.sh start
  else
    print "STATE=HOLD"
    print "HOLD=RUNNER_SERVICE_SCRIPT_REQUIRED"
    exit 7
  fi
)

sleep 2

if ps -axo command= | grep -v grep | grep -q "Runner.Listener"; then
  print "STATE=PASS"
  print "RUNNER_HOME=$RUNNER_HOME"
  print "RUNNER_NAME=$RUNNER_NAME"
  print "LABELS=self-hosted,macOS,ARM64,$LABELS"
  print "TOKEN_PERSISTED=false"
  print "NEXT_ACTION=enguru-mac doctor"
else
  print "STATE=HOLD"
  print "HOLD=RUNNER_LISTENER_NOT_OBSERVED"
  print "NEXT_ACTION=enguru-mac doctor"
  exit 8
fi
