"""Typed boundaries; observations, ownership and output remain distinct."""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Nonempty = Annotated[str, Field(min_length=1)]
State = Literal["PRESENT", "ABSENT", "REDACTED", "ANONYMIZED", "ACTIVE", "DISABLED", "BLOCKED"]
Action = Literal["DELETE", "REDACT", "ANONYMIZE", "RETAIN", "DISABLE", "BLOCK"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class Request(Contract):
    case_id: Nonempty
    email: Nonempty
    requested_at: datetime
    reported_status: Literal["COMPLETE", "PARTIALLY_COMPLETE", "NOT_STARTED"]
    reported_at: datetime
    audit_at: datetime
    request_text: Nonempty

    @field_validator("requested_at", "reported_at", "audit_at")
    @classmethod
    def aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timezone required")
        return value


class Authorization(Contract):
    intent: Literal["DELETE", "AUDIT_PRIOR_DELETION", "NON_DELETION", "UNRESOLVED"]
    request_spans: list[Nonempty]


class SourceRef(Contract):
    evidence_id: Nonempty
    locator: Nonempty
    captured_at: datetime
    observed_at: datetime
    time_precision: Literal["EXACT", "DATE"] = "EXACT"

    def observation_interval(self) -> tuple[datetime, datetime]:
        if self.time_precision == "EXACT":
            return self.observed_at, self.observed_at
        # Calendar-only dates have no invented clock time or assumed local timezone.
        anchor = datetime.combine(self.observed_at.date(), datetime.min.time(), tzinfo=UTC)
        return anchor - timedelta(hours=14), min(anchor + timedelta(hours=36), self.captured_at)

    @field_validator("captured_at", "observed_at")
    @classmethod
    def aware(cls, value: datetime) -> datetime:
        return Request.aware(value)


class SubjectLink(Contract):
    subject_id: Nonempty
    system_id: Nonempty
    resource_id: Nonempty
    identifier_type: Nonempty
    identifier_value: Nonempty
    source: SourceRef


class Observation(Contract):
    system_id: Nonempty
    resource_id: Nonempty
    copy_id: Nonempty
    state: State
    source: SourceRef
    proof_kind: Literal["READBACK", "SNAPSHOT", "CONFIGURATION", "ARTIFACT", "CLAIM"]
    scope_complete: bool
    # Fields are literal extracted values, not a model's compliant-state label.
    fields: dict[str, str | None]


class Obligation(Contract):
    system_id: Nonempty
    resource_id: Nonempty
    category: Nonempty
    rule_id: Nonempty
    action: Action
    prohibited_fields: list[Nonempty]
    permitted_fields: list[Nonempty]


class Dependency(Contract):
    before_system: Nonempty
    before_resource: Nonempty
    after_system: Nonempty
    after_resource: Nonempty
    source: SourceRef


class Assessment(Contract):
    subject_id: Nonempty
    links: list[SubjectLink]
    observations: list[Observation]
    obligations: list[Obligation]
    dependencies: list[Dependency]
    coverage_complete: bool
    gaps: list[Nonempty]


class Step(Contract):
    step_no: Annotated[int, Field(ge=1)]
    phase: Literal["FINDING", "REMEDIATION", "VERIFICATION"]
    system_id: Nonempty
    resource_id: Nonempty
    operation: Nonempty
    state: State
    evidence_id: str


class Result(Contract):
    case_id: Nonempty
    deletion_status: Literal["COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"]
    steps: list[Step]


class AuditError(ValueError):
    """An internal failure, never a fourth output status."""
