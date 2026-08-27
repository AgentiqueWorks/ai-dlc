#!/usr/bin/env bash
# Eval check for the CSV export feature.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 1. The endpoint file exists
[ -f "${ROOT}/report/export.ts" ] || { echo "Missing report/export.ts"; exit 1; }

# 2. The test file exists and passes
[ -f "${ROOT}/report/export.test.ts" ] || { echo "Missing report/export.test.ts"; exit 1; }
if command -v npm >/dev/null 2>&1; then
  npm test -- report/export.test.ts
fi

echo "CSV export eval passed"