import csv
import json
from datetime import timedelta

import pytest
from evaluation.custom_cases import fixtures
from evaluation.main import score
from ghost_audit.models import AuditError, Dependency, Result, Step
from ghost_audit.output import OPERATIONS, canonical_steps, validate_result, write_csv
from ghost_audit.workflow import assemble
from pydantic import ValidationError


@pytest.mark.parametrize("case", fixtures(), ids=lambda c: c.request.case_id)
def test_acceptance(case):
    assert assemble(case.request, case.authorization, case.assessment) == case.expected


def test_non_deletion_never_reads_assessment():
    case = fixtures()[0]
    assert assemble(case.request, case.authorization, object()) == case.expected


@pytest.mark.parametrize("operation,pair", OPERATIONS.items())
def test_registered_pairs_and_reject_wrong_state(operation, pair):
    phase, state = pair
    step = Step(
        step_no=1,
        phase=phase,
        state=state,
        operation=operation,
        system_id="s",
        resource_id="r",
        evidence_id="e",
    )
    bad = step.model_copy(update={"state": "ACTIVE" if state != "ACTIVE" else "PRESENT"})
    result = Result(case_id="c", deletion_status="COMPLETE", steps=[bad])
    with pytest.raises(AuditError):
        validate_result(result)


def test_extra_fields_and_coercion_rejected():
    raw = fixtures()[2].expected.steps[0].model_dump()
    with pytest.raises(ValidationError):
        Step.model_validate({**raw, "step_no": "1"})
    with pytest.raises(ValidationError):
        Step.model_validate({**raw, "explanation": "extra"})


@pytest.mark.parametrize(
    "mutation", ["number", "order", "citation", "unknown", "duplicate", "repair", "phase"]
)
def test_malformed_output(mutation):
    result = fixtures()[1].expected
    steps = list(result.steps)
    if mutation == "number":
        steps[0] = steps[0].model_copy(update={"step_no": 2})
    elif mutation == "order":
        steps[0], steps[1] = steps[1], steps[0]
        steps = [s.model_copy(update={"step_no": i}) for i, s in enumerate(steps, 1)]
    elif mutation == "citation":
        steps[2] = steps[2].model_copy(update={"evidence_id": "custom_e02"})
    elif mutation == "unknown":
        steps[0] = steps[0].model_copy(update={"evidence_id": "invented"})
    elif mutation == "duplicate":
        steps = canonical_steps(steps + [steps[0]])
    elif mutation == "repair":
        steps = canonical_steps([s for s in steps if s.operation != "DELETE_RECORD"])
    else:
        steps[0] = steps[0].model_copy(update={"phase": "VERIFICATION"})
    with pytest.raises(AuditError):
        validate_result(result.model_copy(update={"steps": steps}), {"custom_e02"})


@pytest.mark.parametrize(
    "failure",
    ["late", "unlinked", "claim", "coverage", "partial", "retention", "conflict", "order"],
)
def test_unsupported_assessment(failure):
    case = fixtures()[2]
    a = case.assessment
    if failure == "late":
        obs = a.observations[0]
        source = obs.source.model_copy(update={"captured_at": case.request.audit_at + timedelta(1)})
        a = a.model_copy(
            update={
                "observations": [obs.model_copy(update={"source": source}), *a.observations[1:]]
            }
        )
    elif failure == "unlinked":
        a = a.model_copy(update={"links": a.links[1:]})
    elif failure == "claim":
        a = a.model_copy(
            update={
                "observations": [
                    o.model_copy(update={"proof_kind": "CLAIM"}) for o in a.observations
                ]
            }
        )
    elif failure == "coverage":
        a = a.model_copy(update={"coverage_complete": False})
    elif failure == "partial":
        a = a.model_copy(
            update={
                "observations": [
                    a.observations[0].model_copy(update={"scope_complete": False}),
                    *a.observations[1:],
                ]
            }
        )
    elif failure == "retention":
        a = a.model_copy(
            update={
                "observations": [
                    *a.observations[:2],
                    a.observations[2].model_copy(update={"state": "ABSENT"}),
                ]
            }
        )
    elif failure == "conflict":
        a = a.model_copy(
            update={
                "observations": [
                    *a.observations,
                    a.observations[0].model_copy(update={"state": "PRESENT"}),
                ]
            }
        )
    else:
        case = fixtures()[1]
        a = case.assessment
        dep = Dependency(
            before_system="search_service",
            before_resource="search_custom02",
            after_system="integration_service",
            after_resource="flow_custom02",
            source=a.observations[0].source,
        )
        a = a.model_copy(update={"dependencies": [dep]})
    with pytest.raises(AuditError):
        assemble(case.request, case.authorization, a)


