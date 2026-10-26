"""Validate model proposals against exact retrieved participant fragments."""

import json
import re

from .agent import AuditProposal
from .data import Dataset, Identity, email_key, timestamp
from .evidence import Fragment, exact_match
from .models import Assessment, AuditError, Request, SourceRef
from .policy import validate_obligation
from .readbacks import log_values, normalize_readbacks
from .resource_links import matches_resource, resource_aliases

CATEGORY_CONTENT = {
    "USER_PROFILE": (
        r"customer_profiles|profile_lookup|user.profile|customer.profile|primary.profile|account.profile|"
        r"account.id|account.reference"
    ),
    "SECONDARY_IDENTIFIER": r"contact_lookup|contact.record|secondary.identifier|contact_directory",
    "SEARCH_INDEX_ENTRY": r"customer_search|index_query|search.index|customer_directory",
    "CACHE_ENTRY": r"cache.entry|cache.key|cached.profile",
    "SUPPORT_MESSAGE": r"support_records|support_ticket|message_scan|support.message|conversation",
    "SUPPORT_ATTACHMENT": r"attachment|object.storage|object_key",
    "ANALYTICS_PROFILE": r"analytics.profile|customer_analytics|analytics.report",
    "PRODUCT_TELEMETRY": r"telemetry|product.event",
    "USER_EXPORT": r"customer_exports|export.job|export.manifest|user.export|object_key|export.id",
    "MARKETING_PROFILE": r"marketing|email_opt_in|contact_lookup",
    "EMAIL_DELIVERY_LOG": r"email.delivery|delivery.log|recipient.email",
    "SECURITY_AUDIT_LOG": r"security_audit|audit_record_read|security.audit|audit.ledger",
    "LEGAL_HOLD_RECORD": r"legal.hold",
    "BACKUP_ARCHIVE": r"backup|restore_policy|archive",
    "ACCOUNT_TOMBSTONE": (
        r"tombstone|deleted.account.reference|deleted.customer.reference|"
        r"account_status.*DELETED"
    ),
}
DIRECT_FIELDS = {
    "name",
    "full_name",
    "display_name",
    "email",
    "phone",
    "email_hash",
    "requester_name",
    "requester_email",
    "requester_phone",
    "customer_email",
    "customer_phone",
    "customer_name",
    "owner_email",
    "owner_phone",
}
LINK_FIELDS = {"user_id", "customer_reference", "subject_reference", "customer_id", "account_id"}


def readable(fragment: Fragment) -> str:
    try:
        node = json.loads(fragment.text)
        if isinstance(node, dict) and "text" in node:
            return node["text"]
    except ValueError, TypeError:
        pass
    return fragment.text


def literal_fields(fragment: Fragment) -> dict[str, str | None]:
    if fragment.extracted_fields:
        return fragment.extracted_fields
    if fragment.locator.startswith(("visual:", "page:")):
        fields = {}
        ambiguous = set()
        for line in readable(fragment).splitlines():
            match = re.fullmatch(r"\s*([A-Za-z][A-Za-z _/-]{0,44})\s*[:|=]\s*(.*?)\s*", line)
            if not match:
                continue
            key, value = match.groups()
            key = re.sub(r"[\s/-]+", "_", key.strip().lower())
            if key in {"owner", "customer", "recipient"} and re.fullmatch(
                r"[^\s@]+@[^\s@]+", value
            ):
                key += "_email"
            if key in fields or key in ambiguous:
                ambiguous.add(key)
                fields.pop(key, None)  # Repeated table labels are not a unique record field.
                continue
            fields[key] = None if value.lower() in {"null", "none", "—"} else value
        return fields
    if fragment.locator.startswith("line:"):
        return {k: None if v == "null" else v for k, v in log_values(fragment).items()}
    result = {}
    conflicts = set()

    def visit(node):
        if isinstance(node, list):
            for value in node:
                visit(value)
            return
        if not isinstance(node, dict):
            return
        for k, v in node.items():
            if k == "record_json" and isinstance(v, str):
                visit(json.loads(v))
            elif isinstance(v, (dict, list)):
                visit(v)
            elif not isinstance(v, list):
                value = None if v is None else (json.dumps(v) if isinstance(v, bool) else str(v))
                if k in result and result[k] != value:
                    conflicts.add(k)
                result[k] = value

    try:
        visit(json.loads(fragment.text))
    except ValueError:
        pass
    for k in conflicts:
        if k in DIRECT_FIELDS | LINK_FIELDS:
            raise AuditError("AMBIGUOUS_IDENTIFIER_FIELDS")
        result.pop(k, None)
    return result


