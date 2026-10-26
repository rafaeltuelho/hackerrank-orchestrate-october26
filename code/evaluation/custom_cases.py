"""Authored A01–A03 source inventories, frozen task doubles and independent answers.

These task doubles test contracts/orchestration, not model interpretation. No fixture
or expected answer is imported by production code. All identifiers are fictional.
"""

from dataclasses import dataclass
from datetime import datetime

from ghost_audit.models import (
    Assessment,
    Authorization,
    Obligation,
    Observation,
    Request,
    Result,
    SourceRef,
    Step,
    SubjectLink,
)


@dataclass
class CustomCase:
    request: Request
    authorization: Authorization
    assessment: Assessment | None
    expected: Result
    inventory: str


def request(number: int, text: str) -> Request:
    return Request(
        case_id=f"custom_a{number:02}",
        email=f"sample{number:02}@example.invalid",
        requested_at=datetime.fromisoformat("2026-06-10T10:00:00Z"),
        reported_status="COMPLETE",
        reported_at=datetime.fromisoformat("2026-06-10T11:00:00Z"),
        audit_at=datetime.fromisoformat("2026-06-10T12:00:00Z"),
        request_text=text,
    )


def fixtures() -> list[CustomCase]:
    cases = []
    texts = [
        "Please send me a copy of my records. Do not delete my account.",
        "Permanently delete my account and remaining copies.",
        "Delete my personal details, keeping only references required for retained records.",
    ]
    for n, text in enumerate(texts, 1):
        req = request(n, text)
        auth = Authorization(intent="NON_DELETION" if n == 1 else "DELETE", request_spans=[text])
        if n == 1:
            cases.append(
                CustomCase(
                    req,
                    auth,
                    None,
                    Result(case_id=req.case_id, deletion_status="NOT_APPLICABLE", steps=[]),
                    "Empty: discovery must never execute.",
                )
            )
            continue
        subject = f"custom_user_{n:02}"
        evidence = f"custom_e{n:02}"
        capture = f"2026-06-10T11:{50 if n == 2 else 55}:00Z"
        resources = (
            [
                (
                    "search_service",
                    "search_custom02",
                    "PRESENT",
                    "SEARCH_INDEX_ENTRY",
                    "rule_03",
                    "DELETE",
                    {},
                ),
                (
                    "integration_service",
                    "flow_custom02",
                    "ACTIVE",
                    "DATA_FLOW",
                    "active_flow",
                    "DISABLE",
                    {"enabled": "true"},
                ),
            ]
            if n == 2
            else [
                (
                    "account_service",
                    "account_custom03",
                    "ABSENT",
                    "USER_PROFILE",
                    "rule_01",
                    "DELETE",
                    {},
                ),
                (
                    "identity_service",
                    "tombstone_custom03",
                    "REDACTED",
                    "ACCOUNT_TOMBSTONE",
                    "rule_15",
                    "REDACT",
                    {
                        "subject_reference": subject,
                        "name": None,
                        "email": None,
                        "phone": None,
                        "email_hash": None,
                    },
                ),
                (
                    "security_service",
                    "audit_custom03",
                    "PRESENT",
                    "SECURITY_AUDIT_LOG",
                    "rule_12",
                    "RETAIN",
                    {"retained_until": "2030-12-31T23:59:59Z"},
                ),
            ]
        )
        links, observations, obligations = [], [], []
        for i, (system, resource, state, category, rule, action, fields) in enumerate(resources):
            ref = SourceRef(
                evidence_id=evidence,
                locator=f"/readbacks/{i}",
                captured_at=datetime.fromisoformat(capture),
                observed_at=datetime.fromisoformat(f"2026-06-10T11:{45 + i}:00Z"),
            )
            links.append(
                SubjectLink(
                    subject_id=subject,
                    system_id=system,
                    resource_id=resource,
                    identifier_type="user_id",
                    identifier_value=subject,
                    source=ref,
                )
            )
            observations.append(
                Observation(
                    system_id=system,
                    resource_id=resource,
                    copy_id="primary",
                    state=state,
                    source=ref,
                    proof_kind="CONFIGURATION" if action == "DISABLE" else "READBACK",
                    scope_complete=True,
                    fields=fields,
                )
            )
            obligations.append(
                Obligation(
                    system_id=system,
                    resource_id=resource,
                    category=category,
                    rule_id=rule,
                    action=action,
                    prohibited_fields=["name", "email", "phone", "email_hash"]
                    if action == "REDACT"
                    else [],
                    permitted_fields=["subject_reference"] if action == "REDACT" else [],
                )
            )
        assessment = Assessment(
            subject_id=subject,
            links=links,
            observations=observations,
            obligations=obligations,
            dependencies=[],
            coverage_complete=True,
            gaps=[],
        )
        # Independent literal operation sequences from the approved acceptance tables.
        expected_rows = (
            [
                (
                    "FINDING",
                    "search_service",
                    "search_custom02",
                    "REPORT_REMAINING_RECORD",
                    "PRESENT",
                    evidence,
                ),
                (
                    "FINDING",
                    "integration_service",
                    "flow_custom02",
                    "REPORT_ACTIVE_DATA_FLOW",
                    "ACTIVE",
                    evidence,
                ),
                (
                    "REMEDIATION",
                    "integration_service",
                    "flow_custom02",
                    "DISABLE_DATA_FLOW",
                    "DISABLED",
                    "",
                ),
                ("REMEDIATION", "search_service", "search_custom02", "DELETE_RECORD", "ABSENT", ""),
                (
                    "VERIFICATION",
                    "search_service",
                    "search_custom02",
                    "VERIFY_RECORD_ABSENT",
                    "ABSENT",
                    "",
                ),
                (
                    "VERIFICATION",
                    "integration_service",
                    "flow_custom02",
                    "VERIFY_DATA_FLOW_DISABLED",
                    "DISABLED",
                    "",
                ),
            ]
            if n == 2
            else [
                (
                    "VERIFICATION",
                    "account_service",
                    "account_custom03",
                    "VERIFY_RECORD_ABSENT",
                    "ABSENT",
                    evidence,
                ),
                (
                    "VERIFICATION",
                    "security_service",
                    "audit_custom03",
                    "VERIFY_RECORD_PRESENT",
                    "PRESENT",
                    evidence,
                ),
                (
                    "VERIFICATION",
                    "identity_service",
                    "tombstone_custom03",
                    "VERIFY_RECORD_REDACTED",
                    "REDACTED",
                    evidence,
                ),
            ]
        )
        expected = Result(
            case_id=req.case_id,
            deletion_status="INCOMPLETE" if n == 2 else "COMPLETE",
            steps=[
                Step(
                    step_no=i,
                    phase=p,
                    system_id=s,
                    resource_id=r,
                    operation=o,
                    state=t,
                    evidence_id=e,
                )
                for i, (p, s, r, o, t, e) in enumerate(expected_rows, 1)
            ],
        )
        inventory = (
            "Complete: exact subject-linked search readback and enabled connector; "
            "SEARCH_INDEX_ENTRY DELETE and active-flow control."
            if n == 2
            else "Complete: scoped empty account lookup, stable tombstone with all prohibited "
            "fields null, and security record retained through 2030; DELETE/REDACT/RETAIN."
        )
        cases.append(CustomCase(req, auth, assessment, expected, inventory))
    return cases
