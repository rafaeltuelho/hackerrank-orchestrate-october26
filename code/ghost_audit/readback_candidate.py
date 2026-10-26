"""Conservative candidate proposals from literal participant readbacks.

This is partial inventory extraction, never a whole-case completeness certificate.
Every treatment still passes the existing evidence/condition validator.
"""

import re

from .agent import AuditProposal
from .data import email_key
from .grounding import CATEGORY_CONTENT, DIRECT_FIELDS, literal_fields
from .models import Observation, SourceRef, SubjectLink
from .readbacks import IDENTITY_KEYS, normalize_readbacks


def propose_readbacks(identity, sources, rules):
    observations, links = normalize_readbacks(list(sources.values()), identity)
    for f in sources.values():
        fields = literal_fields(f)
        resource = fields.get("resource_id")
        system = fields.get("origin_system") or fields.get("service")
        if not resource or not system or f.observed_at is None:
            continue
        if not (f.locator.startswith("sql:") and "/row:" in f.locator):
            continue
        # A literal SQL row is presence proof, not proof of redaction/anonymization.
        source = SourceRef(
            evidence_id=f.evidence_id,
            locator=f.locator,
            captured_at=f.captured_at,
            observed_at=f.observed_at,
        )
        for alias in identity.aliases:
            if alias.kind == "name":
                continue
            for key, kind in IDENTITY_KEYS.items():
                value = fields.get(key)
                matches = (
                    email_key(value) == email_key(alias.value)
                    if kind == "email" and value is not None
                    else value == alias.value
                )
                if alias.kind == kind and matches:
                    links.append(
                        SubjectLink(
                            subject_id=identity.subject_id,
                            system_id=system,
                            resource_id=resource,
                            identifier_type=kind,
                            identifier_value=alias.value,
                            source=source,
                        )
                    )
        observations.append(
            Observation(
                system_id=system,
                resource_id=resource,
                copy_id=f.locator.split("/")[0],
                state="PRESENT",
                source=source,
                proof_kind="SNAPSHOT",
                scope_complete=False,
                fields=fields,
            )
        )
    linked = {(link.system_id, link.resource_id) for link in links}
    observations = [o for o in observations if (o.system_id, o.resource_id) in linked]
    obligations, support = {}, []
    for obs in observations:
        f = sources[obs.source.evidence_id, obs.source.locator]
        fields = literal_fields(f)
        if "enabled" in fields:
            options = [("DATA_FLOW", "active_flow", "DISABLE")]
        elif "restore_allowed" in fields:
            options = [("RESTORE_PATH", "restore_risk", "BLOCK")]
        else:
            category = fields.get("data_category")
            if not category:
                matches = [
                    c
                    for c, regex in CATEGORY_CONTENT.items()
                    if re.search(regex, f.locator + "\n" + f.text, re.I)
                ]
                category = matches[0] if len(matches) == 1 else None
            options = [
                (r["data_category"], r["rule_id"], r["required_action"])
                for r in rules
                if r["data_category"] == category
            ]
        for category, rule_id, action in options:
            key = obs.system_id, obs.resource_id, action
            obligations[key] = dict(
                system_id=obs.system_id,
                resource_id=obs.resource_id,
                category=category,
                rule_id=rule_id,
                action=action,
                prohibited_fields=sorted(DIRECT_FIELDS & fields.keys())
                if action == "REDACT"
                else [],
                permitted_fields=sorted(set(fields) - DIRECT_FIELDS) if action == "REDACT" else [],
            )
            support.append(
                dict(
                    system_id=obs.system_id,
                    resource_id=obs.resource_id,
                    rule_id=rule_id,
                    evidence_id=f.evidence_id,
                    locator=f.locator,
                    quote=f.text,
                )
            )
    raw_obs = []
    for observation in observations:
        raw = observation.model_dump(mode="json")
        raw["fields"] = [{"name": k, "value": v} for k, v in observation.fields.items()]
        raw_obs.append(raw)
    return AuditProposal.model_validate_json(
        __import__("json").dumps(
            {
                "assessment": dict(
                    subject_id=identity.subject_id,
                    links=[link.model_dump(mode="json") for link in links],
                    observations=raw_obs,
                    obligations=list(obligations.values()),
                    dependencies=[],
                    coverage_complete=False,
                    gaps=[
                        "PARTIAL_LITERAL_READBACK_INVENTORY: unclassified artifacts "
                        "and dependencies require audit"
                    ],
                ),
                "policy_support": support,
            }
        )
    )
