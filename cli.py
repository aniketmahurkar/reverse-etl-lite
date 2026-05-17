#!/usr/bin/env python3
"""CLI for reverse-etl-lite."""
import argparse
import logging
import sys

from syncs import run_sync

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Sync dbt outputs to CRM APIs")
    parser.add_argument("config", help="Path to sync config YAML")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing")
    args = parser.parse_args()

    result = run_sync(args.config, dry_run=args.dry_run)

    print(f"\n{'='*40}")
    print(f"Status: {result['status']}")
    print(f"Records read: {result['records_read']}")
    if "records_synced" in result:
        print(f"Records synced: {result['records_synced']}")
        print(f"Records failed: {result['records_failed']}")
    if result.get("errors"):
        print(f"Errors: {len(result['errors'])}")
        for e in result["errors"][:5]:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
