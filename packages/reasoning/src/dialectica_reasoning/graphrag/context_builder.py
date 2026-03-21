"""
Conflict Context Builder — Format graph retrieval results into LLM-ready context.

Structures retrieved entities and relationships into structured markdown sections
with citation markers [source:node_id] for provenance tracking.
Respects context window budget (default 30K chars).
"""
from __future__ import annotations

from dialectica_reasoning.graphrag.retriever import RetrievalResult


_SECTION_MODES = {
    "escalation": ["CONFLICT_STATE", "EVENTS", "ACTORS", "POWER", "CAUSAL_CHAINS"],
    "ripeness": ["CONFLICT_STATE", "PROCESSES", "TRUST", "ACTORS", "ISSUES"],
    "trust": ["TRUST", "ACTORS", "EVENTS", "POWER"],
    "power": ["POWER", "ACTORS", "ISSUES", "EVENTS"],
    "general": ["ACTORS", "CONFLICT_STATE", "ISSUES", "EVENTS", "NARRATIVES", "POWER", "TRUST", "CAUSAL_CHAINS"],
}

DEFAULT_BUDGET = 30_000


class ConflictContextBuilder:
    """
    Formats a RetrievalResult into structured text for LLM synthesis.

    Includes citation markers [source:node_id] for provenance tracking.
    Respects context window budget to avoid exceeding LLM limits.
    """

    def build_context(
        self,
        retrieval_result: RetrievalResult,
        mode: str = "general",
        max_chars: int = DEFAULT_BUDGET,
    ) -> str:
        """Build LLM-ready context string from retrieval result."""
        sections_order = _SECTION_MODES.get(mode, _SECTION_MODES["general"])
        nodes = retrieval_result.nodes
        edges = retrieval_result.edges

        # Partition nodes by type
        actors = [n for n in nodes if self._label(n) == "Actor"]
        conflicts = [n for n in nodes if self._label(n) == "Conflict"]
        events = [n for n in nodes if self._label(n) == "Event"]
        issues = [n for n in nodes if self._label(n) == "Issue"]
        interests = [n for n in nodes if self._label(n) == "Interest"]
        processes = [n for n in nodes if self._label(n) == "Process"]
        outcomes = [n for n in nodes if self._label(n) == "Outcome"]
        narratives = [n for n in nodes if self._label(n) == "Narrative"]
        power_nodes = [n for n in nodes if self._label(n) == "PowerDynamic"]
        trust_nodes = [n for n in nodes if self._label(n) == "TrustState"]

        section_builders = {
            "ACTORS": lambda: self._fmt_actors(actors, edges),
            "CONFLICT_STATE": lambda: self._fmt_conflict_state(conflicts),
            "ISSUES": lambda: self._fmt_issues(issues, interests),
            "EVENTS": lambda: self._fmt_events(events, edges),
            "NARRATIVES": lambda: self._fmt_narratives(narratives),
            "POWER": lambda: self._fmt_power(power_nodes, edges),
            "TRUST": lambda: self._fmt_trust(trust_nodes, edges),
            "CAUSAL_CHAINS": lambda: self._fmt_causal(events, edges),
            "PROCESSES": lambda: self._fmt_processes(processes, outcomes),
        }

        header = (
            f"# DIALECTICA CONFLICT CONTEXT\n"
            f"Workspace: {retrieval_result.workspace_id}\n"
            f"Query: {retrieval_result.query}\n"
            f"Nodes retrieved: {len(nodes)} | Edges: {len(edges)} | "
            f"Method: {retrieval_result.retrieval_method}\n"
        )

        parts: list[str] = [header]
        budget = max_chars - len(header)

        for section in sections_order:
            if budget <= 0:
                break
            builder = section_builders.get(section)
            if builder:
                section_text = builder()
                if section_text.strip():
                    if len(section_text) <= budget:
                        parts.append(section_text)
                        budget -= len(section_text)
                    else:
                        parts.append(section_text[:budget] + "\n[...section truncated...]")
                        budget = 0

        return "\n\n".join(parts)

    def _label(self, node: object) -> str:
        return getattr(node, "label", node.__class__.__name__)

    def _name(self, node: object) -> str:
        return getattr(node, "name", None) or getattr(node, "id", "unknown")

    def _cite(self, node: object) -> str:
        """Generate citation marker for provenance tracking."""
        nid = getattr(node, "id", "unknown")
        return f"[source:{nid}]"

    def _fmt_actors(self, actors: list, edges: list) -> str:
        if not actors:
            return ""
        lines = ["## ACTORS"]
        allied_map: dict[str, list[str]] = {}
        opposed_map: dict[str, list[str]] = {}
        for e in edges:
            etype = getattr(e, "type", "")
            if hasattr(etype, "value"):
                etype = etype.value
            if etype == "ALLIED_WITH":
                allied_map.setdefault(e.source_id, []).append(e.target_id)
            elif etype == "OPPOSED_TO":
                opposed_map.setdefault(e.source_id, []).append(e.target_id)
        for actor in actors[:15]:
            actor_type = getattr(actor, "actor_type", "unknown")
            desc = getattr(actor, "description", "")
            line = f"- **{self._name(actor)}** ({actor_type}) {self._cite(actor)}"
            if desc:
                line += f": {desc[:120]}"
            allies = allied_map.get(actor.id, [])
            opponents = opposed_map.get(actor.id, [])
            if allies:
                line += f" | Allied with: {', '.join(allies[:3])}"
            if opponents:
                line += f" | Opposed to: {', '.join(opponents[:3])}"
            lines.append(line)
        return "\n".join(lines)

    def _fmt_conflict_state(self, conflicts: list) -> str:
        if not conflicts:
            return ""
        lines = ["## CONFLICT STATE"]
        for c in conflicts[:3]:
            lines.append(f"### {self._name(c)} {self._cite(c)}")
            for attr in ["glasl_stage", "kriesberg_phase", "status", "violence_type", "scale", "domain"]:
                val = getattr(c, attr, None)
                if val is not None:
                    lines.append(f"- {attr}: {val}")
            desc = getattr(c, "description", "")
            if desc:
                lines.append(f"- Description: {desc[:200]}")
        return "\n".join(lines)

    def _fmt_issues(self, issues: list, interests: list) -> str:
        if not issues and not interests:
            return ""
        lines = ["## ISSUES & INTERESTS"]
        for issue in issues[:10]:
            incompatibility = getattr(issue, "incompatibility", "")
            lines.append(f"- **Issue**: {self._name(issue)} ({incompatibility}) {self._cite(issue)}")
            desc = getattr(issue, "description", "")
            if desc:
                lines.append(f"  {desc[:150]}")
        if interests:
            lines.append("\n**Interests:**")
            for interest in interests[:10]:
                lines.append(f"- {self._name(interest)} ({getattr(interest, 'interest_type', '')}) {self._cite(interest)}")
        return "\n".join(lines)

    def _fmt_events(self, events: list, edges: list) -> str:
        if not events:
            return ""
        lines = ["## EVENTS (chronological)"]
        sorted_events = sorted(
            events,
            key=lambda e: getattr(e, "occurred_at", None) or "",
        )
        for ev in sorted_events[:20]:
            ts = getattr(ev, "occurred_at", "unknown date")
            et = getattr(ev, "event_type", "event")
            severity = getattr(ev, "severity", 0)
            desc = getattr(ev, "description", "")
            line = f"- [{ts}] **{et}** (severity: {severity:.1f}) {self._cite(ev)}"
            if desc:
                line += f"\n  {desc[:150]}"
            lines.append(line)
        return "\n".join(lines)

    def _fmt_narratives(self, narratives: list) -> str:
        if not narratives:
            return ""
        lines = ["## NARRATIVES"]
        for n in narratives[:5]:
            frame = getattr(n, "frame_type", "")
            lines.append(f"- **{self._name(n)}** ({frame}) {self._cite(n)}")
            desc = getattr(n, "description", "")
            if desc:
                lines.append(f"  {desc[:200]}")
        return "\n".join(lines)

    def _fmt_power(self, power_nodes: list, edges: list) -> str:
        power_edges = [e for e in edges if str(getattr(e, "type", "")) == "HAS_POWER_OVER"]
        if not power_nodes and not power_edges:
            return ""
        lines = ["## POWER DYNAMICS"]
        for e in power_edges[:10]:
            props = getattr(e, "properties", {}) or {}
            domain = props.get("domain", "")
            magnitude = props.get("magnitude", getattr(e, "weight", 0) or 0)
            lines.append(f"- {e.source_id} HAS_POWER_OVER {e.target_id} [{domain}] (magnitude: {magnitude:.2f})")
        return "\n".join(lines)

    def _fmt_trust(self, trust_nodes: list, edges: list) -> str:
        trust_edges = [e for e in edges if str(getattr(e, "type", "")) == "TRUSTS"]
        if not trust_nodes and not trust_edges:
            return ""
        lines = ["## TRUST LEVELS"]
        for ts in trust_nodes[:10]:
            trustor = getattr(ts, "trustor_id", "?")
            trustee = getattr(ts, "trustee_id", "?")
            overall = getattr(ts, "overall_trust", 0.5)
            lines.append(f"- {trustor} -> {trustee}: overall_trust={overall:.2f} {self._cite(ts)}")
        return "\n".join(lines)

    def _fmt_causal(self, events: list, edges: list) -> str:
        caused_edges = [e for e in edges if str(getattr(e, "type", "")) == "CAUSED"]
        if not caused_edges:
            return ""
        lines = ["## CAUSAL CHAINS"]
        for e in caused_edges[:15]:
            lines.append(f"- {e.source_id} CAUSED {e.target_id}")
        return "\n".join(lines)

    def _fmt_processes(self, processes: list, outcomes: list) -> str:
        if not processes and not outcomes:
            return ""
        lines = ["## PROCESSES & OUTCOMES"]
        for p in processes[:5]:
            status = getattr(p, "status", "")
            lines.append(f"- **Process**: {self._name(p)} (status: {status}) {self._cite(p)}")
        for o in outcomes[:5]:
            outcome_type = getattr(o, "outcome_type", "")
            lines.append(f"- **Outcome**: {self._name(o)} ({outcome_type}) {self._cite(o)}")
        return "\n".join(lines)
