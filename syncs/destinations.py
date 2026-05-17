"""Destination connectors — upsert to Salesforce and HubSpot APIs."""
from __future__ import annotations

import logging
import os
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class Destination(Protocol):
    def upsert(self, records: list[dict], key_field: str) -> dict[str, Any]: ...


def get_destination(config: dict) -> Destination:
    dest_type = config["type"]
    if dest_type == "salesforce":
        return SalesforceDestination(config)
    elif dest_type == "hubspot":
        return HubSpotDestination(config)
    elif dest_type == "console":
        return ConsoleDestination(config)
    else:
        raise ValueError(f"Unsupported destination: {dest_type}")


class ConsoleDestination:
    """Debug destination — prints records to stdout."""

    def __init__(self, config: dict):
        pass

    def upsert(self, records: list[dict], key_field: str) -> dict[str, Any]:
        for r in records:
            logger.info(f"  → {r}")
        return {"success": len(records), "failed": 0, "errors": []}


class SalesforceDestination:
    """Upsert records to Salesforce via simple-salesforce."""

    def __init__(self, config: dict):
        self.object_name = config["object"]
        self.external_id = config.get("external_id_field", "Id")
        self.instance_url = config.get("instance_url") or os.environ.get("SF_INSTANCE_URL", "")
        self.access_token = config.get("access_token") or os.environ.get("SF_ACCESS_TOKEN", "")

    def _get_client(self):
        try:
            from simple_salesforce import Salesforce
        except ImportError:
            raise ImportError("Install simple-salesforce: pip install simple-salesforce")
        return Salesforce(instance_url=self.instance_url, session_id=self.access_token)

    def upsert(self, records: list[dict], key_field: str) -> dict[str, Any]:
        sf = self._get_client()
        obj = getattr(sf, self.object_name)
        success, failed, errors = 0, 0, []

        for record in records:
            try:
                obj.upsert(f"{self.external_id}/{record.get(key_field, '')}", record)
                success += 1
            except Exception as e:
                failed += 1
                errors.append({"record": record.get(key_field), "error": str(e)})

        return {"success": success, "failed": failed, "errors": errors}


class HubSpotDestination:
    """Upsert contacts/companies to HubSpot via v3 API."""

    def __init__(self, config: dict):
        self.object_type = config.get("object", "contacts")
        self.api_key = config.get("api_key") or os.environ.get("HUBSPOT_API_KEY", "")
        self.base_url = "https://api.hubapi.com/crm/v3/objects"

    def upsert(self, records: list[dict], key_field: str) -> dict[str, Any]:
        try:
            import requests
        except ImportError:
            raise ImportError("Install requests: pip install requests")

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        success, failed, errors = 0, 0, []

        for record in records:
            payload = {"properties": record}
            try:
                resp = requests.post(
                    f"{self.base_url}/{self.object_type}",
                    json=payload,
                    headers=headers,
                )
                if resp.status_code in (200, 201):
                    success += 1
                else:
                    failed += 1
                    errors.append({"record": record.get(key_field), "error": resp.text[:200]})
            except Exception as e:
                failed += 1
                errors.append({"record": record.get(key_field), "error": str(e)})

        return {"success": success, "failed": failed, "errors": errors}
