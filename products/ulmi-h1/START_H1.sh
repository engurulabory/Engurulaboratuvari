#!/usr/bin/env bash
# H1 isolated portable HTML/HTTP product launcher. Not an OSi installation.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ENGURU_H1_STATE_HOME="${ENGURU_H1_STATE_HOME:-$ROOT/STATE}"
export ENGURU_USTA_PORT="${ENGURU_USTA_PORT:-18990}"
mkdir -p "$ENGURU_H1_STATE_HOME"
printf 'ULMi H1 gerçek HTML: http://127.0.0.1:%s/\n' "$ENGURU_USTA_PORT"
exec python3 -B "$ROOT/PRODUCT/server.py"
