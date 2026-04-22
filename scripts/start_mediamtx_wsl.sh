#!/usr/bin/env bash
set -euo pipefail

MEDIAMTX_PATH="${1:-/home/kirataiki/apps/mediamtx}"

if [ -d "$MEDIAMTX_PATH" ]; then
  cd "$MEDIAMTX_PATH"
  MEDIAMTX_BIN="./mediamtx"
else
  cd "$(dirname "$MEDIAMTX_PATH")"
  MEDIAMTX_BIN="$MEDIAMTX_PATH"
fi

echo "[INFO] Current dir: $(pwd)"
ls -l "$MEDIAMTX_BIN" 2>/dev/null || {
  echo "[ERROR] MediaMTX binary not found: $MEDIAMTX_BIN"
  exit 1
}

chmod +x "$MEDIAMTX_BIN" 2>/dev/null || true

echo "[INFO] Starting MediaMTX..."
echo "[INFO] Press Ctrl+C in this window to stop."
echo

exec stdbuf -oL -eL "$MEDIAMTX_BIN" 2>&1
