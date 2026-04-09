"""
Databricks Connector for DIALECTICA reasoning pipeline.

Exports graph snapshots to Delta Lake and orchestrates KGE training jobs
on Databricks. The databricks-sdk is an optional dependency — the connector
degrades gracefully when it is not installed.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy import of databricks.sdk
# ---------------------------------------------------------------------------

_databricks_sdk: Any = None
_sdk_import_attempted: bool = False


def _get_databricks_sdk() -> Any:
    """Lazy-load databricks.sdk; returns the module or None."""
    global _databricks_sdk, _sdk_import_attempted  # noqa: PLW0603
    if not _sdk_import_attempted:
        _sdk_import_attempted = True
        try:
            import databricks.sdk as sdk  # type: ignore[import-untyped]

            _databricks_sdk = sdk
        except ImportError:
            logger.warning("databricks-sdk not installed — Databricks features unavailable")
    return _databricks_sdk


DATABRICKS_AVAILABLE: bool = _get_databricks_sdk() is not None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class DatabricksConfig:
    """Connection and catalog settings for the Databricks workspace."""

    workspace_url: str = field(default_factory=lambda: os.environ.get("DATABRICKS_HOST", ""))
    token: str = field(default_factory=lambda: os.environ.get("DATABRICKS_TOKEN", ""))
    cluster_id: str = field(default_factory=lambda: os.environ.get("DATABRICKS_CLUSTER_ID", ""))
    catalog: str = "dialectica"
    schema: str = "conflict_graphs"


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


class DatabricksConnector:
    """Interface to Databricks for graph export and KGE training.

    All operations handle the missing SDK gracefully — they log a warning
    and return a sentinel value instead of raising.
    """

    def __init__(self, config: DatabricksConfig | None = None) -> None:
        self._config = config or DatabricksConfig()
        self._client: Any = None
        self._init_attempted: bool = False

    # -- internal helpers ----------------------------------------------------

    def _ensure_client(self) -> Any:
        """Return a WorkspaceClient or None (idempotent)."""
        if self._init_attempted:
            return self._client
        self._init_attempted = True
        sdk = _get_databricks_sdk()
        if sdk is None:
            return None
        try:
            self._client = sdk.WorkspaceClient(
                host=self._config.workspace_url,
                token=self._config.token,
            )
        except Exception:
            logger.warning("Failed to create Databricks WorkspaceClient", exc_info=True)
        return self._client

    @property
    def available(self) -> bool:
        """True when the SDK is installed and a client could be created."""
        return self._ensure_client() is not None

    # -- public API ----------------------------------------------------------

    def export_graph_snapshot(
        self,
        workspace_id: str,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Export a conflict graph snapshot to Delta Lake via Databricks SQL.

        Returns a dict with ``status`` ("ok" or "unavailable") and optional
        ``rows_written`` count.
        """
        client = self._ensure_client()
        if client is None:
            logger.warning("Databricks unavailable — skipping graph export for %s", workspace_id)
            return {"status": "unavailable"}

        catalog_schema = f"{self._config.catalog}.{self._config.schema}"

        try:
            # Use the statement execution API to INSERT rows
            node_values = ", ".join(
                f"('{workspace_id}', '{n.get('id', '')}', "
                f"'{n.get('label', '')}', '{n.get('name', '')}')"
                for n in nodes
            )
            if node_values:
                client.statement_execution.execute_statement(
                    warehouse_id=self._config.cluster_id,
                    catalog=self._config.catalog,
                    schema=self._config.schema,
                    statement=f"INSERT INTO {catalog_schema}.nodes VALUES {node_values}",
                )

            edge_values = ", ".join(
                f"('{workspace_id}', '{e.get('id', '')}', "
                f"'{e.get('source_id', '')}', "
                f"'{e.get('target_id', '')}', '{e.get('type', '')}')"
                for e in edges
            )
            if edge_values:
                client.statement_execution.execute_statement(
                    warehouse_id=self._config.cluster_id,
                    catalog=self._config.catalog,
                    schema=self._config.schema,
                    statement=f"INSERT INTO {catalog_schema}.edges VALUES {edge_values}",
                )

            total = len(nodes) + len(edges)
            logger.info("Exported %d rows to Databricks for workspace %s", total, workspace_id)
            return {"status": "ok", "rows_written": total}

        except Exception:
            logger.error("Databricks export failed for workspace %s", workspace_id, exc_info=True)
            return {"status": "error"}

    def trigger_kge_training(
        self,
        workspace_id: str,
        model_type: str = "RotatE",
        epochs: int = 100,
    ) -> dict[str, Any]:
        """Submit a KGE training job on the Databricks cluster.

        Returns a dict with ``status`` and ``run_id`` if the job was submitted.
        """
        client = self._ensure_client()
        if client is None:
            logger.warning("Databricks unavailable — cannot trigger KGE training")
            return {"status": "unavailable"}

        try:
            run = client.jobs.submit(
                run_name=f"kge-train-{workspace_id}-{model_type}",
                tasks=[
                    {
                        "task_key": "kge_training",
                        "existing_cluster_id": self._config.cluster_id,
                        "notebook_task": {
                            "notebook_path": f"/Repos/dialectica/kge/train_{model_type.lower()}",
                            "base_parameters": {
                                "workspace_id": workspace_id,
                                "model_type": model_type,
                                "epochs": str(epochs),
                                "catalog": self._config.catalog,
                                "schema": self._config.schema,
                            },
                        },
                    }
                ],
            )
            run_id = getattr(run, "run_id", None)
            logger.info("Submitted KGE training run %s for workspace %s", run_id, workspace_id)
            return {"status": "ok", "run_id": run_id}

        except Exception:
            logger.error("Failed to submit KGE training job", exc_info=True)
            return {"status": "error"}

    def get_kge_predictions(
        self,
        head_id: str,
        relation: str,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Retrieve link predictions from the latest KGE model.

        Returns a list of dicts with ``tail_id`` and ``score``, or an
        empty list when Databricks is unavailable.
        """
        client = self._ensure_client()
        if client is None:
            logger.warning("Databricks unavailable — cannot retrieve KGE predictions")
            return []

        catalog_schema = f"{self._config.catalog}.{self._config.schema}"

        try:
            result = client.statement_execution.execute_statement(
                warehouse_id=self._config.cluster_id,
                catalog=self._config.catalog,
                schema=self._config.schema,
                statement=(
                    f"SELECT tail_id, score FROM {catalog_schema}.kge_predictions "
                    f"WHERE head_id = '{head_id}' AND relation = '{relation}' "
                    f"ORDER BY score DESC LIMIT {top_k}"
                ),
            )
            rows = getattr(result, "result", None)
            if rows and hasattr(rows, "data_array"):
                return [{"tail_id": row[0], "score": float(row[1])} for row in rows.data_array]
            return []

        except Exception:
            logger.error("Failed to retrieve KGE predictions", exc_info=True)
            return []
