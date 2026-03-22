"""
GCS Document Loader — Download and extract text from GCS-hosted documents.

Supports PDF (pymupdf), DOCX (python-docx), TXT, HTML, and Markdown.
"""

from __future__ import annotations

import io
import logging
import os

logger = logging.getLogger(__name__)

GCS_BUCKET = os.getenv("GCS_DOCUMENTS_BUCKET", "dialectica-documents")


async def load_document_from_gcs(gcs_uri: str) -> str:
    """Download a document from GCS and extract plain text.

    Args:
        gcs_uri: GCS URI like gs://bucket/path/to/file.pdf

    Returns:
        Extracted plain text content.
    """
    bucket_name, blob_path = _parse_gcs_uri(gcs_uri)

    try:
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        content = blob.download_as_bytes()
    except Exception as e:
        logger.error("Failed to download %s: %s", gcs_uri, e)
        raise

    ext = blob_path.rsplit(".", 1)[-1].lower() if "." in blob_path else ""
    return extract_text(content, ext, filename=blob_path)


def extract_text(content: bytes, extension: str, filename: str = "") -> str:
    """Extract plain text from document bytes based on file extension."""
    if extension == "pdf":
        return _extract_pdf(content)
    elif extension == "docx":
        return _extract_docx(content)
    elif extension in ("html", "htm"):
        return _extract_html(content)
    elif extension in ("txt", "md", "markdown", "text"):
        return content.decode("utf-8", errors="replace")
    else:
        logger.warning("Unknown extension '%s' for %s, treating as text", extension, filename)
        return content.decode("utf-8", errors="replace")


def _extract_pdf(content: bytes) -> str:
    """Extract text from PDF using pymupdf."""
    try:
        import pymupdf

        doc = pymupdf.open(stream=content, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n\n".join(text_parts)
    except ImportError:
        logger.warning("pymupdf not installed, trying pypdf")
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(content))
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError as err:
            raise ImportError("Install pymupdf or pypdf for PDF support") from err


def _extract_docx(content: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError as err:
        raise ImportError("Install python-docx for DOCX support") from err


def _extract_html(content: bytes) -> str:
    """Extract text from HTML by stripping tags."""
    import re

    text = content.decode("utf-8", errors="replace")
    # Strip HTML tags
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    """Parse gs://bucket/path into (bucket, path)."""
    if uri.startswith("gs://"):
        uri = uri[5:]
    parts = uri.split("/", 1)
    bucket = parts[0]
    path = parts[1] if len(parts) > 1 else ""
    return bucket, path
