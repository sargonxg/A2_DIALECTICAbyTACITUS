"""Document source loaders for DIALECTICA ingestion."""

from dialectica_extraction.sources.gutenberg import (
    GUTENBERG_CATALOG,
    GutenbergBook,
    fetch_gutenberg_text,
    gutenberg_text_urls,
    strip_gutenberg_boilerplate,
)

__all__ = [
    "GUTENBERG_CATALOG",
    "GutenbergBook",
    "fetch_gutenberg_text",
    "gutenberg_text_urls",
    "strip_gutenberg_boilerplate",
]
