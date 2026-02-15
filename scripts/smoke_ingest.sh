#!/usr/bin/env bash
# Smoke test: hit /health then /ingest and print results.
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

echo "=== Health check ==="
curl -s "$BASE_URL/health" | python3 -m json.tool

echo ""
echo "=== Ingest corpus_raw ==="
curl -s -X POST "$BASE_URL/ingest" \
  -H "Content-Type: application/json" \
  -d '{"path": "data/corpus_raw"}' | python3 -m json.tool

echo ""
echo "=== Health check (post-ingest) ==="
curl -s "$BASE_URL/health" | python3 -m json.tool

echo ""
echo "Smoke test passed ✓"
