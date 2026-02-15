#!/usr/bin/env python3
"""ChromaDB collection statistics — queries the running API container.

By default fetches stats from the API's GET /stats endpoint, which reads
the **actual** ChromaDB inside the Docker container.  Use --local to
fall back to opening the local chroma directory (only useful for
debugging outside Docker).

Usage:
    python scripts/chroma_stats.py                          # via API (default)
    python scripts/chroma_stats.py --api-url http://host:8000
    python scripts/chroma_stats.py --local                  # local ChromaDB
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def get_chroma_stats_via_api(api_url: str) -> dict:
    """Fetch collection stats from the running API container."""
    import httpx

    resp = httpx.get(f"{api_url}/stats", timeout=15.0)
    resp.raise_for_status()
    return resp.json()


def get_chroma_stats_local() -> dict:
    """Read stats directly from the local ChromaDB directory.

    ⚠ This reads the HOST's ./chroma/ directory, which is NOT the same
    as the Docker named volume.  Use only for debugging without Docker.
    """
    # Ensure project root is on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.db.chroma import get_collection  # noqa: E402

    collection = get_collection()
    total = collection.count()

    if total == 0:
        return {
            "total_chunks": 0,
            "by_content_type": {},
            "top_docs": [],
            "md_count": 0,
        }

    all_data = collection.get(include=["metadatas"])
    metadatas = all_data["metadatas"] or []

    type_counter: Counter[str] = Counter()
    doc_counter: Counter[str] = Counter()

    for meta in metadatas:
        ct = meta.get("content_type", "unknown")
        type_counter[ct] += 1
        doc_counter[meta.get("doc_id", "unknown")] += 1

    top_docs = [
        {"doc_id": doc_id, "chunks": count}
        for doc_id, count in doc_counter.most_common(5)
    ]

    return {
        "total_chunks": total,
        "by_content_type": dict(type_counter),
        "top_docs": top_docs,
        "md_count": type_counter.get("md", 0),
    }


def _print_stats(stats: dict) -> None:
    print("ChromaDB Collection Statistics")
    print("=" * 40)
    print(f"Total chunks: {stats['total_chunks']}")
    print()
    if stats.get("by_content_type"):
        print("By content type:")
        for ct, count in sorted(stats["by_content_type"].items()):
            print(f"  {ct:>6s}: {count}")
        print()
    if stats.get("top_docs"):
        print("Top documents by chunk count:")
        for entry in stats["top_docs"]:
            print(f"  {entry['doc_id']}: {entry['chunks']} chunks")
        print()
    print(json.dumps(stats, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="ChromaDB collection statistics")
    parser.add_argument(
        "--api-url", default="http://localhost:8000",
        help="Base URL of the running RAG API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--local", action="store_true", default=False,
        help="Read local ChromaDB instead of querying the API container",
    )
    args = parser.parse_args()

    if args.local:
        print("⚠  Reading LOCAL chroma directory (not the Docker container)\n")
        stats = get_chroma_stats_local()
    else:
        try:
            stats = get_chroma_stats_via_api(args.api_url)
        except Exception as exc:
            print(f"❌  Cannot reach API at {args.api_url}: {exc}")
            print("    Is the service running? Try: docker compose up")
            print("    Or use --local to read the host's chroma directory.\n")
            sys.exit(1)

    _print_stats(stats)


if __name__ == "__main__":
    main()
