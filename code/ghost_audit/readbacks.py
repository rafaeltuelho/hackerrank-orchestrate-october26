"""Ground a conservative subset of exact operational readbacks.

Other artifact forms remain explicit extraction/interpretation work. No status/result
claim is converted into state. A trace join requires the same source, service and exact
trace ID; it never uses adjacent rows or timestamps to infer ownership.
"""

import shlex

from .data import Identity, email_key
from .evidence import Fragment
from .models import Observation, SourceRef, SubjectLink

IDENTITY_KEYS = {
    "user_id": "user_id",
    "customer_reference": "user_id",
    "subject_reference": "user_id",
    "email": "email",
    "customer_email": "email",
    "requester_email": "email",
    "phone": "phone",
    "requester_phone": "phone",
    "email_hash": "email_hash",
}
READ_EVENTS = {
    "scoped_sql_lookup_completed",
    "profile_lookup_completed",
    "index_query_completed",
    "connector_config_read_completed",
    "restore_policy_read_completed",
    "audit_record_read_completed",
    "support_ticket_read_completed",
}


def log_values(fragment: Fragment) -> dict[str, str]:
    if fragment.extracted_fields:
        return fragment.extracted_fields
    if not fragment.locator.startswith("line:"):
        return {}
    values = {}
    try:
        tokens = shlex.split(fragment.text)
    except ValueError:
        return {}  # Not every plain-text log line is a shell-style key/value record.
    for token in tokens:
        if "=" in token:
            key, value = token.split("=", 1)
            if key in values:
                return {}  # Ambiguous duplicate fields cannot support state.
            values[key] = value
    return values


def normalize_readbacks(
    fragments: list[Fragment], identity: Identity
) -> tuple[list[Observation], list[SubjectLink]]:
    observations, links = [], []
    aliases = {(a.kind, a.value) for a in identity.aliases if a.kind != "name"}
    parsed = [(f, log_values(f)) for f in fragments if f.observed_at is not None]
    for fragment, values in parsed:
        event = values.get("event")
        system, resource = values.get("service"), values.get("resource_id")
        if (
            not system
            or not resource
            or (event not in READ_EVENTS and "handover_state" not in values)
        ):
            continue
        state, complete = None, False
        if event == "scoped_sql_lookup_completed":
            state, complete = ("ABSENT", True) if values.get("rows") == "0" else (None, False)
        elif "handover_state" in values:
            state = {
                "NOT_FOUND": "ABSENT",
                "FOUND": "PRESENT",
                "IDENTIFIABLE": "PRESENT",
                "ACTIVE": "ACTIVE",
                "ANONYMIZED": "ANONYMIZED",
                "BLOCKED": "BLOCKED",
                "DISABLED": "DISABLED",
                "REDACTED": "REDACTED",
            }.get(values["handover_state"])
            complete = state == "ABSENT"
        elif event == "profile_lookup_completed":
            if values.get("rows") == "0" and values.get("http_status") == "404":
                state, complete = "ABSENT", True
            elif values.get("rows") == "1" and values.get("http_status") == "200":
                state = "PRESENT"
        elif event == "index_query_completed":
            if values.get("result") == "hit":
                state = "PRESENT"
            elif values.get("result") == "miss" and values.get("total_hits") == "0":
                state, complete = "ABSENT", True
        elif event == "connector_config_read_completed":
            state = {"true": "ACTIVE", "false": "DISABLED"}.get(values.get("enabled"))
        elif event == "restore_policy_read_completed":
            state = {"true": "ACTIVE", "false": "BLOCKED"}.get(values.get("restore_allowed"))
        elif event == "audit_record_read_completed" and values.get("rows") == "1":
            state = "PRESENT"
        elif event == "support_ticket_read_completed" and any(
            key in values for key in ("requester_email", "requester_phone", "customer_reference")
        ):
            state = "PRESENT"
        if state is None:
            continue
        source = SourceRef(
            evidence_id=fragment.evidence_id,
            locator=fragment.locator,
            captured_at=fragment.captured_at,
            observed_at=fragment.observed_at,
        )
        # Field map preserves literal fields including operational metadata; policy
        # classification must explicitly account for permitted business fields later.
        observations.append(
            Observation(
                system_id=system,
                resource_id=resource,
                copy_id=values.get("region", "unspecified")
                + "/"
                + values.get("route", "unspecified"),
                state=state,
                source=source,
                proof_kind="CONFIGURATION"
                if event in {"connector_config_read_completed", "restore_policy_read_completed"}
                else ("ARTIFACT" if "handover_state" in values else "READBACK"),
                scope_complete=complete,
                fields={k: None if v == "null" else v for k, v in values.items()},
            )
        )
        candidates = [(fragment, values)]
        trace = values.get("trace_id")
        if trace:
            candidates.extend(
                (f, v)
                for f, v in parsed
                if f.evidence_id == fragment.evidence_id
                and v.get("trace_id") == trace
                and v.get("service") == system
                and f.observed_at <= fragment.observed_at
                and v.get("resource_id", resource) == resource
            )
        for f, v in candidates:
            matches = {
                (kind, v[key])
                for key, kind in IDENTITY_KEYS.items()
                if key in v
                and any(
                    k == kind
                    and (
                        email_key(value) == email_key(v[key])
                        if kind == "email"
                        else value == v[key]
                    )
                    for k, value in aliases
                )
            }
            if "lookup_key" in v:
                matches |= {
                    (kind, v["lookup_key"])
                    for kind, value in aliases
                    if (
                        email_key(value) == email_key(v["lookup_key"])
                        if kind == "email"
                        else value == v["lookup_key"]
                    )
                }
            for kind, value in sorted(matches):
                links.append(
                    SubjectLink(
                        subject_id=identity.subject_id,
                        system_id=system,
                        resource_id=resource,
                        identifier_type=kind,
                        identifier_value=value,
                        source=SourceRef(
                            evidence_id=f.evidence_id,
                            locator=f.locator,
                            captured_at=f.captured_at,
                            observed_at=f.observed_at,
                        ),
                    )
                )
    return observations, links
