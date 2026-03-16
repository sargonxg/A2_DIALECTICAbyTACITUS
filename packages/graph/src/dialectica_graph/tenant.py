"""
Tenant Isolation — Multi-tenant enforcement for DIALECTICA graph queries.

Ensures all data access is scoped by tenant_id and workspace_id.
Provides row-level filtering helpers for both Spanner SQL and Cypher.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TenantContext:
    """Active tenant + workspace scope for a request."""

    tenant_id: str
    workspace_id: str

    def validate(self) -> None:
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        if not self.workspace_id:
            raise ValueError("workspace_id is required")


class TenantFilter:
    """Generates tenant-scoped WHERE clauses for queries."""

    @staticmethod
    def spanner_node_filter(
        alias: str = "n",
        tenant_id: str | None = None,
        workspace_id: str | None = None,
    ) -> tuple[str, dict[str, str]]:
        """Return a SQL WHERE fragment and params for tenant-scoped node queries.

        Returns:
            (where_clause, params) where clause starts with ' AND ...'
        """
        clauses = []
        params: dict[str, str] = {}

        if workspace_id:
            clauses.append(f"{alias}.workspace_id = @ws")
            params["ws"] = workspace_id
        if tenant_id:
            clauses.append(f"{alias}.tenant_id = @tid")
            params["tid"] = tenant_id
        clauses.append(f"{alias}.deleted_at IS NULL")

        where = " AND ".join(clauses)
        return where, params

    @staticmethod
    def spanner_edge_filter(
        alias: str = "e",
        tenant_id: str | None = None,
        workspace_id: str | None = None,
    ) -> tuple[str, dict[str, str]]:
        """Return a SQL WHERE fragment and params for tenant-scoped edge queries."""
        clauses = []
        params: dict[str, str] = {}

        if workspace_id:
            clauses.append(f"{alias}.workspace_id = @ws")
            params["ws"] = workspace_id
        if tenant_id:
            clauses.append(f"{alias}.tenant_id = @tid")
            params["tid"] = tenant_id

        where = " AND ".join(clauses)
        return where, params

    @staticmethod
    def cypher_node_filter(
        alias: str = "n",
        workspace_id: str | None = None,
        tenant_id: str | None = None,
    ) -> tuple[str, dict[str, str]]:
        """Return a Cypher WHERE fragment and params for tenant-scoped queries."""
        clauses = []
        params: dict[str, str] = {}

        if workspace_id:
            clauses.append(f"{alias}.workspace_id = $ws")
            params["ws"] = workspace_id
        if tenant_id:
            clauses.append(f"{alias}.tenant_id = $tid")
            params["tid"] = tenant_id
        clauses.append(f"{alias}.deleted_at IS NULL")

        where = " AND ".join(clauses)
        return where, params

    @staticmethod
    def validate_access(
        tenant_id: str,
        workspace_id: str,
        resource_tenant_id: str,
        resource_workspace_id: str,
    ) -> bool:
        """Check if a tenant has access to a resource."""
        return (
            tenant_id == resource_tenant_id
            and workspace_id == resource_workspace_id
        )
