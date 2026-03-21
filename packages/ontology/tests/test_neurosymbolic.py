"""Tests for dialectica_ontology.neurosymbolic — TACITUS four-layer neurosymbolic architecture."""

import pytest
from pydantic import ValidationError

from dialectica_ontology.neurosymbolic import (
    ArchitectureLayer,
    BridgeProtocol,
    BridgeStep,
    NeuralComponent,
    NeuralLayer,
    NeurosymbolicArchitecture,
    ScientificRisk,
    SymbolicComponent,
    SymbolicLayer,
)


# ─── SymbolicComponent ────────────────────────────────────────────────────────


class TestSymbolicComponent:
    """Tests for the SymbolicComponent frozen model."""

    def test_creation_with_required_fields(self):
        sc = SymbolicComponent(name="test_rule", description="A test rule")
        assert sc.name == "test_rule"
        assert sc.description == "A test rule"
        assert sc.deterministic is True  # default

    def test_deterministic_defaults_true(self):
        sc = SymbolicComponent(name="r", description="d")
        assert sc.deterministic is True

    def test_deterministic_can_be_overridden(self):
        sc = SymbolicComponent(name="r", description="d", deterministic=False)
        assert sc.deterministic is False

    def test_frozen_config_prevents_mutation(self):
        sc = SymbolicComponent(name="r", description="d")
        with pytest.raises(ValidationError):
            sc.name = "new_name"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            SymbolicComponent(description="d")

    def test_missing_description_raises(self):
        with pytest.raises(ValidationError):
            SymbolicComponent(name="r")


# ─── SymbolicLayer ─────────────────────────────────────────────────────────────


class TestSymbolicLayer:
    """Tests for the SymbolicLayer with its 9 default components."""

    @pytest.fixture()
    def layer(self) -> SymbolicLayer:
        return SymbolicLayer()

    def test_default_has_9_components(self, layer: SymbolicLayer):
        assert len(layer.components) == 9

    def test_default_description(self, layer: SymbolicLayer):
        assert "Deterministic" in layer.description

    def test_default_query_language(self, layer: SymbolicLayer):
        assert "Cypher" in layer.query_language

    def test_component_names_returns_list_of_strings(self, layer: SymbolicLayer):
        names = layer.component_names
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)
        assert len(names) == 9

    def test_component_names_contains_expected(self, layer: SymbolicLayer):
        names = layer.component_names
        assert "glasl_escalation_rules" in names
        assert "ury_brett_goldberg_loopback" in names
        assert "trust_breach_detection" in names
        assert "ucdp_conflict_classification" in names
        assert "temporal_logic" in names
        assert "norm_violation_detection" in names
        assert "batna_zopa_computation" in names
        assert "causal_chain_analysis" in names
        assert "cross_case_structural_similarity" in names

    def test_get_component_returns_component(self, layer: SymbolicLayer):
        comp = layer.get_component("glasl_escalation_rules")
        assert comp is not None
        assert comp.name == "glasl_escalation_rules"
        assert comp.deterministic is True

    def test_get_component_returns_none_for_missing(self, layer: SymbolicLayer):
        assert layer.get_component("nonexistent_rule") is None

    def test_all_components_are_deterministic(self, layer: SymbolicLayer):
        for comp in layer.components:
            assert comp.deterministic is True

    def test_frozen_config(self, layer: SymbolicLayer):
        with pytest.raises(ValidationError):
            layer.description = "something"


# ─── NeuralComponent ──────────────────────────────────────────────────────────


class TestNeuralComponent:
    """Tests for the NeuralComponent frozen model."""

    def test_creation_with_required_fields(self):
        nc = NeuralComponent(name="test_nn", description="A neural component")
        assert nc.name == "test_nn"
        assert nc.description == "A neural component"
        assert nc.probabilistic is True  # default

    def test_probabilistic_defaults_true(self):
        nc = NeuralComponent(name="n", description="d")
        assert nc.probabilistic is True

    def test_probabilistic_can_be_overridden(self):
        nc = NeuralComponent(name="n", description="d", probabilistic=False)
        assert nc.probabilistic is False

    def test_frozen_config_prevents_mutation(self):
        nc = NeuralComponent(name="n", description="d")
        with pytest.raises(ValidationError):
            nc.name = "new_name"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            NeuralComponent(description="d")

    def test_missing_description_raises(self):
        with pytest.raises(ValidationError):
            NeuralComponent(name="n")


# ─── NeuralLayer ───────────────────────────────────────────────────────────────


