from datetime import datetime

import pytest
from evaluation.custom_cases import fixtures
from ghost_audit.data import Alias, Identity
from ghost_audit.evidence import Fragment
from ghost_audit.models import AuditError
from ghost_audit.policy import validate_obligation
from ghost_audit.readbacks import normalize_readbacks

WHEN = datetime.fromisoformat("2026-06-10T11:00:00Z")


def fragment(line, n=1, source="e"):
    return Fragment(source, f"line:{n}", WHEN, WHEN, line)


def identity():
    return Identity(
        subject_id="u",
        aliases=[
            Alias(kind="email", value="u@example.invalid", evidence_id="a", available_at=WHEN)
        ],
    )


def test_trace_join_and_no_adjacency_guess():
    lines = [
        fragment(
            "service=account_service trace_id=t event=profile_lookup_started "
            "lookup_key=u@example.invalid"
        ),
        fragment(
            "service=account_service trace_id=t event=profile_lookup_completed "
            "resource_id=r rows=0 http_status=404",
            2,
        ),
        fragment(
            "service=account_service trace_id=other event=profile_lookup_completed "
            "resource_id=unlinked rows=0 http_status=404",
            3,
        ),
    ]
    observations, links = normalize_readbacks(lines, identity())
    assert {o.resource_id for o in observations} == {"r", "unlinked"}
    assert {link.resource_id for link in links} == {"r"}
    assert observations[0].state == "ABSENT" and observations[0].scope_complete


def test_cross_source_trace_collision_not_ownership():
    _, links = normalize_readbacks(
        [
            fragment(
                "service=account_service trace_id=t event=profile_lookup_started "
                "lookup_key=u@example.invalid",
                source="elsewhere",
            ),
            fragment(
                "service=account_service trace_id=t event=profile_lookup_completed "
                "resource_id=r rows=0 http_status=404",
                2,
            ),
        ],
        identity(),
    )
    assert links == []


@pytest.mark.parametrize(
    "line",
    [
        "service=account_service resource_id=r event=DELETE_RECORD reported_result=SUCCESS",
        "service=account_service resource_id=r event=profile_lookup_completed "
        "rows=0 http_status=500",
        "service=search_service resource_id=r event=index_query_completed result=error",
        "service=account_service resource_id=r resource_id=other event=profile_lookup_completed "
        "rows=0 http_status=404",
    ],
)
def test_claim_and_failed_query_are_not_absence(line):
    assert normalize_readbacks([fragment(line)], identity()) == ([], [])


def test_policy_exact_category_action_and_condition():
    ob = fixtures()[2].assessment.obligations[2]
    rules = [
        {
            "rule_id": "rule_12",
            "data_category": "SECURITY_AUDIT_LOG",
            "condition": "Record is within the supplied retention period",
            "required_action": "RETAIN",
        }
    ]
    with pytest.raises(AuditError, match="UNRESOLVED_POLICY_CONDITION"):
        validate_obligation(ob, rules, set())
    validate_obligation(ob, rules, {"rule_12"})
    with pytest.raises(AuditError, match="POLICY_RULE_MISMATCH"):
        validate_obligation(ob.model_copy(update={"action": "DELETE"}), rules, {"rule_12"})


def test_pipe_handover_is_scoped_and_typed():
    from ghost_audit.evidence import pipe_values

    line = (
        "- 2026-06-10T11:00:00Z | account_service | r | USER_PROFILE | NOT_FOUND | "
        "u@example.invalid"
    )
    f = Fragment("e", "line:1", WHEN, WHEN, line, pipe_values(line))
    observations, links = normalize_readbacks([f], identity())
    assert observations[0].state == "ABSENT" and observations[0].scope_complete
    assert observations[0].proof_kind == "ARTIFACT"
    assert links[0].resource_id == "r" and links[0].identifier_type == "email"
