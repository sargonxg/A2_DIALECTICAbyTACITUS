"""
Integration test fixtures with testcontainers for Neo4j, Redis, and Qdrant.
"""
from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def neo4j_container():
    """Start a Neo4j test container for the session."""
    try:
        from testcontainers.neo4j import Neo4jContainer
        container = Neo4jContainer("neo4j:5-community")
        container.with_env("NEO4J_AUTH", "neo4j/testpassword")
        container.start()
        yield {
            "uri": container.get_connection_url(),
            "username": "neo4j",
            "password": "testpassword",
        }
        container.stop()
    except ImportError:
        pytest.skip("testcontainers[neo4j] not installed")


@pytest.fixture(scope="session")
def redis_container():
    """Start a Redis test container for the session."""
    try:
        from testcontainers.redis import RedisContainer
        container = RedisContainer("redis:7-alpine")
        container.start()
        yield {
            "url": f"redis://{container.get_container_host_ip()}:{container.get_exposed_port(6379)}",
        }
        container.stop()
    except ImportError:
        pytest.skip("testcontainers[redis] not installed")


@pytest.fixture(scope="session")
def qdrant_container():
    """Start a Qdrant test container for the session."""
    try:
        from testcontainers.core.container import DockerContainer
        container = DockerContainer("qdrant/qdrant:v1.15.4")
        container.with_exposed_ports(6333, 6334)
        container.start()
        host = container.get_container_host_ip()
        rest_port = container.get_exposed_port(6333)
        grpc_port = container.get_exposed_port(6334)
        yield {
            "host": host,
            "rest_port": int(rest_port),
            "grpc_port": int(grpc_port),
        }
        container.stop()
    except ImportError:
        pytest.skip("testcontainers not installed")
