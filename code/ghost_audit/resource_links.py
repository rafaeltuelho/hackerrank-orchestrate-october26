"""Explicit catalog aliases connect business document IDs to logical resource IDs."""

import re

from .data import Dataset, Identity, timestamp
from .evidence import Fragment, exact_match
from .models import Request


def resource_aliases(
    dataset: Dataset, request: Request, identity: Identity | None = None
) -> dict[str, list[dict[str, str]]]:
    aliases = {}
    for row in dataset.activity:
        if (
            row["event_type"] != "LINK_RESOURCE_IDENTITY"
            or timestamp(row["event_time"]) > request.audit_at
        ):
            continue
        canonical = row["resource_id"]
        match = re.search(re.escape(canonical) + r"\s*\(([^)\n]+)\)", row["details"])
        if match:
            if identity is not None and not any(
                exact_match(a.value, row["details"]) for a in identity.aliases if a.kind != "name"
            ):
                continue
            aliases.setdefault(canonical, []).append(
                {
                    "value": match[1],
                    "activity_id": row["activity_id"],
                    "event_time": row["event_time"],
                    "system_id": row["target_system"],
                }
            )
    owners = {}
    for resource, values in aliases.items():
        for alias in values:
            owners.setdefault((alias["system_id"], alias["value"]), set()).add(resource)
    return {
        resource: [a for a in values if len(owners[a["system_id"], a["value"]]) == 1]
        for resource, values in aliases.items()
    }


def matches_resource(resource_id: str, fragment: Fragment, aliases: dict) -> bool:
    return exact_match(resource_id, fragment.text) or any(
        exact_match(alias["value"], fragment.text) for alias in aliases.get(resource_id, [])
    )
