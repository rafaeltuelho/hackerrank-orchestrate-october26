"""Recover an unmatched request email only through explicit pre-cutoff subject evidence."""

from .data import Alias, Dataset, Identity
from .evidence import EvidenceStore
from .grounding import literal_fields
from .models import AuditError, Request


def resolve_identity(dataset: Dataset, store: EvidenceStore, request: Request) -> Identity:
    try:
        return dataset.resolve_identity(request.email, request.audit_at)
    except AuditError as exc:
        if str(exc) != "UNRESOLVED_IDENTITY":
            raise
    subjects = {r["user_id"] for r in dataset.identities} | {r["user_id"] for r in dataset.history}
    email_traces = set()
    candidates = {}
    fragments = []
    offset = 0
    while True:
        result = store.search([request.email], request.audit_at, offset, 100)
        fragments.extend(result.fragments)
        for f in result.fragments:
            values = literal_fields(f)
            if values.get("trace_id") and values.get("service"):
                email_traces.add((f.evidence_id, values["service"], values["trace_id"]))
        if result.next_offset is None:
            break
        offset = result.next_offset
    # Trace completion may name the subject separately from a scoped email lookup start.
    if email_traces:
        result = store.search(
            sorted({trace for _, _, trace in email_traces}), request.audit_at, limit=100
        )
        if result.next_offset is not None:
            raise AuditError("IDENTITY_TRACE_COVERAGE_LIMIT")
        fragments.extend(result.fragments)
    for f in fragments:
        fields = literal_fields(f)
        email_fields = {"email", "customer_email", "requester_email", "owner_email", "lookup_key"}
        direct = any(fields.get(k) == request.email for k in email_fields)
        traced = (f.evidence_id, fields.get("service"), fields.get("trace_id")) in email_traces
        if not direct and not traced:
            continue
        for key in ("user_id", "customer_reference", "subject_reference"):
            subject = fields.get(key)
            if subject in subjects:
                candidates.setdefault(subject, []).append(f)
    if len(candidates) != 1:
        raise AuditError("UNRESOLVED_IDENTITY" if not candidates else "AMBIGUOUS_IDENTITY")
    subject = next(iter(candidates))
    # Do not import any current-snapshot fields whose updated_at is after this cutoff.
    aliases = list(dataset.aliases_at(request.audit_at).get(subject, []))
    for f in candidates[subject]:
        aliases.extend(
            [
                Alias(
                    kind="user_id",
                    value=subject,
                    evidence_id=f.evidence_id,
                    available_at=f.captured_at,
                ),
                Alias(
                    kind="email",
                    value=request.email,
                    evidence_id=f.evidence_id,
                    available_at=f.captured_at,
                ),
            ]
        )
    return Identity(subject_id=subject, aliases=aliases)
