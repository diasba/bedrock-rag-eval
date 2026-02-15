#!/usr/bin/env bash
# Smoke test for /query endpoint — tests answerable and no-answer questions.
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

echo "=== Test 1: Answerable question (should return citations) ==="
curl -s -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What metrics does Amazon Bedrock provide?"}' | python3 -m json.tool

echo ""
echo "=== Test 2: Question with include_context=true (debugging) ==="
curl -s -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Does Bedrock support streaming?", "include_context": true}' | python3 -m json.tool

echo ""
echo "=== Test 3: No-answer question (outside corpus) ==="
curl -s -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the price of AWS Lambda?"}' | python3 -m json.tool

echo ""
echo "Query smoke tests complete ✓"
