#!/usr/bin/env bash
# Smoke test for POST /agent/research — auto-research agent endpoint.
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

echo "=== Agent Auto-Research: Amazon Bedrock Knowledge Bases ==="
curl -s -X POST "$BASE_URL/agent/research" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Amazon Bedrock Knowledge Bases",
    "max_subquestions": 5
  }' | python3 -m json.tool

echo ""
echo "Agent research smoke test complete ✓"
