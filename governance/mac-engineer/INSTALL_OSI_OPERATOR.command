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

PROFILE="$HOME/.zprofile"
START="# >>> ENGURU MAC OPERATOR >>>"
END="# <<< ENGURU MAC OPERATOR <<<"

touch "$PROFILE"

if ! grep -Fq "$START" "$PROFILE"; then
  cat >> "$PROFILE" <<'EOF'

# >>> ENGURU MAC OPERATOR >>>
export PATH="$HOME/Enguru/bin:$PATH"
# <<< ENGURU MAC OPERATOR <<<
EOF
fi

export PATH="$TARGET_DIR:$PATH"

if command -v enguru-mac >/dev/null 2>&1; then
  print "PATH=PASS"
  print "PROFILE=$PROFILE"
  print "NEXT_ACTION=enguru-mac doctor"
else
  print "STATE=HOLD"
  print "HOLD=OPERATOR_PATH_BINDING_REQUIRED"
  print "NEXT_ACTION=source \"$PROFILE\""
  exit 3
fi
