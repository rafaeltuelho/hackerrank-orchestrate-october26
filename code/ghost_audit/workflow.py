"""Deterministic assessment reduction and planning; no SDK dependency."""

from collections import defaultdict

from .models import Assessment, AuditError, Authorization, Observation, Request, Result, SourceRef
from .output import canonical_steps, make_step, validate_result

TARGETS = {
    "DELETE": ("ABSENT", "REPORT_REMAINING_RECORD", "DELETE_RECORD", "VERIFY_RECORD_ABSENT"),
    "REDACT": ("REDACTED", "REPORT_EXPOSED_PII", "REDACT_RECORD", "VERIFY_RECORD_REDACTED"),
    "ANONYMIZE": (
        "ANONYMIZED",
        "REPORT_EXPOSED_PII",
        "ANONYMIZE_RECORD",
        "VERIFY_RECORD_ANONYMIZED",
    ),
    "RETAIN": ("PRESENT", "", "", "VERIFY_RECORD_PRESENT"),
    "DISABLE": (
        "DISABLED",
        "REPORT_ACTIVE_DATA_FLOW",
        "DISABLE_DATA_FLOW",
        "VERIFY_DATA_FLOW_DISABLED",
    ),
    "BLOCK": ("BLOCKED", "REPORT_RESTORE_RISK", "BLOCK_RESTORE", "VERIFY_RESTORE_BLOCKED"),
}


def admissible(source: SourceRef, request: Request) -> bool:
    start, end = source.observation_interval()
    return source.captured_at <= request.audit_at and start <= end <= request.audit_at


def reduce_copies(observations: list[Observation]) -> list[Observation]:
    """Latest authoritative readback per physical copy; retain same-time conflicts."""
    copies = defaultdict(list)
    for obs in observations:
        if obs.proof_kind != "CLAIM":
            copies[obs.copy_id].append(obs)
    reduced = []
    for values in copies.values():
        latest_start = max(o.source.observation_interval()[0] for o in values)
        latest = [o for o in values if o.source.observation_interval()[1] >= latest_start]
        if len({(o.state, tuple(sorted(o.fields.items()))) for o in latest}) > 1:
            raise AuditError("CONFLICTING_READBACKS")
        reduced.append(min(latest, key=lambda o: (o.source.evidence_id, o.source.locator)))
    return reduced


def assemble(
    request: Request, authorization: Authorization, assessment: Assessment | None = None
) -> Result:
    if not authorization.request_spans or any(
        span not in request.request_text for span in authorization.request_spans
    ):
        raise AuditError("UNSUPPORTED_INTENT_SPAN")
    if authorization.intent == "UNRESOLVED":
        raise AuditError("UNRESOLVED_INTENT")
    if authorization.intent == "NON_DELETION":
        return Result(case_id=request.case_id, deletion_status="NOT_APPLICABLE", steps=[])
    if assessment is None or not assessment.coverage_complete or assessment.gaps:
        raise AuditError("INCOMPLETE_EVIDENCE_COVERAGE")
    obligations = {(o.system_id, o.resource_id, o.action): o for o in assessment.obligations}
    if not obligations or len(obligations) != len(assessment.obligations):
        raise AuditError("MISSING_OR_DUPLICATE_OBLIGATION")
    links = {
        (link.system_id, link.resource_id)
        for link in assessment.links
        if link.subject_id == assessment.subject_id and admissible(link.source, request)
    }
    if not {(s, r) for s, r, _ in obligations} <= links:
        raise AuditError("UNGROUNDED_SUBJECT_RESOURCE")
    grouped = defaultdict(list)
    for obs in assessment.observations:
        if admissible(obs.source, request):
            grouped[obs.system_id, obs.resource_id].append(obs)
    if set(grouped) - {(s, r) for s, r, _ in obligations}:
        raise AuditError("OBSERVATION_WITHOUT_POLICY")
    findings, actions, checks = [], [], []
    for (system, resource, _), obligation in sorted(obligations.items()):
        key = (system, resource)
        candidates = grouped[key]
        if obligation.action == "BLOCK":
            candidates = [o for o in candidates if o.state in {"ACTIVE", "BLOCKED"}]
        elif obligation.action == "DISABLE":
            candidates = [o for o in candidates if o.state in {"ACTIVE", "DISABLED"}]
        else:
            candidates = [o for o in candidates if o.state not in {"ACTIVE", "DISABLED", "BLOCKED"}]
        copies = reduce_copies(candidates)
        if not copies:
            raise AuditError("NO_STATE_PROOF")
        target, finding, action, check = TARGETS[obligation.action]
        violations = []
        for obs in copies:
            # A zero row observation must represent a successful complete scoped lookup.
            if obs.state == "ABSENT" and not obs.scope_complete:
                raise AuditError("UNSCOPED_ABSENCE")
            compliant = obs.state == target
            if obligation.action == "REDACT":
                required = set(obligation.prohibited_fields)
                if not required or not required <= obs.fields.keys():
                    raise AuditError("MISSING_REDACTION_FIELDS")
                if set(obs.fields) - required - set(obligation.permitted_fields):
                    raise AuditError("UNCLASSIFIED_RETAINED_FIELDS")
                compliant = obs.state in {"PRESENT", "REDACTED"} and all(
                    obs.fields[k] in (None, "") for k in required
                )
                if obligation.category == "ACCOUNT_TOMBSTONE":
                    compliant = compliant and (
                        obs.fields.get("subject_reference") == assessment.subject_id
                    )
            if not compliant:
                if obligation.action == "RETAIN":
                    raise AuditError("UNREPRESENTABLE_OBLIGATION")
                if obs.state in {"ABSENT", "BLOCKED", "DISABLED"} and target != obs.state:
                    raise AuditError("UNREPRESENTABLE_OR_UNKNOWN_STATE")
                violations.append(obs)
        proof = min(
            violations or copies, key=lambda o: (o.source.evidence_id, o.copy_id)
        ).source.evidence_id
        if violations:
            findings.append(make_step(finding, *key, proof))
            actions.append(make_step(action, *key))
        checks.append(make_step(check, *key, proof))
    incomplete = bool(findings)
    if incomplete:
        checks = [s.model_copy(update={"evidence_id": ""}) for s in checks]
    steps = canonical_steps(findings + actions + checks)
    positions = {(s.system_id, s.resource_id): s.step_no for s in steps if s.phase == "REMEDIATION"}
    for dep in assessment.dependencies:
        if not admissible(dep.source, request):
            raise AuditError("INADMISSIBLE_DEPENDENCY")
        before = positions.get((dep.before_system, dep.before_resource))
        after = positions.get((dep.after_system, dep.after_resource))
        if before is not None and after is not None and before >= after:
            raise AuditError("ORDER_CONFLICT")
    result = Result(
        case_id=request.case_id,
        deletion_status="INCOMPLETE" if incomplete else "COMPLETE",
        steps=steps,
    )
    evidence_ids = {
        o.source.evidence_id for o in assessment.observations if admissible(o.source, request)
    }
    validate_result(result, evidence_ids)
    return result
