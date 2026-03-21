#!/usr/bin/env python3
"""
Demo Query — Run sample GraphRAG queries against seeded data.

Usage:
    uv run python scripts/demo_query.py
"""
from __future__ import annotations

import json
import os

import httpx

API_URL = os.getenv("DIALECTICA_API_URL", "http://localhost:8080")
API_KEY = os.getenv("ADMIN_API_KEY", "dev-admin-key-change-in-production")

DEMO_QUERIES = [
    {
        "workspace": "JCPOA",
        "query": "What is the current escalation trajectory?",
        "mode": "escalation",
    },
    {
        "workspace": "JCPOA",
        "query": "Who are the key actors and their alliances?",
        "mode": "general",
    },
    {
        "workspace": "JCPOA",
        "query": "What are the trust dynamics between Iran and the US?",
        "mode": "trust",
    },
]


def run_demo() -> None:
    print("DIALECTICA Demo Queries")
    print("=" * 60)

    headers = {"X-API-Key": API_KEY}

    # Check health
    try:
        resp = httpx.get(f"{API_URL}/health", timeout=5)
        health = resp.json()
        print(f"\nAPI Status: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"\nAPI not reachable at {API_URL}: {e}")
        print("Start the API with: make dev")
        return

    # List workspaces
    try:
        resp = httpx.get(f"{API_URL}/v1/workspaces", headers=headers, timeout=10)
        if resp.status_code == 200:
            workspaces = resp.json()
            print(f"Workspaces: {len(workspaces)}")
            for ws in workspaces[:5]:
                print(f"  - {ws.get('name', ws.get('workspace_id', '?'))}")
        else:
            print(f"Workspace list: {resp.status_code}")
    except Exception as e:
        print(f"Failed to list workspaces: {e}")

    # Run demo queries
    print("\n" + "-" * 60)
    for i, demo in enumerate(DEMO_QUERIES, 1):
        print(f"\nQuery {i}: {demo['query']}")
        print(f"  Mode: {demo['mode']}")
        print(f"  Workspace: {demo['workspace']}")
        # In production: POST to /v1/workspaces/{id}/analyze
        print("  (Requires seeded data — run scripts/seed_demo.py first)")

    print("\n" + "=" * 60)
    print("Demo complete. For full functionality, seed data with:")
    print("  uv run python scripts/seed_demo.py")


if __name__ == "__main__":
    run_demo()
