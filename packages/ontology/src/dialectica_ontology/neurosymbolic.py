"""
Neurosymbolic Architecture Configuration — TACITUS four-layer system.

Converts the NEUROSYMBOLIC dict from ontology.py into structured configuration:
  NeurosymbolicArchitecture: Full architecture description
  SymbolicLayer: All 9 symbolic components (deterministic rules)
  NeuralLayer: All 7 neural components + embedding specs
  BridgeProtocol: Reason-then-embed interaction pattern
  ScientificRisks: Risk categories + mitigations

Architecture layers:
  1. Neural Ingestion (GLiNER + Gemini)
  2. Symbolic Representation (Conflict Grammar + Spanner Graph)
  3. Reasoning/Inference (Rules + GraphRAG + GNN)
  4. Decision Support (Agents + Human loop)

Theoretical basis: TACITUS Core Ontology v2.0 (see ontology.py NEUROSYMBOLIC{}).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# ─── Symbolic Layer ────────────────────────────────────────────────────────────


class SymbolicComponent(BaseModel):
    """A single deterministic rule or component in the symbolic layer."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Short identifier for the rule component")
    description: str = Field(..., description="What this component does")
    deterministic: bool = Field(
        default=True,
        description="Whether this component produces deterministic output",
    )


class SymbolicLayer(BaseModel):
    """Deterministic reasoning via Cypher queries and rule-based inference.

    All 9 symbolic components fire *before* neural inference.
    Their conclusions are never overridden by probabilistic predictions.
    """

    model_config = ConfigDict(frozen=True)

    description: str = Field(
        default="Deterministic reasoning via Cypher queries and rule-based inference",
    )
    query_language: str = Field(
        default="Cypher (Neo4j/FalkorDB) + custom rule engine",
    )
    components: tuple[SymbolicComponent, ...] = Field(
        default=(
            SymbolicComponent(
                name="glasl_escalation_rules",
                description=(
                    "Glasl escalation rules: stage transition triggers "
                    "and intervention recommendations"
                ),
            ),
            SymbolicComponent(
                name="ury_brett_goldberg_loopback",
                description=(
                    "Ury/Brett/Goldberg loop-back rules: "
                    "failed power contest recommends return to interests"
                ),
            ),
            SymbolicComponent(
                name="trust_breach_detection",
                description=(
                    "Trust breach detection: integrity drop > 0.3 triggers alert "
                    "(Mayer/Davis/Schoorman model)"
                ),
            ),
            SymbolicComponent(
                name="ucdp_conflict_classification",
                description=(
                    "UCDP conflict classification: 25-death threshold, "
                    "incompatibility typing (territory vs. government)"
                ),
            ),
            SymbolicComponent(
                name="temporal_logic",
                description=(
                    "Temporal logic via Allen's interval algebra on valid_from / valid_to intervals"
                ),
            ),
            SymbolicComponent(
                name="norm_violation_detection",
                description=(
                    "Norm violation detection: "
                    "Event -[VIOLATES]-> Norm chains in the conflict graph"
                ),
            ),
            SymbolicComponent(
                name="batna_zopa_computation",
                description=(
                    "BATNA comparison: reservation values across parties "
                    "yield ZOPA (Zone of Possible Agreement) computation"
                ),
            ),
            SymbolicComponent(
                name="causal_chain_analysis",
                description=(
                    "Causal chain analysis: Event -[CAUSED]-> Event path traversal "
                    "for escalation pattern detection"
                ),
            ),
            SymbolicComponent(
                name="cross_case_structural_similarity",
                description=(
                    "Cross-case structural similarity: subgraph isomorphism "
                    "for pattern recognition across conflict cases"
                ),
            ),
        ),
        description="All 9 deterministic symbolic components",
    )

    @property
    def component_names(self) -> list[str]:
        """Return list of component short names."""
        return [c.name for c in self.components]

    def get_component(self, name: str) -> SymbolicComponent | None:
        """Lookup a component by short name."""
        for c in self.components:
            if c.name == name:
                return c
        return None


# ─── Neural Layer ──────────────────────────────────────────────────────────────


