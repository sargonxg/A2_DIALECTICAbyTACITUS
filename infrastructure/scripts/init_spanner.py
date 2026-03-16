"""
Spanner Initialization Script — Apply DIALECTICA DDL to Spanner instance.

Creates:
  - Spanner instance (dialectica-graph, Enterprise, 100 PUs, us-east1)
  - Spanner database (dialectica)
  - All tables: Nodes, Edges, Workspaces, TheoryAssessments, APIKeys, UsageLogs, ExtractionJobs
  - Property Graph: ConflictGraph with dynamic labels
  - All indexes (including vector indexes on embedding column)

Usage:
  python infrastructure/scripts/init_spanner.py

Environment:
  SPANNER_EMULATOR_HOST=localhost:9010  (for local dev)
  GCP_PROJECT_ID=your-project-id
  SPANNER_INSTANCE_ID=dialectica-graph
  SPANNER_DATABASE_ID=dialectica
"""
import os
import sys
import logging

from google.cloud import spanner
from google.api_core.exceptions import AlreadyExists

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Add packages to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "packages", "graph", "src"))

from dialectica_graph.spanner_schema import get_ddl_statements


def main() -> None:
    project_id = os.environ.get("GCP_PROJECT_ID", "local-project")
    instance_id = os.environ.get("SPANNER_INSTANCE_ID", "dialectica-graph")
    database_id = os.environ.get("SPANNER_DATABASE_ID", "dialectica")
    emulator_host = os.environ.get("SPANNER_EMULATOR_HOST")

    logger.info("Project: %s", project_id)
    logger.info("Instance: %s", instance_id)
    logger.info("Database: %s", database_id)
    if emulator_host:
        logger.info("Using Spanner emulator at %s", emulator_host)

    client = spanner.Client(project=project_id)
    instance = client.instance(instance_id)

    # Create instance (emulator only — production instances are pre-created via Terraform)
    if emulator_host:
        try:
            operation = instance.create()
            operation.result()
            logger.info("Created Spanner instance: %s", instance_id)
        except AlreadyExists:
            logger.info("Spanner instance already exists: %s", instance_id)

    # Create database with DDL
    ddl_statements = get_ddl_statements()
    logger.info("Applying %d DDL statements", len(ddl_statements))

    database = instance.database(database_id, ddl_statements=ddl_statements)
    try:
        operation = database.create()
        operation.result()
        logger.info("Created database '%s' with schema", database_id)
    except AlreadyExists:
        logger.info("Database '%s' already exists, applying DDL updates", database_id)
        # Apply DDL to existing database
        database = instance.database(database_id)
        try:
            operation = database.update_ddl(ddl_statements)
            operation.result()
            logger.info("Schema updated successfully")
        except Exception as e:
            # Some statements may fail if already applied — that's OK
            logger.warning("Some DDL statements may have already been applied: %s", e)

    # Verify tables
    logger.info("Verifying schema...")
    with database.snapshot() as snapshot:
        # Check Nodes table
        result = snapshot.execute_sql(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = '' ORDER BY table_name"
        )
        tables = [row[0] for row in result]
        logger.info("Tables: %s", ", ".join(tables))

    expected = {"Nodes", "Edges", "Workspaces", "TheoryAssessments", "APIKeys", "UsageLogs", "ExtractionJobs", "SchemaMigrations"}
    found = set(tables)
    missing = expected - found
    if missing:
        logger.error("Missing tables: %s", missing)
        sys.exit(1)

    logger.info("Schema initialization complete — all %d tables verified", len(expected))


if __name__ == "__main__":
    main()