def test_tombstone_residual_hash():
    c = fixtures()[2]
    obs = c.assessment.observations[1]
    altered = obs.model_copy(update={"fields": {**obs.fields, "email_hash": "residual"}})
    a = c.assessment.model_copy(
        update={
            "observations": [c.assessment.observations[0], altered, c.assessment.observations[2]]
        }
    )
    result = assemble(c.request, c.authorization, a)
    assert result.deletion_status == "INCOMPLETE"
    assert [s.operation for s in result.steps] == [
        "REPORT_EXPOSED_PII",
        "REDACT_RECORD",
        "VERIFY_RECORD_ABSENT",
        "VERIFY_RECORD_PRESENT",
        "VERIFY_RECORD_REDACTED",
    ]
    assert all(not s.evidence_id for s in result.steps[1:])


def test_csv_roundtrip_and_failure_preserves_existing(tmp_path):
    path = tmp_path / "output.csv"
    results = [c.expected for c in reversed(fixtures())]
    ids = [c.request.case_id for c in fixtures()]
    write_csv(path, results, ids)
    before = path.read_bytes()
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert [r["case_id"] for r in rows] == ids
    assert json.loads(rows[1]["steps_json"])[0]["evidence_id"] == "custom_e02"
    with pytest.raises(AuditError):
        write_csv(path, results[:-1], ids)
    assert path.read_bytes() == before


def test_evaluator_penalizes_missing_extra_and_misalignment():
    expected = [c.expected for c in fixtures()]
    metrics = score(expected, expected)
    assert metrics["status_accuracy"] == metrics["sequence_accuracy"] == 1.0
    assert metrics["step_matches"] == 9
    assert metrics["fields_correct"] == metrics["fields_total"] == 63
    missing = score(expected[:1], expected)
    assert missing["status_accuracy"] == 1 / 3
    assert missing["fields_correct"] == 0
    assert missing["fields_total"] == 63
    extra = score([*expected, expected[0].model_copy(update={"case_id": "extra"})], expected)
    assert extra["sequence_accuracy"] == 3 / 4


def test_date_precision_is_an_interval_and_conflicts_are_not_arbitrarily_ordered():
    from datetime import datetime

    from ghost_audit.models import SourceRef
    from ghost_audit.workflow import admissible, reduce_copies

    case = fixtures()[2]
    dated = SourceRef(
        evidence_id="e",
        locator="page:1",
        captured_at=datetime.fromisoformat("2026-06-10T11:00:00Z"),
        observed_at=datetime.fromisoformat("2026-06-10T00:00:00Z"),
        time_precision="DATE",
    )
    assert admissible(dated, case.request)
    assert dated.observation_interval()[0] < dated.observed_at
    assert dated.observation_interval()[1] == dated.captured_at
    old = case.assessment.observations[0].model_copy(update={"source": dated})
    exact = dated.model_copy(
        update={
            "time_precision": "EXACT",
            "observed_at": datetime.fromisoformat("2026-06-10T10:00:00Z"),
        }
    )
    conflict = old.model_copy(update={"state": "PRESENT", "source": exact})
    with pytest.raises(AuditError, match="CONFLICTING_READBACKS"):
        reduce_copies([old, conflict])
