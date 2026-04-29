"""Download public-domain Project Gutenberg texts for DIALECTICA ingestion.

Examples:
    uv run python tools/download_gutenberg.py 1513 --output data/raw/romeo_juliet.txt
    uv run python tools/download_gutenberg.py 2600 --output data/raw/war_and_peace.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path

import httpx


def gutenberg_text_urls(book_id: str) -> list[str]:
    return [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
    ]


def download_text(book_id: str) -> str:
    last_error = ""
    for url in gutenberg_text_urls(book_id):
        try:
            response = httpx.get(url, timeout=30.0, follow_redirects=True)
            if response.status_code == 200 and response.text.strip():
                return response.text
            last_error = f"{url} returned HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            last_error = f"{url}: {exc}"
    raise RuntimeError(f"Could not download Project Gutenberg book {book_id}: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("book_id", help="Project Gutenberg numeric ID, e.g. 1513")
    parser.add_argument("--output", required=True, help="Output .txt path")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=0,
        help="Optional character limit for quick experiments",
    )
    args = parser.parse_args()

    text = download_text(args.book_id)
    if args.max_chars > 0:
        text = text[: args.max_chars]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(f"Wrote {len(text):,} characters to {output}")


if __name__ == "__main__":
    main()
