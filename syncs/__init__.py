"""reverse-etl-lite: Sync dbt model outputs to CRM APIs.

Reads from any SQL source (dbt outputs), maps fields, and upserts to
Salesforce or HubSpot via their REST APIs.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .sources import read_source
from .destinations import get_destination
from .mapper import apply_mapping

logger = logging.getLogger(__name__)


def load_sync_config(config_path: str) -> dict:
    """Load a sync job configuration."""
    return yaml.safe_load(Path(config_path).read_text())


def run_sync(config_path: str, dry_run: bool = False) -> dict[str, Any]:
    """Execute a single sync job.

    Args:
        config_path: Path to sync YAML config.
        dry_run: If True, validate and log but don't write to destination.

    Returns:
        Summary dict with counts and errors.
    """
    config = load_sync_config(config_path)
    source_cfg = config["source"]
    dest_cfg = config["destination"]
    mapping = config["mapping"]

    # 1. Read source data
    logger.info(f"Reading from source: {source_cfg['type']}")
    records = read_source(source_cfg)
    logger.info(f"Read {len(records)} records")

    # 2. Apply field mapping
    mapped = [apply_mapping(record, mapping) for record in records]
    logger.info(f"Mapped {len(mapped)} records")

    # 3. Write to destination
    if dry_run:
        logger.info(f"[DRY RUN] Would sync {len(mapped)} records to {dest_cfg['type']}")
        return {"status": "dry_run", "records_read": len(records), "records_mapped": len(mapped)}

    destination = get_destination(dest_cfg)
    result = destination.upsert(mapped, key_field=mapping.get("key_field", "id"))

    summary = {
        "status": "complete",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "records_read": len(records),
        "records_synced": result.get("success", 0),
        "records_failed": result.get("failed", 0),
        "errors": result.get("errors", []),
    }

    # Write run log
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    with open(log_path / "sync_log.jsonl", "a") as f:
        f.write(json.dumps(summary) + "\n")

    return summary