def source_fragment(source: SourceRef, sources: dict, request: Request) -> Fragment:
    f = sources.get((source.evidence_id, source.locator))
    if f is None:
        raise AuditError("UNRETRIEVED_SOURCE")
    if f.captured_at != source.captured_at or source.captured_at > request.audit_at:
        raise AuditError("INVALID_CAPTURE_TIME")
    if source.observed_at > request.audit_at:
        raise AuditError("FUTURE_OBSERVATION")
    if f.observed_at is not None:
        if source.time_precision != "EXACT" or f.observed_at != source.observed_at:
            raise AuditError("OBSERVATION_TIME_MISMATCH")
    elif source.time_precision == "DATE":
        if source.observed_at.hour or source.observed_at.minute or source.observed_at.second:
            raise AuditError("DATE_PRECISION_REQUIRES_MIDNIGHT_ANCHOR")
        dates = [
            source.observed_at.strftime(fmt)
            for fmt in ("%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%B %d, %Y")
        ]
        dates += [s.lstrip("0") for s in dates]
        # Only an explicit business creation/update/snapshot date may supply date precision.
        if not any(
            re.search(
                r"(?:^|\n)\s*(?:created|generated|issued|snapshot|observed|updated|"
                r"creation\s+date|date(?:\s+(?:created|issued|generated))?)"
                r"[^\n]{0,35}" + re.escape(d),
                readable(f),
                re.I,
            )
            for d in dates
        ):
            raise AuditError("UNSUPPORTED_OBSERVATION_DATE")
        start, end = source.observation_interval()
        if start > end or end > request.audit_at:
            raise AuditError("DATE_INTERVAL_NOT_ADMISSIBLE")
    else:
        iso = source.observed_at.isoformat().replace("+00:00", "Z")
        variants = [source.observed_at.isoformat(), iso]
        variants.extend(
            source.observed_at.strftime(fmt)
            for fmt in (
                "%d %b %Y %H:%M UTC",
                "%d %B %Y %H:%M UTC",
                "%Y-%m-%d %H:%M:%S UTC",
                "%Y-%m-%d %H:%M UTC",
                "%d %b %Y %H:%M:%S UTC",
            )
        )
        if not any(v in readable(f) for v in variants):
            raise AuditError("UNKNOWN_OBSERVATION_TIME")
    return f


