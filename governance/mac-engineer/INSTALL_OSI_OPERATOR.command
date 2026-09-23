#!/bin/zsh
set -euo pipefail

CONTROL_PLANE="${ENGURU_CONTROL_PLANE:-$HOME/Enguru/Projects/Engurulaboratuvari}"
SOURCE="$CONTROL_PLANE/bin/enguru-mac"
TARGET_DIR="$HOME/Enguru/bin"
TARGET="$TARGET_DIR/enguru-mac"

[[ -x "$SOURCE" || -f "$SOURCE" ]] || {
  print "STATE=HOLD"
  print "HOLD=OPERATOR_SOURCE_MISSING"
  exit 2
}

mkdir -p "$TARGET_DIR"
ln -sfn "$SOURCE" "$TARGET"
chmod +x "$SOURCE"

print "STATE=PASS"
print "COMMAND=INSTALL_OSI_OPERATOR"
print "OPERATOR=$TARGET"

if [[ ":$PATH:" == *":$TARGET_DIR:"* ]]; then
  print "PATH=PASS"
  print "NEXT_ACTION=enguru-mac doctor"
else
  print "PATH=HOLD"
  print "NEXT_ACTION=export PATH=\"$HOME/Enguru/bin:\$PATH\""
fi
