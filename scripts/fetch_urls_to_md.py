#!/usr/bin/env python3
"""Download URLs from a text file and store cleaned pages as Markdown files.

This script converts web docs into local `.md` files so `/ingest` can index them.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import ssl
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class _HTMLTextExtractor(HTMLParser):
    """Very small HTML -> text extractor (stdlib only)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._in_title = False
        self.title = ""
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        if tag in {"p", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in {"p", "li", "section", "article", "div"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            if self.title:
                self.title += " "
            self.title += text
        self.parts.append(text + " ")

    def text(self) -> str:
        raw = html.unescape("".join(self.parts))
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def _read_urls(path: Path) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        first = line.split()[0]
        if not first.startswith(("http://", "https://")):
            continue
        if first not in seen:
            seen.add(first)
            urls.append(first)
    return urls


def _slug_for_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    base = path.split("/")[-1] if path else "index"
    if not base:
        base = "index"
    base = re.sub(r"[^a-zA-Z0-9._-]+", "-", base).strip("-").lower()
    if not base:
        base = "page"
    short = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    return f"{base}-{short}.md"


def _fetch(url: str, timeout: float) -> tuple[str, str]:
    req = Request(
        url,
        headers={
            "User-Agent": "bedrock-rag-eval-corpus-builder/1.0 (+local)",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(req, timeout=timeout, context=_SSL_CONTEXT) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        body = resp.read().decode(charset, errors="replace")
    parser = _HTMLTextExtractor()
    parser.feed(body)
    title = parser.title.strip() or url
    text = parser.text()
    return title, text


def _build_ssl_context(insecure: bool) -> ssl.SSLContext:
    """Build SSL context with certifi CA bundle when available."""
    if insecure:
        return ssl._create_unverified_context()  # noqa: SLF001
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


_SSL_CONTEXT = _build_ssl_context(insecure=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download docs URLs into markdown files")
    parser.add_argument("--urls-file", default="data/corpus_raw/html/urls.txt")
    parser.add_argument("--output-dir", default="data/corpus_raw/md")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--min-chars", type=int, default=300)
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification (last resort).",
    )
    args = parser.parse_args()

    global _SSL_CONTEXT  # noqa: PLW0603
    _SSL_CONTEXT = _build_ssl_context(args.insecure)

    urls_path = Path(args.urls_file)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not urls_path.exists():
        print(f"ERROR: urls file not found: {urls_path}", file=sys.stderr)
        return 1

    urls = _read_urls(urls_path)
    if not urls:
        print(f"No URLs found in {urls_path}")
        return 0

    ok = 0
    failed = 0
    skipped = 0
    fetched_at = datetime.now(timezone.utc).isoformat()

    for i, url in enumerate(urls, start=1):
        name = _slug_for_url(url)
        out_path = out_dir / name
        try:
            title, text = _fetch(url, timeout=args.timeout)
            if len(text) < args.min_chars:
                skipped += 1
                print(f"[{i}/{len(urls)}] SKIP  {url} (too short: {len(text)} chars)")
                continue

            content = (
                f"# {title}\n\n"
                f"Source: {url}\n"
                f"Fetched-At: {fetched_at}\n\n"
                "---\n\n"
                f"{text}\n"
            )
            out_path.write_text(content, encoding="utf-8")
            ok += 1
            print(f"[{i}/{len(urls)}] OK    {url} -> {out_path}")
        except (HTTPError, URLError, TimeoutError) as exc:
            failed += 1
            print(f"[{i}/{len(urls)}] FAIL  {url} ({exc})")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"[{i}/{len(urls)}] FAIL  {url} ({type(exc).__name__}: {exc})")

    print("\nSummary")
    print(f"  urls_total: {len(urls)}")
    print(f"  saved:      {ok}")
    print(f"  skipped:    {skipped}")
    print(f"  failed:     {failed}")
    print(f"  output_dir: {out_dir}")
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