class NeuralComponent(BaseModel):
    """A single probabilistic inference component in the neural layer."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Short identifier for the neural component")
    description: str = Field(..., description="What this component does")
    probabilistic: bool = Field(
        default=True,
        description="Whether this component produces probabilistic output",
    )


class NeuralLayer(BaseModel):
    """Probabilistic inference via GNN embeddings and link prediction.

    Neural components fill gaps left by symbolic rules.  Their predictions
    require human-in-the-loop validation before promotion to symbolic rules.
    """

    model_config = ConfigDict(frozen=True)

    description: str = Field(
        default="Probabilistic inference via GNN embeddings and link prediction",
    )
    components: tuple[NeuralComponent, ...] = Field(
        default=(
            NeuralComponent(
                name="r_gat",
                description=(
                    "R-GAT (Relational Graph Attention Network) for heterogeneous graph embedding"
                ),
            ),
            NeuralComponent(
                name="rotate",
                description=(
                    "RotatE for knowledge graph link prediction: "
                    "predict future alliances and oppositions"
                ),
            ),
            NeuralComponent(
                name="temporal_attention",
                description=("Temporal attention mechanism for trajectory forecasting"),
            ),
            NeuralComponent(
                name="narrative_similarity",
                description=("Narrative similarity via embedding cosine distance"),
            ),
            NeuralComponent(
                name="conflict_pattern_matching",
                description=(
                    "Conflict pattern matching via subgraph isomorphism and neural fingerprinting"
                ),
            ),
            NeuralComponent(
                name="escalation_prediction",
                description=(
                    "Escalation prediction: GNN trained on historical (Event, Event, CAUSED) chains"
                ),
            ),
            NeuralComponent(
                name="outcome_prediction",
                description=(
                    "Outcome prediction: predict resolution probability by dispute profile"
                ),
            ),
        ),
        description="All 7 probabilistic neural components",
    )
    embedding_nodes: tuple[str, ...] = Field(
        default=("Actor", "Conflict", "Event", "Narrative"),
        description="Node types that receive learned embeddings",
    )
    recommended_dim: int = Field(
        default=128,
        description="Recommended embedding dimensionality",
    )
    training_approach: str = Field(
        default="reason-then-embed",
        description=(
            "OWL inference materializes edges first, "
            "then embed the enriched graph (reason-then-embed)"
        ),
    )

    @property
    def component_names(self) -> list[str]:
        """Return list of component short names."""
        return [c.name for c in self.components]

    def get_component(self, name: str) -> NeuralComponent | None:
        """Lookup a component by short name."""
        for c in self.components:
            if c.name == name:
                return c
        return None


# ─── Bridge Protocol ───────────────────────────────────────────────────────────


class BridgeStep(BaseModel):
    """A single step in the reason-then-embed bridge protocol."""

    model_config = ConfigDict(frozen=True)

    step: int = Field(..., ge=1, le=4, description="Step number (1-4)")
    description: str


class ScientificRisk(BaseModel):
    """A known scientific risk with its mitigation strategy."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Risk category identifier")
    risk: str = Field(..., description="What can go wrong")
    mitigation: str = Field(..., description="How the architecture mitigates this risk")


class BridgeProtocol(BaseModel):
    """How symbolic and neural layers interact (reason-then-embed pipeline).

    The 4-step pattern ensures deterministic conclusions are never overridden
    by probabilistic inference.  Human-in-the-loop validates neural suggestions
    before they are promoted to new symbolic rules.
    """

    model_config = ConfigDict(frozen=True)

    description: str = Field(
        default=("How symbolic and neural layers interact (reason-then-embed pipeline)"),
    )
    pattern: tuple[BridgeStep, ...] = Field(
        default=(
            BridgeStep(
                step=1,
                description=("Symbolic rules fire first (deterministic, explainable)"),
            ),
            BridgeStep(
                step=2,
                description=("Neural layer fills gaps (predictions, similarities, anomalies)"),
            ),
            BridgeStep(
                step=3,
                description=("Human-in-the-loop validates neural suggestions"),
            ),
            BridgeStep(
                step=4,
                description=("Validated suggestions become new symbolic rules (learning loop)"),
            ),
        ),
        description="The 4-step reason-then-embed bridge pattern",
    )
    key_principle: str = Field(
        default=(
            "Deterministic conclusions are NEVER overridden by probabilistic "
            "inference. The symbolic layer provides the auditability and "
            "accountability required in high-stakes conflict domains."
        ),
        description="Inviolable architectural principle",
    )
    scientific_risks: tuple[ScientificRisk, ...] = Field(
        default=(
            ScientificRisk(
                name="ontology_loss",
                risk=("If schema is too rigid, it flattens meaningful ambiguity."),
                mitigation=("Controlled vocabularies, confidence scores, preserved source_text."),
            ),
            ScientificRisk(
                name="extraction_error_propagation",
                risk=("LLM misreads can look authoritative in symbolic layer."),
                mitigation=("Confidence scores, HITL validation, stated/inferred distinction."),
            ),
            ScientificRisk(
                name="normative_overreach",
                risk=(
                    "System may identify strategic efficiency without "
                    "understanding procedural fairness or political legitimacy."
                ),
                mitigation=("TACITUS is decision-support, not autonomous resolution."),
            ),
        ),
        description="Known scientific risks with mitigations",
    )

    def get_risk(self, name: str) -> ScientificRisk | None:
        """Lookup a scientific risk by name."""
        for r in self.scientific_risks:
            if r.name == name:
                return r
        return None


