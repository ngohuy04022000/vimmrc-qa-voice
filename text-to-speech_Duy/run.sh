#!/usr/bin/env bash
# ==============================================================================
# Cross-platform runner script for macOS & Linux (and Windows Git Bash)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Tìm lệnh Python phù hợp
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[Lỗi] Không tìm thấy Python trên hệ thống!" >&2
    exit 1
fi

"$PY_CMD" run.py "$@"

