"""
Schema Migrations — Version-tracked DDL changes for DIALECTICA Spanner schema.

Provides migration utilities for safe schema evolution:
- Version tracking in SchemaMigrations table
- Safe ALTER TABLE / CREATE INDEX operations
- Rollback support (where possible with Spanner DDL)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from google.cloud.spanner_v1 import param_types

logger = logging.getLogger(__name__)


@dataclass
class Migration:
    """A single schema migration."""

    version: int
    name: str
    up_ddl: list[str]  # DDL statements to apply
    down_ddl: list[str]  # DDL statements to revert (best-effort)


# ── Migration Registry ─────────────────────────────────────────────────────

MIGRATIONS: list[Migration] = [
    Migration(
        version=1,
        name="initial_schema",
        up_ddl=[],  # Applied via initialize_schema()
        down_ddl=[],
    ),
    Migration(
        version=2,
        name="add_extraction_jobs_progress",
        up_ddl=[
            "ALTER TABLE ExtractionJobs ADD COLUMN progress FLOAT64 DEFAULT (0.0)",
        ],
        down_ddl=[
            "ALTER TABLE ExtractionJobs DROP COLUMN progress",
        ],
    ),
    Migration(
        version=3,
        name="add_nodes_name_index",
        up_ddl=[
            "CREATE INDEX Idx_Nodes_Properties_Name ON Nodes (tenant_id, workspace_id, label) STORING (properties)",  # noqa: E501
        ],
        down_ddl=[
            "DROP INDEX Idx_Nodes_Properties_Name",
        ],
    ),
]


def get_pending_migrations(current_version: int) -> list[Migration]:
    """Return migrations that haven't been applied yet."""
    return [m for m in MIGRATIONS if m.version > current_version]


class MigrationRunner:
    """Runs schema migrations against a Spanner database."""

    def __init__(self, database: Any) -> None:
        """Args: database — google.cloud.spanner_v1.database.Database instance."""
        self._database = database

    def get_current_version(self) -> int:
        """Get the latest applied migration version."""
        try:
            with self._database.snapshot() as snapshot:
                result = snapshot.execute_sql("SELECT MAX(version) FROM SchemaMigrations")
                row = list(result)
                if row and row[0][0] is not None:
                    return row[0][0]
        except Exception:
            logger.info("SchemaMigrations table not found; assuming version 0")
        return 0

    def apply_migration(self, migration: Migration) -> None:
        """Apply a single migration's DDL and record it."""
        if migration.up_ddl:
            logger.info(
                "Applying migration %d: %s (%d statements)",
                migration.version,
                migration.name,
                len(migration.up_ddl),
            )
            operation = self._database.update_ddl(migration.up_ddl)
            operation.result()

        # Record the migration
        self._database.run_in_transaction(
            lambda txn: txn.insert(
                "SchemaMigrations",
                columns=["version", "name", "applied_at"],
                values=[[migration.version, migration.name, datetime.utcnow()]],
            )
        )
        logger.info("Migration %d applied successfully", migration.version)

    def rollback_migration(self, migration: Migration) -> None:
        """Revert a migration (best-effort — some DDL can't be undone in Spanner)."""
        if migration.down_ddl:
            logger.info("Rolling back migration %d: %s", migration.version, migration.name)
            operation = self._database.update_ddl(migration.down_ddl)
            operation.result()

        # Remove migration record
        self._database.run_in_transaction(
            lambda txn: txn.execute_update(
                "DELETE FROM SchemaMigrations WHERE version = @v",
                params={"v": migration.version},
                param_types={"v": param_types.INT64},
            )
        )
        logger.info("Migration %d rolled back", migration.version)

    def migrate_to_latest(self) -> int:
        """Apply all pending migrations. Returns number applied."""
        current = self.get_current_version()
        pending = get_pending_migrations(current)
        if not pending:
            logger.info("Schema is up to date (version %d)", current)
            return 0

        for migration in pending:
            self.apply_migration(migration)

        logger.info("Applied %d migrations (now at version %d)", len(pending), pending[-1].version)
        return len(pending)
