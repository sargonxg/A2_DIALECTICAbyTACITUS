"""Optional Databricks entry point for TACITUS primitive extraction to Delta."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="dialectica")
    parser.add_argument("--schema", default="conflict_graphs")
    args = parser.parse_args()
    print(f"TODO extract TACITUS primitives into {args.catalog}.{args.schema}.primitive_candidates")


if __name__ == "__main__":
    main()
