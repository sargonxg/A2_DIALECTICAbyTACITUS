"""Load local text documents for ingestion."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from dialectica.ontology.models import SourceDocument


@dataclass(frozen=True)
class LoadedDocument:
    document: SourceDocument
    text: str


def load_documents(
    path: str | Path,
    *,
    workspace_id: str,
    case_id: str,
) -> list[LoadedDocument]:
    root = Path(path)
    files = [root] if root.is_file() else sorted(root.glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"No .txt documents found at {root}")

    loaded: list[LoadedDocument] = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        source_id = f"source_{hashlib.sha1(str(file_path).encode()).hexdigest()[:12]}"
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        document = SourceDocument(
            workspace_id=workspace_id,
            case_id=case_id,
            source_id=source_id,
            title=file_path.stem.replace("_", " "),
            path=str(file_path),
            text_sha256=digest,
            trust_level="user_direct",
        )
        loaded.append(LoadedDocument(document=document, text=text))
    return loaded
