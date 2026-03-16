"""
Query Engine — Natural language → graph operations → LLM synthesis.

Orchestrates the full DIALECTICA reasoning pipeline with SSE streaming support.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import AsyncIterator

from dialectica_graph import GraphClient
from dialectica_reasoning.graphrag.retriever import ConflictGraphRAGRetriever, RetrievalResult
from dialectica_reasoning.graphrag.context_builder import ConflictContextBuilder
from dialectica_reasoning.symbolic.constraint_engine import ConflictGrammarEngine
from dialectica_reasoning.symbolic.escalation import EscalationDetector
from dialectica_reasoning.symbolic.ripeness import RipenessScorer
from dialectica_reasoning.symbolic.trust_analysis import TrustAnalyzer
from dialectica_reasoning.symbolic.power_analysis import PowerMapper
from dialectica_reasoning.symbolic.causal_analysis import CausalAnalyzer
from dialectica_reasoning.symbolic.pattern_matching import PatternMatcher


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

@dataclass
class Citation:
    node_id: str
    node_name: str
    node_type: str
    relevance: float


@dataclass
class ReasoningStep:
    step: str
    status: str
    result_summary: str = ""


@dataclass
class AnalysisResponse:
    query: str
    workspace_id: str
    mode: str
    answer: str
    citations: list[Citation] = field(default_factory=list)
    reasoning_trace: list[ReasoningStep] = field(default_factory=list)
    escalation_stage: int | None = None
    ripeness_score: float | None = None
    patterns_detected: list[str] = field(default_factory=list)
    hallucination_risk: str = "unknown"
    confidence: float = 0.5


# ---------------------------------------------------------------------------
# Query Engine
# ---------------------------------------------------------------------------

class ConflictQueryEngine:
    """
    Main orchestrator for DIALECTICA analytical queries.

    Supports modes: general, escalation, ripeness, trust, power, causal, network.
    Yields SSE-compatible JSON strings when used via stream_analyze().
    """

    def __init__(
        self,
        graph_client: GraphClient,
        gemini_client: object | None = None,
    ) -> None:
        self._gc = graph_client
        self._gemini = gemini_client
        self._retriever = ConflictGraphRAGRetriever(graph_client)
        self._context_builder = ConflictContextBuilder()
        self._engine = ConflictGrammarEngine(graph_client)
        self._escalation = EscalationDetector(graph_client)
        self._ripeness = RipenessScorer(graph_client)
        self._trust = TrustAnalyzer(graph_client)
        self._power = PowerMapper(graph_client)
        self._causal = CausalAnalyzer(graph_client)
        self._patterns = PatternMatcher(graph_client)

    async def analyze(
        self,
        query: str,
        workspace_id: str,
        mode: str = "general",
        top_k: int = 20,
        hops: int = 2,
    ) -> AnalysisResponse:
        """Execute full analysis and return structured response."""
        trace: list[ReasoningStep] = []
        response = AnalysisResponse(
            query=query,
            workspace_id=workspace_id,
            mode=mode,
            answer="",
        )

        # Step 1: Retrieval
        try:
            retrieval = await self._retriever.retrieve(
                query=query,
                workspace_id=workspace_id,
                top_k=top_k,
                hops=hops,
            )
            trace.append(ReasoningStep(
                step="retrieval",
                status="complete",
                result_summary=f"Retrieved {len(retrieval.nodes)} nodes via {retrieval.retrieval_method}",
            ))
        except Exception as exc:
            trace.append(ReasoningStep(step="retrieval", status="error", result_summary=str(exc)))
            response.reasoning_trace = trace
            response.answer = "Retrieval failed. Check graph connectivity."
            return response

        # Step 2: Build context
        context = self._context_builder.build_context(retrieval, mode=mode)
        trace.append(ReasoningStep(
            step="context_build",
            status="complete",
            result_summary=f"Context built ({len(context)} chars, mode={mode})",
        ))

        # Step 3: Symbolic analysis (always run, mode-specific focus)
        symbolic_summary_parts: list[str] = []

        # Escalation
        if mode in ("escalation", "general"):
            try:
                glasl = await self._escalation.compute_glasl_stage(workspace_id)
                response.escalation_stage = glasl.stage.stage_number if glasl.stage else None
                symbolic_summary_parts.append(
                    f"Glasl stage: {glasl.stage} (confidence: {glasl.confidence:.2f})"
                )
                trace.append(ReasoningStep(
                    step="escalation_analysis",
                    status="complete",
                    result_summary=f"Stage={glasl.stage}, confidence={glasl.confidence}",
                ))
            except Exception:
                pass

        # Ripeness
        if mode in ("ripeness", "general"):
            try:
                ripe = await self._ripeness.compute_ripeness(workspace_id)
                response.ripeness_score = ripe.overall_score
                symbolic_summary_parts.append(
                    f"Ripeness: MHS={ripe.mhs_score:.2f}, MEO={ripe.meo_score:.2f}, "
                    f"overall={ripe.overall_score:.2f}, is_ripe={ripe.is_ripe}"
                )
                trace.append(ReasoningStep(
                    step="ripeness_analysis",
                    status="complete",
                    result_summary=f"Ripeness={ripe.overall_score:.2f}, ripe={ripe.is_ripe}",
                ))
            except Exception:
                pass

        # Pattern matching
        try:
            patterns = await self._patterns.detect_all(workspace_id)
            response.patterns_detected = [p.pattern_name for p in patterns if p.confidence > 0.4]
            if patterns:
                top_patterns = [f"{p.pattern_name}({p.confidence:.2f})" for p in patterns[:3]]
                symbolic_summary_parts.append(f"Patterns: {', '.join(top_patterns)}")
            trace.append(ReasoningStep(
                step="pattern_matching",
                status="complete",
                result_summary=f"{len(patterns)} patterns detected",
            ))
        except Exception:
            pass

        symbolic_summary = "\n".join(symbolic_summary_parts)

        # Step 4: Symbolic constraint check
        try:
            rule_report = await self._engine.evaluate_all_rules(workspace_id)
            critical_findings = [
                f for f in rule_report.findings
                if f.severity == "CRITICAL"
            ]
            trace.append(ReasoningStep(
                step="symbolic_rules",
                status="complete",
                result_summary=(
                    f"Score={rule_report.summary_score:.2f}, "
                    f"{len(critical_findings)} critical findings"
                ),
            ))
        except Exception:
            rule_report = None

        # Step 5: LLM synthesis
        if self._gemini is not None:
            try:
                prompt = self._build_synthesis_prompt(query, context, symbolic_summary, mode)
                answer = await self._call_gemini(prompt)
                trace.append(ReasoningStep(
                    step="synthesis",
                    status="complete",
                    result_summary="LLM synthesis complete",
                ))
            except Exception as exc:
                answer = self._fallback_answer(query, retrieval, symbolic_summary)
                trace.append(ReasoningStep(
                    step="synthesis",
                    status="fallback",
                    result_summary=f"LLM unavailable: {exc}",
                ))
        else:
            answer = self._fallback_answer(query, retrieval, symbolic_summary)
            trace.append(ReasoningStep(
                step="synthesis",
                status="no_llm",
                result_summary="No LLM configured — returning symbolic summary",
            ))

        # Step 6: Citations
        citations = [
            Citation(
                node_id=node.id,
                node_name=getattr(node, "name", node.id),
                node_type=getattr(node, "label", node.__class__.__name__),
                relevance=retrieval.scores.get(node.id, 0.0),
            )
            for node in retrieval.nodes[:10]
        ]

        response.answer = answer
        response.citations = citations
        response.reasoning_trace = trace
        response.confidence = min(1.0, len(citations) * 0.1 + 0.2)
        return response

    async def stream_analyze(
        self,
        query: str,
        workspace_id: str,
        mode: str = "general",
    ) -> AsyncIterator[str]:
        """Stream analysis steps as SSE-compatible JSON strings."""
        yield json.dumps({"step": "started", "query": query, "mode": mode})

        yield json.dumps({"step": "retrieval", "status": "started"})
        retrieval = await self._retriever.retrieve(query, workspace_id)
        yield json.dumps({
            "step": "retrieval",
            "status": "complete",
            "nodes_found": len(retrieval.nodes),
        })

        yield json.dumps({"step": "symbolic", "status": "started"})
        glasl = await self._escalation.compute_glasl_stage(workspace_id)
        ripe = await self._ripeness.compute_ripeness(workspace_id)
        patterns = await self._patterns.detect_all(workspace_id)
        yield json.dumps({
            "step": "symbolic",
            "status": "complete",
            "glasl_stage": str(glasl.stage),
            "ripeness": ripe.overall_score,
            "patterns": [p.pattern_name for p in patterns if p.confidence > 0.4],
        })

        yield json.dumps({"step": "synthesis", "status": "started"})
        context = self._context_builder.build_context(retrieval, mode=mode)
        symbolic_summary = (
            f"Glasl stage: {glasl.stage}\n"
            f"Ripeness: {ripe.overall_score:.2f} (ripe={ripe.is_ripe})\n"
            f"Patterns: {', '.join(p.pattern_name for p in patterns[:3])}"
        )
        if self._gemini is not None:
            try:
                prompt = self._build_synthesis_prompt(query, context, symbolic_summary, mode)
                answer = await self._call_gemini(prompt)
            except Exception:
                answer = self._fallback_answer(query, retrieval, symbolic_summary)
        else:
            answer = self._fallback_answer(query, retrieval, symbolic_summary)

        citations = [
            {"node_id": n.id, "node_name": getattr(n, "name", n.id), "score": retrieval.scores.get(n.id, 0)}
            for n in retrieval.nodes[:10]
        ]
        yield json.dumps({
            "step": "complete",
            "answer": answer,
            "citations": citations,
            "escalation_stage": getattr(glasl.stage, "stage_number", None),
            "ripeness_score": ripe.overall_score,
            "patterns_detected": [p.pattern_name for p in patterns if p.confidence > 0.4],
        })

    def _build_synthesis_prompt(
        self,
        query: str,
        context: str,
        symbolic_summary: str,
        mode: str,
    ) -> str:
        return f"""You are DIALECTICA, a neurosymbolic conflict intelligence system.
