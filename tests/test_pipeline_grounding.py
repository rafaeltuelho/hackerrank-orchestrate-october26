import asyncio
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from evaluation.custom_cases import fixtures
from ghost_audit.agent import AuditProposal
from ghost_audit.budget import Budget
from ghost_audit.data import Alias, Identity
from ghost_audit.evidence import EvidenceStore
from ghost_audit.grounding import validate_proposal
from ghost_audit.models import AuditError
from ghost_audit.pipeline import audit_request
from ghost_audit.usage import UsageLedger


def prepared(tmp_path):
    case = fixtures()[1]
    captured = datetime.fromisoformat("2026-06-10T11:50:00Z")
    observed = datetime.fromisoformat("2026-06-10T11:45:00Z")
    lines = [
        "2026-06-10T11:45:00Z service=search_service resource_id=search_custom02 "
        "event=index_query_completed result=hit email=sample02@example.invalid",
        "2026-06-10T11:45:00Z service=integration_service resource_id=flow_custom02 "
        "event=connector_config_read_completed enabled=true customer_reference=custom_user_02",
    ]
    (tmp_path / "evidence").mkdir()
    (tmp_path / "evidence/readbacks.log").write_text("\n".join(lines))
    identity = Identity(
        subject_id="custom_user_02",
        aliases=[
            Alias(
                kind="email",
                value="sample02@example.invalid",
                evidence_id="a",
                available_at=observed,
            ),
            Alias(kind="user_id", value="custom_user_02", evidence_id="a", available_at=observed),
        ],
    )
    data = SimpleNamespace(
        root=tmp_path,
        files={
            "custom_e02": {
                "file_path": "evidence/readbacks.log",
                "captured_at": captured.isoformat(),
            }
        },
        activity=[],
        rules=[
            {
                "rule_id": "rule_03",
                "data_category": "SEARCH_INDEX_ENTRY",
                "condition": "Always",
                "required_action": "DELETE",
            }
        ],
        resolve_identity=lambda *args: identity,
    )
    store = EvidenceStore(data)
    sources = {
        (f.evidence_id, f.locator): f for f in store.read("custom_e02", case.request.audit_at)
    }
    raw = case.assessment.model_dump()
    for i, (obs, link) in enumerate(zip(raw["observations"], raw["links"], strict=True), 1):
        source = {
            "evidence_id": "custom_e02",
            "locator": f"line:{i}",
            "captured_at": captured,
            "observed_at": observed,
        }
        obs["source"] = link["source"] = source
        obs["copy_id"] = "unspecified"
        if i == 1:
            obs["fields"] = [{"name": "email", "value": "sample02@example.invalid"}]
            link["identifier_type"] = "email"
            link["identifier_value"] = "sample02@example.invalid"
        else:
            obs["fields"] = [
                {"name": "enabled", "value": "true"},
                {"name": "customer_reference", "value": "custom_user_02"},
            ]
    proposal = AuditProposal.model_validate(
        {
            "assessment": raw,
            "policy_support": [
                {
                    "system_id": "search_service",
                    "resource_id": "search_custom02",
                    "rule_id": "rule_03",
                    "evidence_id": "custom_e02",
                    "locator": "line:1",
                    "quote": "event=index_query_completed",
                },
                {
                    "system_id": "integration_service",
                    "resource_id": "flow_custom02",
                    "rule_id": "active_flow",
                    "evidence_id": "custom_e02",
                    "locator": "line:2",
                    "quote": "enabled=true",
                },
            ],
        }
    )
    return case, data, store, identity, sources, proposal


def test_connected_pipeline_with_authored_evidence(tmp_path, monkeypatch):
    case, data, store, identity, sources, proposal = prepared(tmp_path)

    async def frozen_task(agent, prompt, **kwargs):
        return case.authorization if kwargs["stage"] == "triage" else proposal

    monkeypatch.setattr("ghost_audit.pipeline.run_task", frozen_task)
    actual = asyncio.run(
        audit_request(
            case.request,
            data,
            store,
            "offline",
            Budget(tmp_path / "budget.jsonl", Decimal(1)),
            UsageLedger(),
            tmp_path / "run",
        )
    )
    assert actual == case.expected


