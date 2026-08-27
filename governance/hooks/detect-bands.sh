#!/usr/bin/env bash
# Deterministic control-band detection.
#
# The playbook is explicit that detection is code, not a model: a version-
# controlled script computes the statistic, decides which band was breached, and
# only then invokes an agent with the tools that band allows. This script is the
# detection half. It ships with a file-based sample source so it runs and can be
# tested; wire `fetch_series` to your real metrics store.
#
# Usage:
#   detect-bands.sh --config bands.yaml [--metric NAME] [--output breach.json]
#
# Exit codes: 0 no breach, 10 breach detected (details on stdout and in --output).

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_lib.sh" 2>/dev/null || true

CONFIG="bands.yaml"
OUTPUT=""
ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --metric) ONLY="$2"; shift 2 ;;
    --output) OUTPUT="$2"; shift 2 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 64 ;;
  esac
done

[ -f "$CONFIG" ] || { echo "config not found: $CONFIG" >&2; exit 66; }

# fetch_series <metric-name> -> one numeric sample per line, oldest first.
#
# Replace this with a real query. Two worked examples:
#   Datadog:    curl -s -H "DD-API-KEY: $DATADOG_API_KEY" -H "DD-APPLICATION-KEY: $DATADOG_APP_KEY" \
#                 "https://api.datadoghq.com/api/v1/query?from=$FROM&to=$TO&query=$QUERY" \
#                 | jq -r '.series[0].pointlist[][1]'
#   Prometheus: curl -s --data-urlencode "query=$QUERY" "$PROM/api/v1/query_range" \
#                 | jq -r '.data.result[0].values[][1]'
fetch_series() {
  local metric="$1"
  local file="${BANDS_SAMPLE_DIR:-.ai-dlc/samples}/${metric}.txt"
  if [ -f "$file" ]; then
    cat "$file"
  else
    echo "no sample source for $metric; wire fetch_series to your metrics store" >&2
    return 1
  fi
}

# Metric names, in file order.
metrics="$(awk '/^  - name:/ {print $3}' "$CONFIG")"
[ -n "$ONLY" ] && metrics="$ONLY"

breaches="[]"
worst_tier=""

for metric in $metrics; do
  series="$(fetch_series "$metric" || true)"
  [ -n "$series" ] || continue

  read -r n mean sd latest <<EOF
$(printf '%s\n' "$series" | awk '
    { values[NR] = $1; sum += $1 }
    END {
      if (NR < 2) { print NR, 0, 0, values[NR]; exit }
      mean = sum / NR
      for (i = 1; i <= NR; i++) ss += (values[i] - mean) ^ 2
      printf "%d %.6f %.6f %.6f\n", NR, mean, sqrt(ss / (NR - 1)), values[NR]
    }')
EOF

  min_samples="$(awk '/^  min_samples:/ {print $2}' "$CONFIG")"
  min_samples="${min_samples:-30}"
  if [ "$n" -lt "$min_samples" ]; then
    echo "skip $metric: $n samples, need $min_samples" >&2
    continue
  fi

  sigma="$(awk -v l="$latest" -v m="$mean" -v s="$sd" 'BEGIN { if (s == 0) { print 0 } else { d = (l - m) / s; if (d < 0) d = -d; printf "%.2f", d } }')"
  tier=""
  awk -v x="$sigma" 'BEGIN { exit !(x >= 3) }' && tier="3sigma"
  [ -z "$tier" ] && awk -v x="$sigma" 'BEGIN { exit !(x >= 2) }' && tier="2sigma"
  [ -z "$tier" ] && awk -v x="$sigma" 'BEGIN { exit !(x >= 1) }' && tier="1sigma"
  [ -n "$tier" ] || continue

  echo "$metric: latest=$latest mean=$mean sd=$sd sigma=$sigma tier=$tier"
  entry="$(printf '{"metric":"%s","latest":%s,"mean":%s,"stddev":%s,"sigma":%s,"tier":"%s","n":%s}' \
    "$metric" "$latest" "$mean" "$sd" "$sigma" "$tier" "$n")"
  if command -v jq >/dev/null 2>&1; then
    breaches="$(printf '%s' "$breaches" | jq -c ". += [$entry]")"
  fi
  case "$tier" in
    3sigma) worst_tier="3sigma" ;;
    2sigma) [ "$worst_tier" = "3sigma" ] || worst_tier="2sigma" ;;
    1sigma) [ -n "$worst_tier" ] || worst_tier="1sigma" ;;
  esac
done

payload="$(printf '{"detected_at":"%s","config":"%s","tier":"%s","breaches":%s}' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CONFIG" "${worst_tier:-none}" "$breaches")"
[ -n "$OUTPUT" ] && printf '%s\n' "$payload" > "$OUTPUT"
[ -n "${GITHUB_OUTPUT:-}" ] && printf 'tier=%s\n' "${worst_tier:-none}" >> "$GITHUB_OUTPUT"

# 1-sigma is log-only by design: it must not wake an agent.
case "${worst_tier:-none}" in
  2sigma|3sigma) exit 10 ;;
  *) exit 0 ;;
esac
