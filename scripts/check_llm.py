#!/usr/bin/env python3
"""LLM readiness check — queries the running API container by default.

By default checks the LLM status reported by the container's GET /health
endpoint, which tests the CONTAINER'S Mistral connectivity (the one that
actually serves /query).  Use --local to check the HOST's Mistral key
instead (useful for debugging the eval-runner judge frameworks).

Usage:
    python scripts/check_llm.py                          # via API (default)
    python scripts/check_llm.py --api-url http://host:8000
    python scripts/check_llm.py --local                  # host-side check

Exit codes:
    0 — Mistral LLM is ready
    1 — Mistral LLM is NOT ready (prints diagnosis)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def check_via_api(api_url: str) -> dict:
    """Check LLM readiness via the running API container."""
    import httpx

    resp = httpx.get(f"{api_url}/health", timeout=15.0)
    resp.raise_for_status()
    data = resp.json()
    return {"ready": data.get("llm_ready", False), "reason": data.get("llm_reason", "unknown")}


def check_local() -> dict:
    """Check LLM readiness on the local host (same as old behaviour)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.generation.llm import check_llm_ready  # noqa: E402
    return check_llm_ready()


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Mistral LLM readiness")
    parser.add_argument(
        "--api-url", default="http://localhost:8000",
        help="Base URL of the running RAG API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--local", action="store_true", default=False,
        help="Check HOST's Mistral key instead of the container's",
    )
    args = parser.parse_args()

    if args.local:
        print("⚠  Checking HOST-side Mistral key (not the Docker container)\n")
        result = check_local()
    else:
        try:
            result = check_via_api(args.api_url)
        except Exception as exc:
            print(f"❌  Cannot reach API at {args.api_url}: {exc}")
            print("    Is the service running? Try: docker compose up")
            print("    Or use --local to check the host Mistral key.\n")
            sys.exit(1)

    if result["ready"]:
        print(f"✅  Mistral LLM ready — {result['reason']}")
        sys.exit(0)
    else:
        print(f"❌  Mistral LLM NOT ready — {result['reason']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