@pytest.mark.parametrize("failure", ["field", "alias", "citation", "time", "policy", "absence"])
def test_proposal_grounding_rejects_unsupported_claims(tmp_path, failure):
    case, data, store, identity, sources, proposal = prepared(tmp_path)
    raw = proposal.model_dump()
    if failure == "field":
        raw["assessment"]["observations"][0]["fields"][0]["value"] = "someone-else@example.invalid"
    elif failure == "alias":
        raw["assessment"]["links"][0]["identifier_value"] = "someone-else@example.invalid"
    elif failure == "citation":
        raw["assessment"]["observations"][0]["source"]["locator"] = "line:999"
    elif failure == "time":
        raw["assessment"]["observations"][0]["source"]["observed_at"] = case.request.audit_at
    elif failure == "policy":
        raw["policy_support"][0]["quote"] = "invented category"
    else:
        raw["assessment"]["observations"][0]["state"] = "ABSENT"
    with pytest.raises(AuditError):
        validate_proposal(AuditProposal.model_validate(raw), case.request, identity, data, sources)


def test_grounding_rejects_analytics_stable_reference(tmp_path):
    case, data, store, identity, sources, proposal = prepared(tmp_path)
    raw = proposal.model_dump()
    raw["assessment"]["observations"][1]["state"] = "ANONYMIZED"
    with pytest.raises(AuditError, match="READBACK_STATE_MISMATCH|STABLE_REFERENCE"):
        validate_proposal(AuditProposal.model_validate(raw), case.request, identity, data, sources)


def test_omitted_known_subject_resource_cannot_pass_coverage(tmp_path):
    case, data, store, identity, sources, proposal = prepared(tmp_path)
    raw = proposal.model_dump()
    raw["assessment"]["observations"] = raw["assessment"]["observations"][:1]
    raw["assessment"]["obligations"] = raw["assessment"]["obligations"][:1]
    raw["assessment"]["links"] = raw["assessment"]["links"][:1]
    raw["policy_support"] = raw["policy_support"][:1]
    with pytest.raises(AuditError, match="UNASSESSED_GROUNDED_RESOURCE"):
        validate_proposal(AuditProposal.model_validate(raw), case.request, identity, data, sources)


def test_read_tool_exposes_parsed_fields_without_optional_tracking(tmp_path):
    import json

    from agents.tool_context import ToolContext
    from ghost_audit.agent import AuditContext, read_evidence

    case, data, store, identity, sources, proposal = prepared(tmp_path)
    context = ToolContext(
        AuditContext(store, case.request.audit_at),
        tool_name="read_evidence",
        tool_call_id="offline",
        tool_arguments='{"file_id":"custom_e02"}',
    )
    result = asyncio.run(read_evidence.on_invoke_tool(context, '{"file_id":"custom_e02"}'))
    fields = json.loads(result)["fragments"][0]["extracted_fields"]
    assert fields["resource_id"] == "search_custom02"
    assert fields["email"] == "sample02@example.invalid"


def test_date_precision_requires_observation_date_not_expiry(tmp_path):
    from ghost_audit.evidence import Fragment
    from ghost_audit.grounding import source_fragment
    from ghost_audit.models import SourceRef

    case = fixtures()[2]
    captured = datetime.fromisoformat("2026-06-10T11:00:00Z")
    source = SourceRef(
        evidence_id="e",
        locator="page:1",
        captured_at=captured,
        observed_at=datetime.fromisoformat("2026-06-09T00:00:00Z"),
        time_precision="DATE",
    )
    good = Fragment("e", "page:1", captured, None, "Created: 09 Jun 2026")
    assert source_fragment(source, {("e", "page:1"): good}, case.request) == good
    expiry = Fragment("e", "page:1", captured, None, "Expiry date: 09 Jun 2026")
    with pytest.raises(AuditError, match="UNSUPPORTED_OBSERVATION_DATE"):
        source_fragment(source, {("e", "page:1"): expiry}, case.request)


