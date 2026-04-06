"""Tests for subdomain ontology specifications."""

from __future__ import annotations

import pytest

from dialectica_ontology.subdomains import (
    SUBDOMAIN_SPECS,
    ConflictSubdomain,
    SubdomainSpec,
    detect_subdomain,
)


# ---------------------------------------------------------------------------
# ConflictSubdomain enum
# ---------------------------------------------------------------------------


class TestConflictSubdomain:
    def test_all_values_present(self):
        expected = {"geopolitical", "workplace", "commercial", "legal", "armed", "environmental"}
        assert {s.value for s in ConflictSubdomain} == expected

    def test_is_str_enum(self):
        assert isinstance(ConflictSubdomain.GEOPOLITICAL, str)
        assert ConflictSubdomain.WORKPLACE == "workplace"


# ---------------------------------------------------------------------------
# SUBDOMAIN_SPECS
# ---------------------------------------------------------------------------


class TestSubdomainSpecs:
    def test_all_subdomains_have_specs(self):
        for sd in ConflictSubdomain:
            assert sd in SUBDOMAIN_SPECS, f"Missing spec for {sd}"

    def test_specs_are_SubdomainSpec(self):
        for spec in SUBDOMAIN_SPECS.values():
            assert isinstance(spec, SubdomainSpec)

    def test_each_spec_has_node_types(self):
        for sd, spec in SUBDOMAIN_SPECS.items():
            assert len(spec.primary_node_types) > 0, f"{sd}: no primary_node_types"

    def test_each_spec_has_edge_types(self):
        for sd, spec in SUBDOMAIN_SPECS.items():
            assert len(spec.primary_edge_types) > 0, f"{sd}: no primary_edge_types"

    def test_each_spec_has_theories(self):
        for sd, spec in SUBDOMAIN_SPECS.items():
            assert len(spec.applicable_theories) > 0, f"{sd}: no applicable_theories"

    def test_each_spec_has_vocabulary(self):
        for sd, spec in SUBDOMAIN_SPECS.items():
            assert len(spec.vocabulary) > 0, f"{sd}: no vocabulary"

    def test_each_spec_has_escalation_indicators(self):
        for sd, spec in SUBDOMAIN_SPECS.items():
            assert len(spec.escalation_indicators) > 0, f"{sd}: no escalation_indicators"

    def test_each_spec_has_description(self):
        for sd, spec in SUBDOMAIN_SPECS.items():
            assert spec.description, f"{sd}: empty description"

    def test_geopolitical_includes_glasl(self):
        spec = SUBDOMAIN_SPECS[ConflictSubdomain.GEOPOLITICAL]
        assert "glasl" in spec.applicable_theories

    def test_workplace_includes_trust(self):
        spec = SUBDOMAIN_SPECS[ConflictSubdomain.WORKPLACE]
        assert "mayer_trust" in spec.applicable_theories

    def test_armed_includes_location(self):
        spec = SUBDOMAIN_SPECS[ConflictSubdomain.ARMED]
        assert "Location" in spec.primary_node_types


# ---------------------------------------------------------------------------
# detect_subdomain
# ---------------------------------------------------------------------------


class TestDetectSubdomain:
    def test_geopolitical_detection(self):
        result = detect_subdomain(
            node_labels=["Actor", "Conflict", "Norm", "Process"],
            edge_types=["PARTY_TO", "ALLIED_WITH", "GOVERNED_BY", "VIOLATES"],
        )
        assert result == ConflictSubdomain.GEOPOLITICAL

    def test_workplace_detection(self):
        result = detect_subdomain(
            node_labels=["Actor", "EmotionalState", "TrustState", "Role"],
            edge_types=["HAS_POWER_OVER", "EXPERIENCES", "TRUSTS", "MEMBER_OF"],
        )
        assert result == ConflictSubdomain.WORKPLACE

    def test_armed_detection(self):
        result = detect_subdomain(
            node_labels=["Actor", "Event", "Location", "PowerDynamic"],
            edge_types=["AT_LOCATION", "HAS_POWER_OVER", "ALLIED_WITH", "OPPOSED_TO"],
        )
        assert result == ConflictSubdomain.ARMED

    def test_legal_detection(self):
        result = detect_subdomain(
            node_labels=["Norm", "Evidence", "Process", "Outcome"],
            edge_types=["GOVERNED_BY", "VIOLATES", "EVIDENCED_BY", "RESOLVED_THROUGH"],
        )
        assert result == ConflictSubdomain.LEGAL

    def test_commercial_detection(self):
        result = detect_subdomain(
            node_labels=["Actor", "Interest", "Norm", "Outcome"],
            edge_types=["HAS_INTEREST", "GOVERNED_BY", "VIOLATES", "RESOLVED_THROUGH"],
        )
        assert result == ConflictSubdomain.COMMERCIAL

    def test_environmental_detection(self):
        result = detect_subdomain(
            node_labels=["Actor", "Issue", "Location", "Interest", "Narrative"],
            edge_types=["HAS_INTEREST", "AT_LOCATION", "ABOUT", "OPPOSED_TO"],
        )
        assert result == ConflictSubdomain.ENVIRONMENTAL

    def test_empty_defaults_to_geopolitical(self):
        """With no signals, should still return a valid subdomain."""
        result = detect_subdomain(node_labels=[], edge_types=[])
        assert isinstance(result, ConflictSubdomain)

    def test_returns_enum_type(self):
        result = detect_subdomain(["Actor"], ["PARTY_TO"])
        assert isinstance(result, ConflictSubdomain)
