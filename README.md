# reverse-etl-lite

**Close the loop: push dbt model outputs back to your CRM.**

A minimal Python tool that syncs dbt model outputs (or any SQL query) to Salesforce and HubSpot via their APIs. Understands the full data lifecycle: warehouse → transformation → activation.

## Why

Your dbt models compute customer health scores, churn risk, LTV, and segments. But that data lives in the warehouse — your sales team needs it in Salesforce. This tool bridges that gap without a $50k/year reverse ETL platform.

## Quick Start

```bash
pip install -r requirements.txt

# Seed demo data
python demo/seed_demo.py

# Dry run (validates without writing)
python cli.py config/customer_health.yaml --dry-run

# Real sync (set API credentials first)
export SF_INSTANCE_URL="https://yourorg.salesforce.com"
export SF_ACCESS_TOKEN="..."
python cli.py config/customer_health.yaml
```

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Source     │     │   Mapper     │     │   Destination    │
│              │     │              │     │                  │
│ • SQLite     │────▶│ • Field map  │────▶│ • Salesforce     │
│ • PostgreSQL │     │ • Transforms │     │ • HubSpot        │
│ • CSV        │     │ • Defaults   │     │ • Console (debug)│
└──────────────┘     └──────────────┘     └──────────────────┘
```

## Sync Config

Define syncs in YAML:

```yaml
name: "customer_health_to_salesforce"

source:
  type: postgres
  host: "warehouse.example.com"
  database: "analytics"
  query: "SELECT * FROM marts.customer_health_scores"

destination:
  type: salesforce
  object: Account
  external_id_field: External_Id__c

mapping:
  key_field: "external_id"
  fields:
    customer_id: "external_id"
    company_name: "Name"
    health_score: "Health_Score__c"
    churn_risk: "Churn_Risk__c"
  transforms:
    Name: "strip"
  defaults:
    Sync_Source__c: "dbt"
```

## Supported Sources

| Source | Config |
|--------|--------|
| SQLite | `type: sqlite`, `path`, `query` |
| PostgreSQL | `type: postgres`, `host`, `database`, `query` |
| CSV | `type: csv`, `path` |

## Supported Destinations

| Destination | Config |
|-------------|--------|
| Salesforce | `type: salesforce`, `object`, `external_id_field` |
| HubSpot | `type: hubspot`, `object` (contacts/companies) |
| Console | `type: console` (debug/dry-run) |

## Field Transforms

| Transform | Effect |
|-----------|--------|
| `upper` | UPPERCASE |
| `lower` | lowercase |
| `strip` | Remove whitespace |
| `int` | Cast to integer |
| `float` | Cast to float |
| `bool` | Cast to boolean |

## Sync Log

Every run appends to `logs/sync_log.jsonl`:

```json
{"status": "complete", "timestamp": "...", "records_read": 50, "records_synced": 48, "records_failed": 2}
```

## License

MIT