def validate_proposal(
    proposal: AuditProposal,
    request: Request,
    identity: Identity,
    dataset: Dataset,
    sources: dict,
    *,
    require_coverage: bool = True,
) -> Assessment:
    assessment = proposal.assessment.to_domain()
    aliases_by_resource = resource_aliases(dataset, request, identity)
    canonical_observations = []
    for observation in assessment.observations:
        f = source_fragment(observation.source, sources, request)
        fields = literal_fields(f)
        if any(
            fields.get(k) not in (None, "", assessment.subject_id)
            for k in {"user_id", "customer_reference", "subject_reference"}
        ):
            raise AuditError("CURRENT_RESOURCE_OWNERSHIP_CONFLICT")
        if f.locator.startswith("sql:"):
            copy_id = f.locator.split("/", 1)[0]
        elif f.locator.startswith("visual:"):
            copy_id = "ui:" + dataset.files[f.evidence_id]["origin"]
        elif f.locator.startswith("page:"):
            copy_id = "document:" + f.evidence_id
        else:
            scopes = {k: v for k, v in fields.items() if k in {"region", "route", "pool"} and v}
            if fields.get("trace_id"):
                for other in sources.values():
                    values = literal_fields(other)
                    if (
                        other.evidence_id == f.evidence_id
                        and values.get("trace_id") == fields["trace_id"]
                        and values.get("service") == fields.get("service")
                        and other.observed_at is not None
                        and other.observed_at <= observation.source.observed_at
                    ):
                        scopes.update(
                            {
                                k: v
                                for k, v in values.items()
                                if k in {"region", "route", "pool"} and v
                            }
                        )
            copy_id = "/".join(f"{k}:{v}" for k, v in sorted(scopes.items())) or "unspecified"
        canonical_observations.append(observation.model_copy(update={"copy_id": copy_id}))
    assessment = assessment.model_copy(update={"observations": canonical_observations})
    if assessment.subject_id != identity.subject_id:
        raise AuditError("SUBJECT_MISMATCH")
    aliases = {(a.kind, a.value) for a in identity.aliases if a.kind != "name"}
    normalized, normalized_links = normalize_readbacks(list(sources.values()), identity)
    trace_links = {
        (
            link.system_id,
            link.resource_id,
            link.identifier_type,
            email_key(link.identifier_value)
            if link.identifier_type == "email"
            else link.identifier_value,
            link.source.evidence_id,
            link.source.locator,
        )
        for link in normalized_links
    }
    grounded_resources = {(link.system_id, link.resource_id) for link in normalized_links}
    proposed_resources = {(o.system_id, o.resource_id) for o in assessment.obligations}
    if require_coverage and not grounded_resources <= proposed_resources:
        raise AuditError("UNASSESSED_GROUNDED_RESOURCE")
    for obs in normalized:
        key = (obs.system_id, obs.resource_id)
        if key not in grounded_resources:
            continue
        required = (
            "BLOCK"
            if "restore_allowed" in obs.fields
            else "DISABLE"
            if "enabled" in obs.fields
            else None
        )
        if (
            require_coverage
            and required
            and not any(
                (o.system_id, o.resource_id, o.action) == (*key, required)
                for o in assessment.obligations
            )
        ):
            raise AuditError("UNASSESSED_GROUNDED_PROCESS")
    for dependency in assessment.dependencies:
        f = source_fragment(dependency.source, sources, request)
        if (
            not exact_match(dependency.before_resource, readable(f))
            or not exact_match(dependency.after_resource, readable(f))
            or not re.search(
                r"depend|before|downstream|upstream|source_resource|target_resource",
                readable(f),
                re.I,
            )
        ):
            raise AuditError("UNSUPPORTED_DEPENDENCY")
    for link in assessment.links:
        f = source_fragment(link.source, sources, request)
        if not any(
            kind == link.identifier_type
            and (
                email_key(value) == email_key(link.identifier_value)
                if kind == "email"
                else value == link.identifier_value
            )
            for kind, value in aliases
        ):
            raise AuditError("UNSUPPORTED_ALIAS")
        trace_key = (
            link.system_id,
            link.resource_id,
            link.identifier_type,
            email_key(link.identifier_value)
            if link.identifier_type == "email"
            else link.identifier_value,
            link.source.evidence_id,
            link.source.locator,
        )
        direct = matches_resource(link.resource_id, f, aliases_by_resource) and exact_match(
            link.identifier_value, readable(f)
        )
        if direct and "/record:" in f.locator:
            direct = literal_fields(f).get("resource_id") == link.resource_id or any(
                literal_fields(f).get("resource_id") == a["value"]
                for a in aliases_by_resource.get(link.resource_id, [])
            )
        elif direct and f.locator.startswith(("visual:", "page:")):
            # A whole table/page is not an ownership edge. Demand a common row/line;
            # multi-line detail panels need a narrower extraction before acceptance.
            direct = any(
                exact_match(link.resource_id, line) and exact_match(link.identifier_value, line)
                for line in readable(f).splitlines()
            )
        if not direct and trace_key not in trace_links:
            raise AuditError("UNSUPPORTED_SUBJECT_LINK")
    for obs in assessment.observations:
        f = source_fragment(obs.source, sources, request)
        content = readable(f)
        if not matches_resource(obs.resource_id, f, aliases_by_resource):
            raise AuditError("RESOURCE_NOT_IN_OBSERVATION")
        fields = literal_fields(f)
        systems = {fields[k] for k in ("service", "origin_system", "data_store") if fields.get(k)}
        if systems and obs.system_id not in systems:
            raise AuditError("SYSTEM_NOT_IN_OBSERVATION")
        if fields:
            if any(k not in fields or fields[k] != v for k, v in obs.fields.items()):
                raise AuditError("OBSERVATION_FIELD_MISMATCH")
            # Every explicitly exposed direct identifier must survive the proposal boundary.
            for key in DIRECT_FIELDS & fields.keys():
                if fields[key] not in (None, "") and obs.fields.get(key) != fields[key]:
                    raise AuditError("OMITTED_DIRECT_IDENTIFIER")
        else:
            # Unstructured values need literal field/value evidence; nulls cannot be guessed.
            for key, value in obs.fields.items():
                if key not in content or (value is not None and value not in content):
                    raise AuditError("UNSUPPORTED_ARTIFACT_FIELD")
                if value is None and not re.search(
                    re.escape(key) + r"\s*[:=]\s*(null|none|—)", content, re.I
                ):
                    raise AuditError("UNSUPPORTED_NULL_FIELD")
        if obs.proof_kind == "CLAIM" or f.evidence_id.startswith(("activity_", "audit_")):
            raise AuditError("CLAIM_NOT_STATE_PROOF")
        known = [
            o
            for o in normalized
            if o.resource_id == obs.resource_id
            and o.system_id == obs.system_id
            and o.source == obs.source
        ]
        if known and obs.state not in {o.state for o in known}:
            raise AuditError("READBACK_STATE_MISMATCH")
        if obs.state == "ABSENT" and not any(o.state == "ABSENT" for o in known):
            raise AuditError("ABSENCE_WITHOUT_SCOPED_LOOKUP")
        if obs.state in {"REDACTED", "ANONYMIZED"}:
            if any(v not in (None, "") for k, v in obs.fields.items() if k in DIRECT_FIELDS):
                raise AuditError("PII_IN_COMPLIANT_RECORD")
        if obs.state == "ANONYMIZED" and any(fields.get(k) not in (None, "") for k in LINK_FIELDS):
            raise AuditError("STABLE_REFERENCE_IN_ANONYMIZED_RECORD")
        if not known and obs.state in {"ACTIVE", "DISABLED", "BLOCKED"}:
            expected = {
                "ACTIVE": {"enabled": "true", "restore_allowed": "true"},
                "DISABLED": {"enabled": "false"},
                "BLOCKED": {"restore_allowed": "false"},
            }
            if not any(fields.get(k) == v for k, v in expected[obs.state].items()):
                raise AuditError("UNSUPPORTED_PROCESS_STATE")
    for obligation in assessment.obligations:
        support = [
            s
            for s in proposal.policy_support
            if (s.system_id, s.resource_id, s.rule_id)
            == (obligation.system_id, obligation.resource_id, obligation.rule_id)
        ]
        if not support:
            raise AuditError("MISSING_POLICY_SUPPORT")
        texts = []
        for s in support:
            f = sources.get((s.evidence_id, s.locator))
            if f is None or s.quote not in readable(f):
                raise AuditError("UNSUPPORTED_POLICY_QUOTE")
            # The policy receipt must concern this resource, not a neighbor in a bundle.
            if not matches_resource(s.resource_id, f, aliases_by_resource):
                raise AuditError("UNLINKED_POLICY_SUPPORT")
            texts.append(f.locator + "\n" + readable(f))
        content = "\n".join(texts)
        explicit_category = any(
            literal_fields(sources[s.evidence_id, s.locator]).get("data_category")
            == obligation.category
            for s in support
        )
        if obligation.category == "USER_EXPORT":
            # A catalog-identified copy delivered by the export service can contain a
            # statement/invoice; do not confuse that exported copy with an original finance record.
            linked = aliases_by_resource.get(obligation.resource_id, [])
            catalog_copy = any(
                a["system_id"] == obligation.system_id == "export_service"
                and any(key[0] == a["activity_id"] for key in sources)
                for a in linked
            )
            doc_copy = any(
                "business_document_content_capture" in sources[s.evidence_id, s.locator].text
                for s in support
            )
            explicit_category = explicit_category or (catalog_copy and doc_copy)
        if (
            obligation.action not in {"DISABLE", "BLOCK"}
            and not explicit_category
            and not re.search(CATEGORY_CONTENT.get(obligation.category, r"(?!)"), content, re.I)
        ):
            raise AuditError("UNSUPPORTED_CATEGORY")
        observations = [
            o
            for o in assessment.observations
            if (o.system_id, o.resource_id) == (obligation.system_id, obligation.resource_id)
        ]
        conditions = set()
        if obligation.action == "DISABLE" and any(
            o.state in {"ACTIVE", "DISABLED"} for o in observations
        ):
            conditions.add("active_flow")
        if obligation.action == "BLOCK" and any(
            o.state in {"ACTIVE", "BLOCKED"} for o in observations
        ):
            conditions.add("restore_risk")
        if obligation.category in {"ANALYTICS_PROFILE", "PRODUCT_TELEMETRY"}:
            conditions.add(obligation.rule_id)  # Grounded subject-specific treatment obligation.
        if obligation.category == "SECURITY_AUDIT_LOG":
            retained = [
                v
                for o in observations
                for k, v in o.fields.items()
                if k in {"retention_until", "retained_until"} and v
            ]
            if retained and all(timestamp(v) >= request.audit_at for v in retained):
                conditions.add(obligation.rule_id)
        if obligation.category == "ACCOUNT_TOMBSTONE" and re.search(
            r"DELETED|tombstone", content, re.I
        ):
            conditions.add(obligation.rule_id)
        if obligation.category == "BACKUP_ARCHIVE" and re.search(
            r"restore_allowed|restore.access", content, re.I
        ):
            conditions.add(obligation.rule_id)
        if obligation.category == "SUPPORT_MESSAGE" and re.search(
            r"agent|order|shared|conversation", content, re.I
        ):
            conditions.add(obligation.rule_id)
        if obligation.category == "SUPPORT_ATTACHMENT" and re.search(
            r"exclusiv|only.*subject|sole.owner", content, re.I
        ):
            conditions.add(obligation.rule_id)
        if obligation.category == "EMAIL_DELIVERY_LOG" and any(
            o.fields.get("email") not in (None, "") for o in observations
        ):
            conditions.add(obligation.rule_id)
        if obligation.action == "REDACT":
            pii = {k for o in observations for k in o.fields if k in DIRECT_FIELDS}
            if not pii or not pii <= set(obligation.prohibited_fields):
                raise AuditError("INCOMPLETE_REDACTION_POLICY")
            if obligation.category == "ACCOUNT_TOMBSTONE":
                for group in (
                    {"name", "full_name", "display_name"},
                    {"email", "customer_email"},
                    {"phone", "customer_phone"},
                    {"email_hash"},
                ):
                    if not any(group & o.fields.keys() for o in observations):
                        raise AuditError("MISSING_TOMBSTONE_IDENTIFIER_FIELD")
        validate_obligation(obligation, dataset.rules, conditions)
    return assessment
