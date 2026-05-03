"""pipeline_audit_tables

Revision ID: b7c2f75d8f91
Revises: 6537795fe346
Create Date: 2026-05-01 21:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op


revision: str = "b7c2f75d8f91"
down_revision: Union[str, Sequence[str], None] = "6537795fe346"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("workspace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_uri", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("objective", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("ontology_profile", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("duplicate", sa.Boolean(), nullable=False),
        sa.Column("object_count", sa.Integer(), nullable=False),
        sa.Column("edge_count", sa.Integer(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("cleaned_chars", sa.Integer(), nullable=False),
        sa.Column("original_chars", sa.Integer(), nullable=False),
        sa.Column("pipeline", sa.JSON(), nullable=True),
        sa.Column("errors", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pipeline_runs_workspace_id"), "pipeline_runs", ["workspace_id"])
    op.create_index(op.f("ix_pipeline_runs_tenant_id"), "pipeline_runs", ["tenant_id"])
    op.create_index(op.f("ix_pipeline_runs_source_id"), "pipeline_runs", ["source_id"])
    op.create_index(op.f("ix_pipeline_runs_source_hash"), "pipeline_runs", ["source_hash"])
    op.create_index(op.f("ix_pipeline_runs_status"), "pipeline_runs", ["status"])
    op.create_index(op.f("ix_pipeline_runs_created_at"), "pipeline_runs", ["created_at"])

    op.create_table(
        "source_chunk_records",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("run_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("workspace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("label", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("start_char", sa.Integer(), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.Column("char_count", sa.Integer(), nullable=False),
        sa.Column("reason", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "ordinal", name="uq_source_chunk_run_ordinal"),
    )
    op.create_index(op.f("ix_source_chunk_records_run_id"), "source_chunk_records", ["run_id"])
    op.create_index(
        op.f("ix_source_chunk_records_workspace_id"), "source_chunk_records", ["workspace_id"]
    )
    op.create_index(
        op.f("ix_source_chunk_records_source_id"), "source_chunk_records", ["source_id"]
    )

    op.create_table(
        "ontology_profile_records",
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("run_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("workspace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("profile_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("objective", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("plan", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ontology_profile_records_run_id"), "ontology_profile_records", ["run_id"]
    )
    op.create_index(
        op.f("ix_ontology_profile_records_workspace_id"),
        "ontology_profile_records",
        ["workspace_id"],
    )
    op.create_index(
        op.f("ix_ontology_profile_records_profile_id"),
        "ontology_profile_records",
        ["profile_id"],
    )

    _graph_table("graph_object_records", object_table=True)
    _graph_table("graph_edge_records", object_table=False)


def downgrade() -> None:
    for table in ["graph_edge_records", "graph_object_records"]:
        op.drop_table(table)
    op.drop_table("ontology_profile_records")
    op.drop_table("source_chunk_records")
    op.drop_table("pipeline_runs")


def _graph_table(name: str, *, object_table: bool) -> None:
    columns = [
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("run_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("workspace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("kind", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    ]
    if not object_table:
        columns.extend(
            [
                sa.Column("source_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                sa.Column("target_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            ]
        )
    columns.extend(
        [
            sa.Column("source_ids", sa.JSON(), nullable=True),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        ]
    )
    op.create_table(name, *columns)
    for column in ["run_id", "workspace_id", "tenant_id", "kind", "created_at"]:
        op.create_index(op.f(f"ix_{name}_{column}"), name, [column])
    if not object_table:
        op.create_index(op.f(f"ix_{name}_source_id"), name, ["source_id"])
        op.create_index(op.f(f"ix_{name}_target_id"), name, ["target_id"])