# ─── Four-Layer Architecture Description ──────────────────────────────────────


class ArchitectureLayer(BaseModel):
    """One of the four layers in the TACITUS neurosymbolic architecture."""

    model_config = ConfigDict(frozen=True)

    layer: int = Field(..., ge=1, le=4)
    name: str
    description: str


# ─── Top-Level Architecture ───────────────────────────────────────────────────


class NeurosymbolicArchitecture(BaseModel):
    """Complete TACITUS neurosymbolic architecture configuration.

    Combines SymbolicLayer, NeuralLayer, and BridgeProtocol into a single
    validated configuration object.  The four_layers field describes the
    end-to-end pipeline from text ingestion to decision support.

    Usage::

        arch = NeurosymbolicArchitecture()
        # inspect symbolic components
        arch.symbolic.component_names
        # inspect neural embedding spec
        arch.neural.recommended_dim
        # check bridge principle
        arch.bridge.key_principle
    """

    model_config = ConfigDict(frozen=True)

    architecture_rationale: str = Field(
        default=(
            "A neurosymbolic architecture for conflict data is justified "
            "because conflict analysis requires both statistical language "
            "understanding and explicit relational reasoning. Neural models "
            "parse unstructured evidence; symbolic structures preserve actors, "
            "claims, commitments, chronology, and causal hypotheses; and "
            "graph-based retrieval plus argumentation improve traceability, "
            "consistency, and decision support. "
            "This is NOT just GraphRAG — it is a four-layer neurosymbolic system."
        ),
    )

    four_layers: tuple[ArchitectureLayer, ...] = Field(
        default=(
            ArchitectureLayer(
                layer=1,
                name="neural_ingestion",
                description=(
                    "Extract actors, claims, events, sentiments, commitments, "
                    "threats, concessions, timelines, and uncertainty from "
                    "messy text using the ontology as an extraction schema. "
                    "Each extraction carries a confidence score."
                ),
            ),
            ArchitectureLayer(
                layer=2,
                name="symbolic_representation",
                description=(
                    "Encode extracted entities into the conflict ontology graph "
                    "with typed relations, controlled vocabularies, and "
                    "temporal metadata."
                ),
            ),
            ArchitectureLayer(
                layer=3,
                name="reasoning_inference",
                description=(
                    "Contradiction checks, commitment tracking, escalation "
                    "pattern detection, argument maps, procedural rules, "
                    "causal hypotheses. Deterministic rules fire first; "
                    "neural GNN predictions fill gaps second."
                ),
            ),
            ArchitectureLayer(
                layer=4,
                name="decision_support",
                description=(
                    "Surface options, risks, missing evidence, and competing "
                    "interpretations for human decision-makers. Human "
                    "validation promotes neural suggestions to new symbolic "
                    "rules (learning loop)."
                ),
            ),
        ),
        description="The four layers of the TACITUS neurosymbolic pipeline",
    )

    symbolic: SymbolicLayer = Field(
        default_factory=SymbolicLayer,
        description="Deterministic symbolic reasoning layer",
    )
    neural: NeuralLayer = Field(
        default_factory=NeuralLayer,
        description="Probabilistic neural inference layer",
    )
    bridge: BridgeProtocol = Field(
        default_factory=BridgeProtocol,
        description="Reason-then-embed bridge protocol",
    )

    # -- convenience helpers --------------------------------------------------

    def get_layer(self, number: int) -> ArchitectureLayer | None:
        """Return a layer by its 1-based number."""
        for layer in self.four_layers:
            if layer.layer == number:
                return layer
        return None

    @property
    def layer_names(self) -> list[str]:
        """Return ordered list of layer names."""
        return [layer.name for layer in self.four_layers]

    @property
    def all_symbolic_components(self) -> list[str]:
        """Shortcut to symbolic component names."""
        return self.symbolic.component_names

    @property
    def all_neural_components(self) -> list[str]:
        """Shortcut to neural component names."""
        return self.neural.component_names