class TestNeuralLayer:
    """Tests for the NeuralLayer with its 7 default components."""

    @pytest.fixture()
    def layer(self) -> NeuralLayer:
        return NeuralLayer()

    def test_default_has_7_components(self, layer: NeuralLayer):
        assert len(layer.components) == 7

    def test_default_description(self, layer: NeuralLayer):
        assert "Probabilistic" in layer.description

    def test_component_names_returns_list_of_strings(self, layer: NeuralLayer):
        names = layer.component_names
        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)
        assert len(names) == 7

    def test_component_names_contains_expected(self, layer: NeuralLayer):
        names = layer.component_names
        assert "r_gat" in names
        assert "rotate" in names
        assert "temporal_attention" in names
        assert "narrative_similarity" in names
        assert "conflict_pattern_matching" in names
        assert "escalation_prediction" in names
        assert "outcome_prediction" in names

    def test_get_component_returns_component(self, layer: NeuralLayer):
        comp = layer.get_component("r_gat")
        assert comp is not None
        assert comp.name == "r_gat"
        assert comp.probabilistic is True

    def test_get_component_returns_none_for_missing(self, layer: NeuralLayer):
        assert layer.get_component("nonexistent_nn") is None

    def test_embedding_nodes(self, layer: NeuralLayer):
        assert layer.embedding_nodes == ("Actor", "Conflict", "Event", "Narrative")

    def test_recommended_dim(self, layer: NeuralLayer):
        assert layer.recommended_dim == 128

    def test_training_approach(self, layer: NeuralLayer):
        assert layer.training_approach == "reason-then-embed"

    def test_all_components_are_probabilistic(self, layer: NeuralLayer):
        for comp in layer.components:
            assert comp.probabilistic is True

    def test_frozen_config(self, layer: NeuralLayer):
        with pytest.raises(ValidationError):
            layer.description = "something"


# ─── BridgeStep ────────────────────────────────────────────────────────────────


class TestBridgeStep:
    """Tests for the BridgeStep frozen model."""

    def test_creation(self):
        bs = BridgeStep(step=1, description="First step")
        assert bs.step == 1
        assert bs.description == "First step"

    def test_step_range_valid(self):
        for i in range(1, 5):
            bs = BridgeStep(step=i, description=f"Step {i}")
            assert bs.step == i

    def test_step_below_range_raises(self):
        with pytest.raises(ValidationError):
            BridgeStep(step=0, description="Invalid")

    def test_step_above_range_raises(self):
        with pytest.raises(ValidationError):
            BridgeStep(step=5, description="Invalid")

    def test_frozen_config(self):
        bs = BridgeStep(step=1, description="d")
        with pytest.raises(ValidationError):
            bs.step = 2


# ─── ScientificRisk ────────────────────────────────────────────────────────────


class TestScientificRisk:
    """Tests for the ScientificRisk frozen model."""

    def test_creation(self):
        sr = ScientificRisk(
            name="test_risk",
            risk="Something can go wrong",
            mitigation="This is how we fix it",
        )
        assert sr.name == "test_risk"
        assert sr.risk == "Something can go wrong"
        assert sr.mitigation == "This is how we fix it"

    def test_frozen_config(self):
        sr = ScientificRisk(name="r", risk="risk", mitigation="mit")
        with pytest.raises(ValidationError):
            sr.name = "new"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            ScientificRisk(risk="r", mitigation="m")

    def test_missing_risk_raises(self):
        with pytest.raises(ValidationError):
            ScientificRisk(name="n", mitigation="m")

    def test_missing_mitigation_raises(self):
        with pytest.raises(ValidationError):
            ScientificRisk(name="n", risk="r")


# ─── BridgeProtocol ────────────────────────────────────────────────────────────


class TestBridgeProtocol:
    """Tests for the BridgeProtocol with its 4 default steps."""

    @pytest.fixture()
    def protocol(self) -> BridgeProtocol:
        return BridgeProtocol()

    def test_default_has_4_steps(self, protocol: BridgeProtocol):
        assert len(protocol.pattern) == 4

    def test_steps_are_numbered_1_through_4(self, protocol: BridgeProtocol):
        step_numbers = [s.step for s in protocol.pattern]
        assert step_numbers == [1, 2, 3, 4]

    def test_key_principle_contains_never_overridden(self, protocol: BridgeProtocol):
        assert "NEVER overridden" in protocol.key_principle

    def test_default_has_3_scientific_risks(self, protocol: BridgeProtocol):
        assert len(protocol.scientific_risks) == 3

    def test_scientific_risk_names(self, protocol: BridgeProtocol):
        names = [r.name for r in protocol.scientific_risks]
        assert "ontology_loss" in names
        assert "extraction_error_propagation" in names
        assert "normative_overreach" in names

    def test_get_risk_returns_risk(self, protocol: BridgeProtocol):
        risk = protocol.get_risk("ontology_loss")
        assert risk is not None
        assert risk.name == "ontology_loss"
        assert "rigid" in risk.risk.lower()

    def test_get_risk_returns_none_for_missing(self, protocol: BridgeProtocol):
        assert protocol.get_risk("nonexistent") is None

    def test_frozen_config(self, protocol: BridgeProtocol):
        with pytest.raises(ValidationError):
            protocol.description = "something"


