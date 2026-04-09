"""
API Configuration — Pydantic Settings for DIALECTICA API.

All settings load from environment variables with sensible defaults.
Validated at startup — missing required settings fail fast.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GCP
    gcp_project_id: str = "local-project"
    spanner_instance_id: str = "dialectica-graph"
    spanner_database_id: str = "dialectica"
    spanner_emulator_host: str = ""
    vertex_ai_location: str = "us-east1"
    gemini_flash_model: str = "gemini-2.5-flash-001"
    gemini_pro_model: str = "gemini-2.5-pro-001"

    # App
    graph_backend: str = "neo4j"  # "neo4j" (primary), "spanner", or "falkordb"
    admin_api_key: str = "dev-admin-key-change-in-production"
    log_level: str = "INFO"
    cors_origins: str = "*"

    # Neo4j (primary — TACITUS is in Neo4j Startup Program)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "dialectica-dev"
    neo4j_database: str = "neo4j"

    # Rate limiting
    rate_limit_backend: str = "memory"  # "memory" or "redis"
    redis_url: str = "redis://localhost:6379"

    # Metadata database (SQLite for dev, PostgreSQL for production Cloud SQL)
    database_url: str = "sqlite+aiosqlite:///./dialectica.db"
    # For production Cloud SQL (PostgreSQL):
    # DATABASE_URL=postgresql+asyncpg://user:pass@/dialectica?host=/cloudsql/PROJECT:REGION:INSTANCE

    # Environment & auth
    environment: str = "development"  # "development" or "production"
    api_keys_json: str = "[]"  # JSON array of key definitions

    model_config = {"env_prefix": "", "case_sensitive": False}


def get_settings() -> Settings:
    """Return a new Settings instance (call-site caching via deps.py)."""
    return Settings()
