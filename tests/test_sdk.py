import asyncio
from types import SimpleNamespace

import pytest
from agents import AgentOutputSchema, Model, ModelResponse
from agents.usage import Usage
from evaluation.custom_cases import fixtures
from ghost_audit.agent import ProposedAssessment, run_task, task_definitions
from ghost_audit.usage import UsageHooks, UsageLedger
from openai.types.responses import ResponseOutputMessage, ResponseOutputText


class OfflineModel(Model):
    def __init__(self, text=None, failure=False):
        self.text, self.failure = text, failure

    async def get_response(self, *args, **kwargs):
        if self.failure:
            raise RuntimeError("offline controlled failure")
        return ModelResponse(
            output=[
                ResponseOutputMessage(
                    id="offline",
                    role="assistant",
                    status="completed",
                    type="message",
                    content=[
                        ResponseOutputText(type="output_text", text=self.text, annotations=[])
                    ],
                )
            ],
            usage=Usage(requests=1, input_tokens=11, output_tokens=7, total_tokens=18),
            response_id="offline",
        )

    async def stream_response(self, *args, **kwargs):
        raise NotImplementedError
        yield


def test_sdk_schemas_no_key_or_network(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    triage, audit = task_definitions("offline-schema-check")
    assert triage.tools == []
    assert [t.name for t in audit.tools] == [
        "search_evidence",
        "read_evidence",
        "lookup_sql_resource",
    ]
    assert triage.handoffs == audit.handoffs == []
    assert triage.model_settings.reasoning.effort == "low"
    assert audit.model_settings.reasoning.effort == "medium"
    assert AgentOutputSchema(audit.output_type).is_strict_json_schema()


def test_sdk_runner_structured_output_and_usage_offline(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    triage, _ = task_definitions("offline-schema-check")
    expected = fixtures()[0].authorization
    triage.model = OfflineModel(expected.model_dump_json())
    ledger = UsageLedger()
    result = asyncio.run(
        run_task(
            triage,
            "offline fixture",
            case_id="custom_a01",
            stage="triage",
            ledger=ledger,
            max_turns=1,
        )
    )
    assert result == expected
    assert ledger.totals() == {
        "requests": 1,
        "known_input_tokens": 11,
        "known_output_tokens": 7,
        "unknown_usage_requests": 0,
    }


def test_sdk_failure_retains_unknown_usage():
    triage, _ = task_definitions("offline-schema-check")
    triage.model = OfflineModel(failure=True)
    ledger = UsageLedger()
    with pytest.raises(RuntimeError, match="controlled failure"):
        asyncio.run(run_task(triage, "offline", case_id="c", stage="triage", ledger=ledger))
    assert ledger.totals()["unknown_usage_requests"] == 1
    assert ledger.entries[0].input_tokens is None


def test_completed_usage_survives_later_failure_without_double_counting():
    ledger = UsageLedger()
    hooks = UsageHooks(ledger, "offline", "c", "audit")
    asyncio.run(hooks.on_llm_start(None, None, None, []))
    asyncio.run(
        hooks.on_llm_end(
            None, None, SimpleNamespace(usage=Usage(requests=1, input_tokens=2, output_tokens=3))
        )
    )
    asyncio.run(hooks.on_llm_start(None, None, None, []))
    hooks.record_failure()
    hooks.record_failure()
    assert ledger.totals() == {
        "requests": 2,
        "known_input_tokens": 2,
        "known_output_tokens": 3,
        "unknown_usage_requests": 1,
    }


def test_audit_schema_roundtrip_and_duplicate_fields():
    raw = fixtures()[2].assessment.model_dump()
    for o in raw["observations"]:
        o["fields"] = [{"name": k, "value": v} for k, v in o["fields"].items()]
    proposal = ProposedAssessment.model_validate(raw)
    assert proposal.to_domain() == fixtures()[2].assessment
    fields = raw["observations"][1]["fields"]
    fields.append(fields[0])
    with pytest.raises(ValueError, match="DUPLICATE_OBSERVATION_FIELD"):
        ProposedAssessment.model_validate(raw).to_domain()


@pytest.mark.parametrize("stage", ["triage", "triage_batch", "audit", "audit_repair", "vision"])
@pytest.mark.parametrize("failure", [False, True])
def test_live_stages_enable_console_storage_and_sdk_tracing(tmp_path, monkeypatch, stage, failure):
    from decimal import Decimal

    import ghost_audit.agent as adapter
    from agents import ModelSettings
    from ghost_audit.budget import Budget

    events = []
    monkeypatch.setenv("OPENAI_API_KEY", "offline-placeholder")

    async def close():
        events.append("client_closed")

    monkeypatch.setattr(adapter, "AsyncOpenAI", lambda **kwargs: SimpleNamespace(close=close))
    monkeypatch.setattr(adapter, "set_tracing_disabled", lambda disabled: events.append(disabled))
    monkeypatch.setattr(
        adapter,
        "set_tracing_export_api_key",
        lambda key: events.append("export_key_set" if key == "offline-placeholder" else "bad_key"),
    )
    monkeypatch.setattr(adapter, "flush_traces", lambda: events.append("flushed"))
    expected = fixtures()[0].authorization

    async def mocked_run(agent, prompt, **kwargs):
        assert agent.model_settings.store is True
        assert agent.model_settings.metadata == {
            "workflow": "ghost_data",
            "case_id": "c",
            "stage": stage,
        }
        config = kwargs["run_config"]
        assert config.tracing_disabled is False
        assert config.trace_include_sensitive_data is True
        assert config.workflow_name == "ghost_data." + stage
        assert config.group_id == "c"
        assert config.trace_metadata == {"case_id": "c", "stage": stage}
        if failure:
            raise RuntimeError("controlled error")
        return SimpleNamespace(final_output=expected)

    monkeypatch.setattr(adapter.Runner, "run", mocked_run)
    triage, _ = task_definitions("gpt-6.1-sol")
    # Even a caller opting out locally cannot silently disable the requested logging.
    triage = triage.clone(model_settings=ModelSettings(store=False))
    call = run_task(
        triage,
        "offline fixture",
        case_id="c",
        stage=stage,
        ledger=UsageLedger(),
        budget=Budget(tmp_path / "budget.jsonl", Decimal(1)),
    )
    if failure:
        with pytest.raises(RuntimeError, match="controlled error"):
            asyncio.run(call)
    else:
        assert asyncio.run(call) == expected
    assert events == [False, "export_key_set", "client_closed", "flushed"]
