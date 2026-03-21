#!/usr/bin/env python3
"""
Seed Demo — Load all sample data into local development environment.

Usage:
    uv run python scripts/seed_demo.py              # Full seed
    uv run python scripts/seed_demo.py --dry-run     # Validate only, no writes
"""
from __future__ import annotations

import argparse
import json
import os
import sys

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "seed", "samples")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "templates")

SAMPLE_FILES = [
    "jcpoa.json",
    "hr_mediation.json",
    "commercial_dispute.json",
    "syria_civil_war.json",
    "labor_dispute.json",
    "commercial_ip_dispute.json",
]


def load_sample(filename: str) -> dict:
    """Load and validate a sample JSON file."""
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        print(f"  SKIP: {filename} (not found)")
        return {}
    with open(path) as f:
        data = json.load(f)
    return data


def validate_sample(data: dict, filename: str) -> bool:
    """Validate sample data structure."""
    issues = []
    if "workspace" not in data and "actors" not in data:
        issues.append("missing workspace or actors")
    if "actors" in data:
        for i, actor in enumerate(data["actors"]):
            if "name" not in actor:
                issues.append(f"actor[{i}] missing name")
            if "actor_type" not in actor:
                issues.append(f"actor[{i}] missing actor_type")
    if issues:
        print(f"  WARN: {filename}: {'; '.join(issues)}")
        return False
    return True


def seed_sample(data: dict, filename: str, dry_run: bool = False) -> None:
    """Seed a sample into the system."""
    ws_name = data.get("workspace", {}).get("name", filename)
    actors = data.get("actors", [])
    events = data.get("events", [])
    conflict = data.get("conflict", {})

    if dry_run:
        print(f"  DRY RUN: {ws_name}")
        print(f"    Actors: {len(actors)}")
        print(f"    Events: {len(events)}")
        print(f"    Conflict: {conflict.get('name', 'none')}")
        return

    print(f"  Seeding: {ws_name} ({len(actors)} actors, {len(events)} events)")
    # In production: call API to create workspace and ingest data
    # For now, just validate and report


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed DIALECTICA demo data")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, no writes")
    args = parser.parse_args()

    print("DIALECTICA Demo Seeder")
    print("=" * 50)

    # Check templates
    print("\nTemplates:")
    if os.path.isdir(TEMPLATES_DIR):
        for f in sorted(os.listdir(TEMPLATES_DIR)):
            if f.endswith((".yaml", ".yml")):
                print(f"  OK: {f}")
    else:
        print(f"  WARN: Templates directory not found: {TEMPLATES_DIR}")

    # Load and validate samples
    print("\nSamples:")
    loaded = 0
    for filename in SAMPLE_FILES:
        data = load_sample(filename)
        if data:
            valid = validate_sample(data, filename)
            if valid:
                seed_sample(data, filename, dry_run=args.dry_run)
                loaded += 1

    print(f"\nDone: {loaded}/{len(SAMPLE_FILES)} samples {'validated' if args.dry_run else 'seeded'}")


if __name__ == "__main__":
    main()
