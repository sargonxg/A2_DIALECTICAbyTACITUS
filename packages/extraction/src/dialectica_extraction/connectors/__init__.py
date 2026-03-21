"""Conflict data connectors — ACLED, GDELT, UCDP."""
from dialectica_extraction.connectors.acled import ACLEDConnector
from dialectica_extraction.connectors.gdelt import GDELTConnector
from dialectica_extraction.connectors.ucdp import UCDPConnector
from dialectica_extraction.connectors.entity_resolver import EntityResolver

__all__ = ["ACLEDConnector", "GDELTConnector", "UCDPConnector", "EntityResolver"]
