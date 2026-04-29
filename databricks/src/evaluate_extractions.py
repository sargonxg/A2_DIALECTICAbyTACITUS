"""Optional Databricks entry point for extraction quality and benchmark scoring."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="dialectica")
    parser.add_argument("--schema", default="conflict_graphs")
    args = parser.parse_args()
    print(f"TODO evaluate extraction quality in {args.catalog}.{args.schema}")


if __name__ == "__main__":
    main()