Analyze the following conflict situation and answer the user's query.
Base your analysis ONLY on the provided context. Cite specific nodes by name.

## USER QUERY
{query}

## SYMBOLIC ANALYSIS
{symbolic_summary}

## CONFLICT CONTEXT
{context}

## INSTRUCTIONS
- Answer the query directly, grounding every claim in the context
- Reference specific actors, events, and relationships by name
- If the mode is '{mode}', focus your analysis accordingly
- Note confidence levels for key assertions
- End with 1-2 actionable recommendations

## RESPONSE
"""

    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API if client is available."""
        if hasattr(self._gemini, "generate"):
            result = await self._gemini.generate(prompt)
            return str(result)
        return prompt[:500]  # Fallback

    def _fallback_answer(
        self,
        query: str,
        retrieval: RetrievalResult,
        symbolic_summary: str,
    ) -> str:
        node_names = [getattr(n, "name", n.id) for n in retrieval.nodes[:5]]
        return (
            f"**Query**: {query}\n\n"
            f"**Symbolic Analysis**:\n{symbolic_summary}\n\n"
            f"**Graph Evidence** ({len(retrieval.nodes)} nodes retrieved):\n"
            f"Key entities: {', '.join(node_names)}\n\n"
            f"*Note: LLM synthesis unavailable. Configure GEMINI_PRO_MODEL for full analysis.*"
        )
