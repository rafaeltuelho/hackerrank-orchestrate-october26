"""Exact operation registry, contract validation and atomic CSV publication."""

import csv
import json
import os
import tempfile
from pathlib import Path

from .models import AuditError, Result, Step

# Insertion order is the contract's canonical operation order.
OPERATIONS = {
    "REPORT_REMAINING_RECORD": ("FINDING", "PRESENT"),
    "REPORT_EXPOSED_PII": ("FINDING", "PRESENT"),
    "REPORT_ACTIVE_DATA_FLOW": ("FINDING", "ACTIVE"),
    "REPORT_RESTORE_RISK": ("FINDING", "ACTIVE"),
    "DISABLE_DATA_FLOW": ("REMEDIATION", "DISABLED"),
    "BLOCK_RESTORE": ("REMEDIATION", "BLOCKED"),
    "DELETE_RECORD": ("REMEDIATION", "ABSENT"),
    "REDACT_RECORD": ("REMEDIATION", "REDACTED"),
    "ANONYMIZE_RECORD": ("REMEDIATION", "ANONYMIZED"),
    "VERIFY_RECORD_ABSENT": ("VERIFICATION", "ABSENT"),
    "VERIFY_RECORD_PRESENT": ("VERIFICATION", "PRESENT"),
    "VERIFY_RECORD_REDACTED": ("VERIFICATION", "REDACTED"),
    "VERIFY_RECORD_ANONYMIZED": ("VERIFICATION", "ANONYMIZED"),
    "VERIFY_DATA_FLOW_DISABLED": ("VERIFICATION", "DISABLED"),
    "VERIFY_RESTORE_BLOCKED": ("VERIFICATION", "BLOCKED"),
}
RANK = {op: n for n, op in enumerate(OPERATIONS)}
HEADER = ["case_id", "deletion_status", "steps_json"]


def sort_key(step: Step) -> tuple[int, str, str]:
    if step.operation not in OPERATIONS:
        raise AuditError("UNKNOWN_OPERATION")
    return RANK[step.operation], step.system_id, step.resource_id


def make_step(operation: str, system: str, resource: str, evidence: str = "") -> Step:
    phase, state = OPERATIONS[operation]
    return Step(
        step_no=1,
        phase=phase,
        system_id=system,
        resource_id=resource,
        operation=operation,
        state=state,
        evidence_id=evidence,
    )


def canonical_steps(steps: list[Step]) -> list[Step]:
    return [
        s.model_copy(update={"step_no": n}) for n, s in enumerate(sorted(steps, key=sort_key), 1)
    ]


def validate_result(
    result: Result, evidence_ids: set[str] | None = None, *, semantic: bool = True
) -> None:
    steps = result.steps
    if result.deletion_status == "NOT_APPLICABLE":
        if steps:
            raise AuditError("NON_DELETION_HAS_STEPS")
        return
    if semantic and not steps:
        raise AuditError("EMPTY_AUTHORIZED_RESULT")
    if [s.step_no for s in steps] != list(range(1, len(steps) + 1)):
        raise AuditError("NONCONSECUTIVE_STEPS")
    if steps != sorted(steps, key=sort_key):
        raise AuditError("NONCANONICAL_ORDER")
    seen = set()
    for s in steps:
        if OPERATIONS.get(s.operation) != (s.phase, s.state):
            raise AuditError("INVALID_OPERATION_PHASE_STATE")
        key = (s.operation, s.system_id, s.resource_id)
        if key in seen:
            raise AuditError("DUPLICATE_STEP")
        seen.add(key)
        needs_evidence = s.phase == "FINDING" or result.deletion_status == "COMPLETE"
        if needs_evidence != bool(s.evidence_id):
            raise AuditError("INVALID_CITATION_MODE")
        if needs_evidence and evidence_ids is not None and s.evidence_id not in evidence_ids:
            raise AuditError("UNKNOWN_CITATION")
        if result.deletion_status == "COMPLETE" and s.phase != "VERIFICATION":
            raise AuditError("COMPLETE_HAS_NONVERIFICATION")
    if semantic and result.deletion_status == "INCOMPLETE":
        if {s.phase for s in steps} != {"FINDING", "REMEDIATION", "VERIFICATION"}:
            raise AuditError("INCOMPLETE_MISSING_PHASE")
        repairs = {
            "REPORT_REMAINING_RECORD": ("DELETE_RECORD", "VERIFY_RECORD_ABSENT"),
            "REPORT_EXPOSED_PII": None,
            "REPORT_ACTIVE_DATA_FLOW": ("DISABLE_DATA_FLOW", "VERIFY_DATA_FLOW_DISABLED"),
            "REPORT_RESTORE_RISK": ("BLOCK_RESTORE", "VERIFY_RESTORE_BLOCKED"),
        }
        needed_actions = set()
        for s in steps:
            if s.phase != "FINDING":
                continue
            options = (
                [repairs[s.operation]]
                if repairs[s.operation]
                else [
                    ("REDACT_RECORD", "VERIFY_RECORD_REDACTED"),
                    ("ANONYMIZE_RECORD", "VERIFY_RECORD_ANONYMIZED"),
                ]
            )
            matching = [
                (a, v)
                for a, v in options
                if (a, s.system_id, s.resource_id) in seen
                and (v, s.system_id, s.resource_id) in seen
            ]
            if len(matching) != 1:
                raise AuditError("FINDING_WITHOUT_UNIQUE_REPAIR_AND_CHECK")
            needed_actions.add((matching[0][0], s.system_id, s.resource_id))
        actual_actions = {
            (s.operation, s.system_id, s.resource_id) for s in steps if s.phase == "REMEDIATION"
        }
        if needed_actions != actual_actions:
            raise AuditError("REMEDIATION_WITHOUT_FINDING")


def write_csv(
    path: Path, results: list[Result], expected_ids: list[str], *, semantic: bool = True
) -> None:
    ids = [r.case_id for r in results]
    if len(set(expected_ids)) != len(expected_ids) or sorted(ids) != sorted(expected_ids):
        raise AuditError("CASE_SET_MISMATCH")
    for result in results:
        validate_result(result, semantic=semantic)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADER, lineterminator="\n")
            writer.writeheader()
            for result in sorted(results, key=lambda r: r.case_id):
                writer.writerow(
                    {
                        "case_id": result.case_id,
                        "deletion_status": result.deletion_status,
                        "steps_json": json.dumps(
                            [s.model_dump() for s in result.steps],
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                    }
                )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
