"""
Confidence Type Tagging — Every conclusion carries a confidence_type.

"deterministic" = from symbolic rules, treaty articles, legal constraints.
"probabilistic" = from GNN inference, LLM synthesis, KGE prediction.

The symbolic firewall (in reasoning package) ensures deterministic conclusions
are NEVER overridden by probabilistic predictions.
"""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, Field, model_validator
from ulid import ULID


def _ulid() -> str:
    return str(ULID())


class ConfidenceType(StrEnum):
    """Whether a conclusion is deterministic (symbolic) or probabilistic (neural)."""

    DETERMINISTIC = "deterministic"  # From symbolic rules, treaty articles, legal constraints
    PROBABILISTIC = "probabilistic"  # From GNN inference, LLM synthesis, KGE prediction


class Conclusion(BaseModel):
    """A conclusion reached by either symbolic rules or neural models.

    Deterministic conclusions (from symbolic rules) always have confidence=1.0
    and must cite a source_rule. Probabilistic conclusions cite a source_model.
    """

    conclusion_id: str = Field(default_factory=_ulid)
    conclusion_type: ConfidenceType
    statement: str
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: list[str] = Field(default_factory=list)  # Source rule IDs or model names
    source_rule: str | None = None  # e.g., "glasl_escalation_stage_3_to_4"
    source_model: str | None = None  # e.g., "compgcn-v1.2"
    workspace_id: str = ""
    tenant_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        if self.conclusion_type == ConfidenceType.DETERMINISTIC:
            if not self.source_rule:
                raise ValueError("Deterministic conclusions must cite a source_rule")
            self.confidence = 1.0  # Deterministic = infinite weight
        return self
