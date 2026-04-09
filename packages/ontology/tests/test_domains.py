"""Tests for two-domain specialization (Human Friction + Conflict/Warfare)."""

from dialectica_ontology.domains import (
    CONFLICT_WARFARE,
    DOMAIN_SPECS,
    HUMAN_FRICTION,
    TacitusDomain,
    detect_domain_from_conflict_domain,
    detect_domain_from_scale,
    get_domain_spec,
    get_extraction_prompt_for_domain,
    get_theories_for_domain,
)


class TestTacitusDomains:
    def test_two_domains_exist(self):
        assert len(DOMAIN_SPECS) == 2
        assert TacitusDomain.HUMAN_FRICTION in DOMAIN_SPECS
        assert TacitusDomain.CONFLICT_WARFARE in DOMAIN_SPECS

    def test_human_friction_spec(self):
        spec = HUMAN_FRICTION
        assert spec.domain == TacitusDomain.HUMAN_FRICTION
        assert "Actor" in spec.primary_node_types
        assert "EmotionalState" in spec.primary_node_types
        assert "fisher_ury" in spec.primary_theories
        assert spec.scale_range == ("micro", "meso")
        assert len(spec.subdomains) >= 4

    def test_conflict_warfare_spec(self):
        spec = CONFLICT_WARFARE
        assert spec.domain == TacitusDomain.CONFLICT_WARFARE
        assert "Actor" in spec.primary_node_types
        assert "Norm" in spec.primary_node_types
        assert "Location" in spec.primary_node_types
        assert "glasl" in spec.primary_theories
        assert "zartman" in spec.primary_theories
        assert spec.scale_range == ("macro", "meta")

    def test_detect_domain_from_scale(self):
        assert detect_domain_from_scale("micro") == TacitusDomain.HUMAN_FRICTION
        assert detect_domain_from_scale("meso") == TacitusDomain.HUMAN_FRICTION
        assert detect_domain_from_scale("macro") == TacitusDomain.CONFLICT_WARFARE
        assert detect_domain_from_scale("meta") == TacitusDomain.CONFLICT_WARFARE

    def test_detect_domain_from_conflict_domain(self):
        assert detect_domain_from_conflict_domain("workplace") == TacitusDomain.HUMAN_FRICTION
        assert detect_domain_from_conflict_domain("commercial") == TacitusDomain.HUMAN_FRICTION
        assert detect_domain_from_conflict_domain("political") == TacitusDomain.CONFLICT_WARFARE
        assert detect_domain_from_conflict_domain("armed") == TacitusDomain.CONFLICT_WARFARE

    def test_get_domain_spec(self):
        spec = get_domain_spec(TacitusDomain.HUMAN_FRICTION)
        assert spec is HUMAN_FRICTION

    def test_get_theories_for_domain(self):
        hf_theories = get_theories_for_domain(TacitusDomain.HUMAN_FRICTION)
        assert "fisher_ury" in hf_theories
        assert hf_theories.index("fisher_ury") < hf_theories.index("kriesberg")

        cw_theories = get_theories_for_domain(TacitusDomain.CONFLICT_WARFARE)
        assert "glasl" in cw_theories
        assert cw_theories.index("glasl") < cw_theories.index("fisher_ury")

    def test_extraction_prompts_differ(self):
        hf_prompt = get_extraction_prompt_for_domain(TacitusDomain.HUMAN_FRICTION)
        cw_prompt = get_extraction_prompt_for_domain(TacitusDomain.CONFLICT_WARFARE)
        assert hf_prompt != cw_prompt
        assert "interests" in hf_prompt.lower()
        assert "UCDP" in cw_prompt or "state" in cw_prompt.lower()

    def test_escalation_indicators_differ(self):
        assert "formal_complaint" in HUMAN_FRICTION.escalation_indicators
        assert "military_mobilization" in CONFLICT_WARFARE.escalation_indicators

    def test_intervention_types_differ(self):
        assert "coaching" in HUMAN_FRICTION.intervention_types
        assert "peacekeeping" in CONFLICT_WARFARE.intervention_types