def test_candidate_keeps_supported_plan_but_does_not_certify_coverage_gap(tmp_path):
    from ghost_audit.candidate import candidate_from_proposal

    case, data, store, identity, sources, proposal = prepared(tmp_path)
    a = proposal.assessment.model_copy(
        update={"coverage_complete": False, "gaps": ["Retention condition unknown"]}
    )
    proposal = proposal.model_copy(update={"assessment": a})
    result, diagnostic = candidate_from_proposal(
        proposal, case.request, case.authorization, identity, data, sources
    )
    assert result == case.expected
    assert not diagnostic["evidence_validated"]
    assert "Retention condition unknown" in diagnostic["diagnostics"]


def test_candidate_unknown_condition_never_creates_delete_action(tmp_path):
    from ghost_audit.candidate import candidate_from_proposal

    case, data, store, identity, sources, proposal = prepared(tmp_path)
    data.rules[0]["condition"] = "Unestablished exclusive ownership"
    result, diagnostic = candidate_from_proposal(
        proposal, case.request, case.authorization, identity, data, sources
    )
    assert not diagnostic["evidence_validated"]
    assert not any(s.resource_id == "search_custom02" for s in result.steps)
    assert any(s.operation == "DISABLE_DATA_FLOW" for s in result.steps)


def test_candidate_fallback_is_structural_only(tmp_path):
    from ghost_audit.candidate import unsupported_candidate
    from ghost_audit.output import validate_result, write_csv

    result, diagnostic = unsupported_candidate("unresolved", "UNKNOWN_POLICY_CONDITION")
    validate_result(result, semantic=False)
    with pytest.raises(AuditError, match="EMPTY_AUTHORIZED_RESULT"):
        validate_result(result)
    assert result.steps == [] and not diagnostic["evidence_validated"]
    write_csv(tmp_path / "candidate.csv", [result], ["unresolved"], semantic=False)


def test_literal_readback_candidate_is_grounded_but_uncertified(tmp_path):
    from ghost_audit.candidate import candidate_from_proposal
    from ghost_audit.readback_candidate import propose_readbacks

    case, data, store, identity, sources, _ = prepared(tmp_path)
    proposal = propose_readbacks(identity, sources, data.rules)
    result, diagnostic = candidate_from_proposal(
        proposal, case.request, case.authorization, identity, data, sources
    )
    assert result == case.expected
    assert not diagnostic["evidence_validated"]


def test_batch_triage_cannot_cross_request_spans_or_omit_ids():
    from ghost_audit.triage_batch import Batch, Item, validate_batch

    a, b, _ = fixtures()
    good = Batch(
        items=[Item(case_id=c.request.case_id, authorization=c.authorization) for c in (a, b)]
    )
    validate_batch(good, [a.request, b.request])
    with pytest.raises(ValueError, match="CASE_SET"):
        validate_batch(Batch(items=good.items[:1]), [a.request, b.request])
    wrong = Item(case_id=a.request.case_id, authorization=b.authorization)
    with pytest.raises(ValueError, match="INTENT_SPAN"):
        validate_batch(Batch(items=[wrong, good.items[1]]), [a.request, b.request])


def test_discovery_caps_broad_expansion_and_records_gap():
    from ghost_audit.data import Alias, Identity
    from ghost_audit.evidence import Fragment, SearchResult
    from ghost_audit.pipeline import discover

    case = fixtures()[1]
    when = case.request.requested_at
    identity = Identity(
        subject_id="subject",
        aliases=[Alias(kind="user_id", value="subject", evidence_id="source", available_at=when)],
    )
    calls = []

    def search(identifiers, cutoff, offset, limit):
        calls.append(identifiers)
        fragments = [
            Fragment("source", f"row:{i}", when, when, '{"resource_id":"resource_' + str(i) + '"}')
            for i in range(257)
        ]
        return SearchResult("OK", fragments, [], [], None, len(fragments))

    _, errors, _ = discover(SimpleNamespace(search=search), identity, case.request)
    assert len(calls) == 1
    assert errors == ["DISCOVERY_IDENTIFIER_LIMIT"]
