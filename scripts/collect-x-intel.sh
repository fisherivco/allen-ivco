#!/bin/bash
# collect-x-intel.sh — Search X → Filter → Store pipeline for IVCO
# Version: 3.0.0 (2026-02-15)
#
# Pipeline: ivco-xsearch (X API v2) → ivco-filter (score+discard) → ivco-collect (POST to CMS, file fallback)
# Runs via launchd: 07:00, 13:00, 20:00 (Asia/Taipei)
#
# Changelog:
#   v1.0.0 (2026-02-08) — Initial: bird → ivco-collect (raw, no filtering)
#   v2.0.0 (2026-02-10) — Added ivco-filter between bird and ivco-collect
#   v2.1.0 (2026-02-11) — Fix: pass --auth-token/--ct0 explicitly to bird
#   v3.0.0 (2026-02-15) — Replace bird with ivco-xsearch (official X API v2)
#                          Remove cookie dependencies (no more BIRD_AUTH_TOKEN/BIRD_CT0)
#                          Add queue flush at start (retry failed POSTs from previous runs)
#                          Auth: X_BEARER_TOKEN from ~/.config/env/global.env
#
# Rollback:
#   cp ~/fisher/memory/backups/collect-x-intel.sh.bak.20260215 \
#      ~/fisher/projects/allen-ivco/scripts/collect-x-intel.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/Users/allenchenmac/fisher/memory/daily"
LOG_FILE="${LOG_DIR}/x-intel-collect.log"
TMP_DIR="/tmp/ivco-collect"
QUEUE_DIR="/tmp/ivco-collect-queue"
PAYLOAD_API="http://localhost:3000/api/company-events"
PAYPAL_COMPANY_ID=2
MAX_RESULTS=10

# Direct paths
PYTHON="/usr/local/bin/python3"
IVCO_XSEARCH="${SCRIPT_DIR}/ivco-xsearch"
IVCO_FILTER="/Library/Frameworks/Python.framework/Versions/3.11/bin/ivco-filter"
FILTER_CONFIG="${SCRIPT_DIR}/../cli/ivco-filter/config/filter-rules.json"

mkdir -p "$TMP_DIR" "$LOG_DIR" "$QUEUE_DIR"

# Load X API bearer token from secure location
X_ENV="$HOME/.config/env/global.env"
if [ -f "$X_ENV" ]; then
  export X_BEARER_TOKEN=$(grep '^X_BEARER_TOKEN=' "$X_ENV" | cut -d= -f2- || true)
else
  echo "[$(date -Iseconds)] ERROR: global.env not found at $X_ENV" >> "$LOG_FILE"
  exit 1
fi

if [ -z "$X_BEARER_TOKEN" ]; then
  echo "[$(date -Iseconds)] ERROR: X_BEARER_TOKEN is empty in $X_ENV" >> "$LOG_FILE"
  exit 1
fi

# Verify ivco-xsearch and ivco-filter are available
if [ ! -x "$IVCO_XSEARCH" ]; then
  echo "[$(date -Iseconds)] ERROR: ivco-xsearch not found at $IVCO_XSEARCH" >> "$LOG_FILE"
  exit 1
fi
if [ ! -x "$IVCO_FILTER" ]; then
  echo "[$(date -Iseconds)] ERROR: ivco-filter not found at $IVCO_FILTER" >> "$LOG_FILE"
  exit 1
fi

log() {
  echo "[$(date -Iseconds)] $1" >> "$LOG_FILE"
}

log "=== Collection run started (v3.0.0 — X API v2) ==="

# Step 0: Flush queue — retry any failed POSTs from previous runs
queue_count=$(find "$QUEUE_DIR" -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$queue_count" -gt 0 ]; then
  log "Flushing queue: ${queue_count} pending events"
  flushed=0
  for qfile in "$QUEUE_DIR"/*.json; do
    [ -f "$qfile" ] || continue
    result=$("$PYTHON" "$SCRIPT_DIR/ivco-collect" \
      --input "$qfile" \
      --api "$PAYLOAD_API" \
      --company-id "$PAYPAL_COMPANY_ID" \
      --keyword "queue-retry" \
      --json 2>> "$LOG_FILE")
    # Only delete queue file if all events stored and zero errors/queued
    q_stored=$("$PYTHON" -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('stored',0))" "$result" 2>/dev/null || echo "0")
    q_errors=$("$PYTHON" -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('errors',0)+d.get('queued',0))" "$result" 2>/dev/null || echo "1")
    if [ "$q_stored" -gt 0 ] && [ "$q_errors" -eq 0 ] 2>/dev/null; then
      rm -f "$qfile"
      flushed=$((flushed + q_stored))
    fi
  done
  log "  Queue flush: ${flushed} events recovered"
fi

total_raw=0
total_filtered=0
total_stored=0

for keyword in "paypal" "PYPL"; do
  log "Searching: ${keyword}"

  # Step 1: ivco-xsearch → raw JSON (official X API v2, bearer token auth)
  "$PYTHON" "$IVCO_XSEARCH" "$keyword" -n "$MAX_RESULTS" \
    > "$TMP_DIR/raw.json" 2>> "$LOG_FILE" || echo "[]" > "$TMP_DIR/raw.json"

  raw_count=$("$PYTHON" -c "import json; print(len(json.load(open('$TMP_DIR/raw.json'))))" 2>/dev/null || echo "0")
  log "  Raw tweets: ${raw_count}"
  total_raw=$((total_raw + raw_count))

  # Step 2: ivco-filter → scored + filtered JSON
  "$IVCO_FILTER" \
    --config "$FILTER_CONFIG" \
    --input "$TMP_DIR/raw.json" \
    --output "$TMP_DIR/filtered.json" \
    --verbose 2>> "$LOG_FILE" || {
    log "  WARNING: ivco-filter failed, falling back to raw tweets"
    cp "$TMP_DIR/raw.json" "$TMP_DIR/filtered.json"
  }

  filtered_count=$("$PYTHON" -c "import json; print(len(json.load(open('$TMP_DIR/filtered.json'))))" 2>/dev/null || echo "0")
  discarded=$((raw_count - filtered_count))
  log "  After filter: ${filtered_count} kept, ${discarded} discarded"
  total_filtered=$((total_filtered + filtered_count))

  # Step 3: ivco-collect → POST to Payload CMS (with file queue fallback)
  stored=$("$PYTHON" "$SCRIPT_DIR/ivco-collect" \
    --input "$TMP_DIR/filtered.json" \
    --api "$PAYLOAD_API" \
    --company-id "$PAYPAL_COMPANY_ID" \
    --keyword "$keyword" \
    --queue-dir "$QUEUE_DIR" 2>> "$LOG_FILE")

  log "  Stored: ${stored} tweets"
  total_stored=$((total_stored + stored))
done

rm -f "$TMP_DIR/raw.json" "$TMP_DIR/filtered.json"
log "=== Collection complete: ${total_raw} raw → ${total_filtered} filtered → ${total_stored} stored ==="
