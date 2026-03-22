"""
Hallucination Detector — GraphEval-inspired claim verification.

When the OAG engine generates a response:
  1. Extract atomic claims as (subject, predicate, object) triples
  2. For each triple, check if it's SUPPORTED by the workspace graph
  3. Score: SUPPORTED | UNSUPPORTED | CONTRADICTED
  4. Compute overall hallucination rate
  5. Flag responses above threshold
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum

from dialectica_graph import GraphClient


class ClaimStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"


@dataclass
class AtomicClaim:
    subject: str
    predicate: str
    obj: str
    raw_text: str = ""


@dataclass
class ClaimVerification:
    claim: AtomicClaim
    status: ClaimStatus
    evidence_ids: list[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class HallucinationReport:
    total_claims: int = 0
    supported: int = 0
    unsupported: int = 0
    contradicted: int = 0
    hallucination_rate: float = 0.0
    flagged: bool = False
    verifications: list[ClaimVerification] = field(default_factory=list)
    summary: str = ""


_HALLUCINATION_THRESHOLD = 0.3  # Flag if >30% claims unsupported/contradicted


class HallucinationDetector:
    """
    GraphEval-inspired hallucination detection for DIALECTICA.

    Verifies LLM-generated claims against the workspace knowledge graph.
    """

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def detect(
        self,
        response_text: str,
        workspace_id: str,
        threshold: float = _HALLUCINATION_THRESHOLD,
    ) -> HallucinationReport:
        """Full pipeline: extract claims → verify → score."""
        claims = await self.extract_claims(response_text)
        verifications = await self.verify_claims(claims, workspace_id)
        return await self.compute_hallucination_score(verifications, threshold)

    async def extract_claims(self, response_text: str) -> list[AtomicClaim]:
        """Extract atomic (subject, predicate, object) claims from response text."""
        claims: list[AtomicClaim] = []

        # Pattern 1: "X is Y" / "X has Y"
        patterns = [
            r"(\b[A-Z][A-Za-z\s]+)\s+is\s+([a-z][^.!?]+)",
            r"(\b[A-Z][A-Za-z\s]+)\s+has\s+([a-z][^.!?]+)",
            r"(\b[A-Z][A-Za-z\s]+)\s+(attacked|threatened|supported|cooperated with|allied with|opposed)\s+([A-Z][A-Za-z\s]+)",  # noqa: E501
        ]

        seen: set[tuple[str, str, str]] = set()
        for pattern in patterns:
            for match in re.finditer(pattern, response_text):
                groups = match.groups()
                if len(groups) == 2:
                    subject, obj = groups
                    predicate = "is"
                elif len(groups) == 3:
                    subject, predicate, obj = groups
                else:
                    continue
                subject = subject.strip()
                predicate = predicate.strip()
                obj = obj.strip()[:80]
                key = (subject.lower(), predicate.lower(), obj.lower())
                if key not in seen:
                    seen.add(key)
                    claims.append(
                        AtomicClaim(
                            subject=subject,
                            predicate=predicate,
                            obj=obj,
                            raw_text=match.group(0),
                        )
                    )

        # Fallback: extract capitalized entity pairs
        if not claims:
            entities = re.findall(r"\b([A-Z][A-Za-z\s]{2,})\b", response_text)
            entities = list(dict.fromkeys(e.strip() for e in entities))[:10]
            for entity in entities[:5]:
                claims.append(
                    AtomicClaim(
                        subject=entity,
                        predicate="mentioned_in_context",
                        obj="conflict_graph",
                        raw_text=entity,
                    )
                )

        return claims[:20]  # Cap at 20 claims

    async def verify_claims(
        self, claims: list[AtomicClaim], workspace_id: str
    ) -> list[ClaimVerification]:
        """Verify each claim against the workspace graph."""
        nodes = await self._gc.get_nodes(workspace_id, limit=500)
        edges = await self._gc.get_edges(workspace_id)

        # Build lookup indexes
        node_names: dict[str, list[str]] = {}  # normalized_name -> [node_ids]
        for n in nodes:
            name = getattr(n, "name", "") or ""
            normalized = name.lower().strip()
            node_names.setdefault(normalized, []).append(n.id)

        edge_pairs: set[tuple[str, str, str]] = set()
        for e in edges:
            edge_pairs.add((e.source_id, str(e.type).lower(), e.target_id))

        verifications: list[ClaimVerification] = []
        for claim in claims:
            subject_lower = claim.subject.lower()
            obj_lower = claim.obj.lower()

            # Check if subject exists in graph
            subject_ids = []
            for name, ids in node_names.items():
                if subject_lower in name or name in subject_lower:
                    subject_ids.extend(ids)

            if not subject_ids:
                verifications.append(
                    ClaimVerification(
                        claim=claim,
                        status=ClaimStatus.UNSUPPORTED,
                        explanation=f"Subject '{claim.subject}' not found in workspace graph.",
                    )
                )
                continue

            # Check if object exists
            obj_ids = []
            for name, ids in node_names.items():
                if obj_lower in name or name in obj_lower:
                    obj_ids.extend(ids)

            if claim.predicate in ("is", "mentioned_in_context", "has"):
                # For existence claims, subject existing is sufficient
                verifications.append(
                    ClaimVerification(
                        claim=claim,
                        status=ClaimStatus.SUPPORTED,
                        evidence_ids=subject_ids[:3],
                        explanation=f"Subject '{claim.subject}' exists in graph.",
                    )
                )
            elif obj_ids:
                # Check if edge exists between subject and object
                edge_found = any(
                    (s, p, o) in edge_pairs
                    for s in subject_ids
                    for o in obj_ids
                    for p in [claim.predicate.lower(), claim.predicate.upper()]
                )
                if edge_found:
                    verifications.append(
                        ClaimVerification(
                            claim=claim,
                            status=ClaimStatus.SUPPORTED,
                            evidence_ids=subject_ids[:2] + obj_ids[:2],
                            explanation="Relationship found in graph.",
                        )
                    )
                else:
                    verifications.append(
                        ClaimVerification(
                            claim=claim,
                            status=ClaimStatus.UNSUPPORTED,
                            explanation=f"Relationship '{claim.predicate}' between '{claim.subject}' and '{claim.obj}' not found.",  # noqa: E501
                        )
                    )
            else:
                verifications.append(
                    ClaimVerification(
                        claim=claim,
                        status=ClaimStatus.UNSUPPORTED,
                        explanation=f"Object '{claim.obj}' not found in workspace graph.",
                    )
                )

        return verifications

    async def compute_hallucination_score(
        self,
        verifications: list[ClaimVerification],
        threshold: float = _HALLUCINATION_THRESHOLD,
    ) -> HallucinationReport:
        """Compute overall hallucination rate and flag if above threshold."""
        if not verifications:
            return HallucinationReport(summary="No claims to verify.")

        total = len(verifications)
        supported = sum(1 for v in verifications if v.status == ClaimStatus.SUPPORTED)
        contradicted = sum(1 for v in verifications if v.status == ClaimStatus.CONTRADICTED)
        unsupported = total - supported - contradicted

        rate = (unsupported + contradicted) / total
        flagged = rate > threshold

        summary_parts = [
            f"{total} claims verified: {supported} supported, "
            f"{unsupported} unsupported, {contradicted} contradicted.",
            f"Hallucination rate: {rate:.1%}.",
        ]
        if flagged:
            summary_parts.append(
                f"⚠️ Response flagged: hallucination rate {rate:.1%} exceeds threshold {threshold:.1%}."  # noqa: E501
            )

        return HallucinationReport(
            total_claims=total,
            supported=supported,
            unsupported=unsupported,
            contradicted=contradicted,
            hallucination_rate=round(rate, 4),
            flagged=flagged,
            verifications=verifications,
            summary=" ".join(summary_parts),
        )
