"""
Project Gutenberg source loader.

Public-domain literary texts used as DIALECTICA conflict corpora. Provides:
- A curated catalog of 8 books spanning the two TACITUS domains
- URL resolution against Gutenberg's three known mirror layouts
- Text fetching with retry-style URL fallback
- Boilerplate stripping (the "*** START OF ... ***" / "*** END OF ... ***" blocks)

Used by:
- ``packages/api/src/dialectica_api/routers/gutenberg.py`` — REST endpoints
- ``tools/download_gutenberg.py`` — CLI tool (kept as a thin wrapper)
- Databricks notebooks (``notebooks/databricks/00_seed_open_books_to_delta.py``)
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

GUTENBERG_TIMEOUT_S = 30.0


@dataclass(frozen=True)
class GutenbergBook:
    """A curated Project Gutenberg book exposed to the picker UI."""

    book_id: str
    title: str
    author: str
    domain: str  # "human_friction" | "conflict_warfare"
    # geopolitical | armed | workplace | legal | environmental | commercial | literary
    subdomain: str
    summary: str
    estimated_words: int
    recommended_tier: str = "standard"

    def to_dict(self) -> dict[str, str | int]:
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "summary": self.summary,
            "estimated_words": self.estimated_words,
            "recommended_tier": self.recommended_tier,
        }


# Curated catalog. Mix of literary classics (already used as benchmarks) and
# non-fiction conflict primary sources. Word counts are approximate.
GUTENBERG_CATALOG: tuple[GutenbergBook, ...] = (
    GutenbergBook(
        book_id="1513",
        title="Romeo and Juliet",
        author="William Shakespeare",
        domain="human_friction",
        subdomain="literary",
        summary=(
            "Two feuding Veronese houses; an interpersonal conflict cascade culminating "
            "in deaths. Benchmark corpus for interpersonal escalation."
        ),
        estimated_words=26000,
        recommended_tier="standard",
    ),
    GutenbergBook(
        book_id="2600",
        title="War and Peace",
        author="Leo Tolstoy",
        domain="conflict_warfare",
        subdomain="armed",
        summary=(
            "Napoleonic invasion of Russia, 1805–1812. Benchmark corpus for "
            "macro-scale armed conflict and civilian impact."
        ),
        estimated_words=587000,
        recommended_tier="lite",
    ),
    GutenbergBook(
        book_id="2554",
        title="Crime and Punishment",
        author="Fyodor Dostoyevsky",
        domain="human_friction",
        subdomain="literary",
        summary=(
            "Psychological conflict and moral self-judgment. Benchmark corpus for "
            "intra-personal/intra-actor conflict."
        ),
        estimated_words=211000,
        recommended_tier="lite",
    ),
    GutenbergBook(
        book_id="6400",
        title="The History of the Peloponnesian War",
        author="Thucydides",
        domain="conflict_warfare",
        subdomain="armed",
        summary=(
            "Athens vs. Sparta, 431–404 BCE. Foundational primary source for "
            "interstate warfare, alliances, and ripeness."
        ),
        estimated_words=210000,
        recommended_tier="standard",
    ),
    GutenbergBook(
        book_id="7142",
        title="The Prince",
        author="Niccolò Machiavelli",
        domain="conflict_warfare",
        subdomain="geopolitical",
        summary=(
            "Treatise on power, statecraft, and the use of conflict. Useful for "
            "theory grounding (Glasl, Galtung)."
        ),
        estimated_words=37000,
        recommended_tier="standard",
    ),
    GutenbergBook(
        book_id="2680",
        title="Meditations",
        author="Marcus Aurelius",
        domain="human_friction",
        subdomain="literary",
        summary=(
            "Stoic reflections on interpersonal friction, restraint, and "
            "self-regulation. Useful for emotional-state extraction."
        ),
        estimated_words=43000,
        recommended_tier="standard",
    ),
    GutenbergBook(
        book_id="14500",
        title="The Art of War",
        author="Sun Tzu",
        domain="conflict_warfare",
        subdomain="armed",
        summary=(
            "Strategic doctrine; deception, terrain, force economy. Compact "
            "test bed for power and asymmetry analysis."
        ),
        estimated_words=13000,
        recommended_tier="standard",
    ),
    GutenbergBook(
        book_id="3300",
        title="The Wealth of Nations",
        author="Adam Smith",
        domain="human_friction",
        subdomain="commercial",
        summary=(
            "Commercial conflicts of interest, mercantile disputes, division "
            "of labor. Useful for commercial-domain extraction."
        ),
        estimated_words=370000,
        recommended_tier="lite",
    ),
)


def gutenberg_text_urls(book_id: str) -> list[str]:
    """Return the three URL layouts Gutenberg uses for plain-text mirrors."""
    return [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
    ]


def fetch_gutenberg_text(
    book_id: str,
    *,
    timeout: float = GUTENBERG_TIMEOUT_S,
    max_chars: int = 0,
    strip_boilerplate: bool = True,
) -> str:
    """Fetch a Project Gutenberg book's plain text.

    Tries each known URL layout and returns the first successful response.
    Raises ``RuntimeError`` if all attempts fail.

    Args:
        book_id: Numeric Gutenberg ID, e.g. ``"1513"``.
        timeout: Per-request timeout in seconds.
        max_chars: If > 0, truncate to this many characters (useful for
            quick demos against very long books).
        strip_boilerplate: Remove the ``*** START OF ... ***`` /
            ``*** END OF ... ***`` framing if present.
    """
    last_error = ""
    for url in gutenberg_text_urls(book_id):
        try:
            response = httpx.get(url, timeout=timeout, follow_redirects=True)
            if response.status_code == 200 and response.text.strip():
                text = response.text
                if strip_boilerplate:
                    text = strip_gutenberg_boilerplate(text)
                if max_chars > 0:
                    text = text[:max_chars]
                return text
            last_error = f"{url} returned HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            last_error = f"{url}: {exc}"
    raise RuntimeError(f"Could not download Project Gutenberg book {book_id}: {last_error}")


def strip_gutenberg_boilerplate(text: str) -> str:
    """Remove the standard Gutenberg header/footer blocks if present."""
    start_marker = "*** START OF"
    end_marker = "*** END OF"

    start_idx = text.find(start_marker)
    if start_idx >= 0:
        line_end = text.find("\n", start_idx)
        if line_end >= 0:
            text = text[line_end + 1 :]

    end_idx = text.find(end_marker)
    if end_idx >= 0:
        text = text[:end_idx]

    return text.strip()


def get_book(book_id: str) -> GutenbergBook | None:
    """Return the curated catalog entry for ``book_id``, if present."""
    for book in GUTENBERG_CATALOG:
        if book.book_id == book_id:
            return book
    return None
