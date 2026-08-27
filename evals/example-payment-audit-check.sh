#!/usr/bin/env bash
# Eval check for payment audit logging.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 1. Audit module exists
[ -f "${ROOT}/payments/audit.rs" ] || { echo "Missing payments/audit.rs"; exit 1; }

# 2. No PII in the audit module
grep -qi "ssn\|email\|phone\|name" "${ROOT}/payments/audit.rs" && { echo "PII may be present in audit.rs"; exit 1; }

# 3. Required fields are present
grep -q "actor" "${ROOT}/payments/audit.rs" && grep -q "action" "${ROOT}/payments/audit.rs" && grep -q "entity" "${ROOT}/payments/audit.rs" && grep -q "timestamp" "${ROOT}/payments/audit.rs" || { echo "Missing required audit fields"; exit 1; }

echo "Payment audit eval passed"