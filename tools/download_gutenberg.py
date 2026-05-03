"""Download public-domain Project Gutenberg texts for DIALECTICA ingestion.

Thin wrapper around ``dialectica_extraction.sources.gutenberg`` so the same
fetch/strip logic is shared by the API, the Databricks notebooks, and this CLI.

Examples:
    uv run python tools/download_gutenberg.py 1513 --output data/raw/romeo_juliet.txt
    uv run python tools/download_gutenberg.py 2600 --output data/raw/war_and_peace.txt
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dialectica_extraction.sources.gutenberg import fetch_gutenberg_text


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
    parser.add_argument(
        "--keep-boilerplate",
        action="store_true",
        help="Keep the *** START OF ... *** / *** END OF ... *** framing",
    )
    args = parser.parse_args()

    text = fetch_gutenberg_text(
        args.book_id,
        max_chars=args.max_chars,
        strip_boilerplate=not args.keep_boilerplate,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    print(f"Wrote {len(text):,} characters to {output}")


if __name__ == "__main__":
    main()