# ─── ArchitectureLayer ─────────────────────────────────────────────────────────


class TestArchitectureLayer:
    """Tests for the ArchitectureLayer frozen model."""

    def test_creation(self):
        al = ArchitectureLayer(layer=1, name="test", description="Test layer")
        assert al.layer == 1
        assert al.name == "test"
        assert al.description == "Test layer"

    def test_layer_range_valid(self):
        for i in range(1, 5):
            al = ArchitectureLayer(layer=i, name=f"l{i}", description=f"Layer {i}")
            assert al.layer == i

    def test_layer_below_range_raises(self):
        with pytest.raises(ValidationError):
            ArchitectureLayer(layer=0, name="x", description="x")

    def test_layer_above_range_raises(self):
        with pytest.raises(ValidationError):
            ArchitectureLayer(layer=5, name="x", description="x")

    def test_frozen_config(self):
        al = ArchitectureLayer(layer=1, name="t", description="d")
        with pytest.raises(ValidationError):
            al.name = "new"


# ─── NeurosymbolicArchitecture ────────────────────────────────────────────────


class TestNeurosymbolicArchitecture:
    """Tests for the top-level NeurosymbolicArchitecture."""

    @pytest.fixture()
    def arch(self) -> NeurosymbolicArchitecture:
        return NeurosymbolicArchitecture()

    def test_full_instantiation(self, arch: NeurosymbolicArchitecture):
        assert arch is not None
        assert isinstance(arch.symbolic, SymbolicLayer)
        assert isinstance(arch.neural, NeuralLayer)
        assert isinstance(arch.bridge, BridgeProtocol)

    def test_four_layers(self, arch: NeurosymbolicArchitecture):
        assert len(arch.four_layers) == 4

    def test_layer_names(self, arch: NeurosymbolicArchitecture):
        names = arch.layer_names
        assert names == [
            "neural_ingestion",
            "symbolic_representation",
            "reasoning_inference",
            "decision_support",
        ]

    def test_get_layer_returns_correct_layer(self, arch: NeurosymbolicArchitecture):
        layer1 = arch.get_layer(1)
        assert layer1 is not None
        assert layer1.name == "neural_ingestion"
        assert layer1.layer == 1

        layer4 = arch.get_layer(4)
        assert layer4 is not None
        assert layer4.name == "decision_support"
        assert layer4.layer == 4

    def test_get_layer_returns_none_for_invalid(self, arch: NeurosymbolicArchitecture):
        assert arch.get_layer(0) is None
        assert arch.get_layer(5) is None
        assert arch.get_layer(99) is None

    def test_all_symbolic_components(self, arch: NeurosymbolicArchitecture):
        names = arch.all_symbolic_components
        assert isinstance(names, list)
        assert len(names) == 9
        assert "glasl_escalation_rules" in names

    def test_all_neural_components(self, arch: NeurosymbolicArchitecture):
        names = arch.all_neural_components
        assert isinstance(names, list)
        assert len(names) == 7
        assert "r_gat" in names

    def test_architecture_rationale(self, arch: NeurosymbolicArchitecture):
        assert "neurosymbolic" in arch.architecture_rationale.lower()
        assert "NOT just GraphRAG" in arch.architecture_rationale

    def test_frozen_config(self, arch: NeurosymbolicArchitecture):
        with pytest.raises(ValidationError):
            arch.architecture_rationale = "something"

    def test_symbolic_layer_accessible(self, arch: NeurosymbolicArchitecture):
        assert arch.symbolic.component_names == arch.all_symbolic_components

    def test_neural_layer_accessible(self, arch: NeurosymbolicArchitecture):
        assert arch.neural.component_names == arch.all_neural_components

    def test_bridge_protocol_accessible(self, arch: NeurosymbolicArchitecture):
        assert len(arch.bridge.pattern) == 4
        assert arch.bridge.get_risk("ontology_loss") is not None
