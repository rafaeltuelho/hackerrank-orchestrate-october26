"""Offline-compatible task declarations for bounded sequential SDK runs."""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime

from agents import (
    Agent,
    AgentOutputSchema,
    ModelRetrySettings,
    ModelSettings,
    OpenAIProvider,
    RunConfig,
    RunContextWrapper,
    Runner,
    flush_traces,
    function_tool,
    set_tracing_disabled,
    set_tracing_export_api_key,
)
from agents.models.openai_responses import OpenAIResponsesModel
from openai import AsyncOpenAI
from openai.types.shared import Reasoning

from .budget import Budget, BudgetedModel
from .config import AUDIT_REASONING_EFFORT, TRIAGE_REASONING_EFFORT
from .evidence import EvidenceStore, search_payload
from .models import Assessment, AuditError, Authorization, Contract, Nonempty, Observation
from .prompts import AUDIT, TRIAGE
from .usage import UsageHooks, UsageLedger


@dataclass
class AuditContext:
    evidence: EvidenceStore
    cutoff: datetime
    accessed: dict | None = None
    allowed_identifiers: set[str] | None = None


@function_tool
def search_evidence(
    ctx: RunContextWrapper[AuditContext], identifiers: list[str], offset: int = 0
) -> str:
    """Search literal identifiers; paginate until next_offset is null. Errors/visual gaps remain."""
    if (
        ctx.context.allowed_identifiers is not None
        and not set(identifiers) <= ctx.context.allowed_identifiers
    ):
        raise ValueError(
            "Search only grounded identity aliases, resource IDs or trace IDs. "
            "Service/table/category names are not identifiers; use read_evidence."
        )
    result = ctx.context.evidence.search(identifiers, ctx.context.cutoff, offset)
    from dataclasses import replace

    from .grounding import literal_fields

    result.fragments = [
        replace(f, extracted_fields=literal_fields(f) or None) for f in result.fragments
    ]
    if ctx.context.accessed is not None:
        for fragment in result.fragments:
            ctx.context.accessed[(fragment.evidence_id, fragment.locator)] = fragment
            if ctx.context.allowed_identifiers is not None:
                ctx.context.allowed_identifiers.update(
                    v
                    for k, v in literal_fields(fragment).items()
                    if k in {"resource_id", "parent_resource_id", "trace_id"} and v
                )
    return search_payload(result)


@function_tool
def read_evidence(ctx: RunContextWrapper[AuditContext], file_id: str, offset: int = 0) -> str:
    """Read an admissible artifact in pages of 40 fragments, preserving exact source locators."""
    import json
    from dataclasses import asdict

    from .grounding import literal_fields

    if offset < 0:
        raise ValueError("negative offset")
    fragments = ctx.context.evidence.read(file_id, ctx.context.cutoff)
    page = fragments[offset : offset + 40]
    if ctx.context.accessed is not None:
        for f in page:
            ctx.context.accessed[(f.evidence_id, f.locator)] = f
            if ctx.context.allowed_identifiers is not None:
                ctx.context.allowed_identifiers.update(
                    v
                    for k, v in literal_fields(f).items()
                    if k in {"resource_id", "parent_resource_id", "trace_id"} and v
                )
    return json.dumps(
        {
            "fragments": [{**asdict(f), "extracted_fields": literal_fields(f)} for f in page],
            "next_offset": offset + 40 if offset + 40 < len(fragments) else None,
            "total": len(fragments),
        },
        default=str,
        ensure_ascii=False,
    )


@function_tool
def lookup_sql_resource(
    ctx: RunContextWrapper[AuditContext], file_id: str, table: str, resource_id: str
) -> str:
    """Look up a known resource in a complete SQL table of a previously read schema.

    Requires a read SQL row with the same resource ID, table, columns and explicit
    origin_system. Returns exact rows or a bounded zero-row receipt.
    """
    import json
    from dataclasses import asdict

    if (
        ctx.context.allowed_identifiers is None
        or resource_id not in ctx.context.allowed_identifiers
    ):
        raise ValueError("SQL lookup requires a grounded resource ID")
    fragments = ctx.context.evidence.lookup_sql(
        file_id,
        table,
        resource_id,
        ctx.context.cutoff,
        list((ctx.context.accessed or {}).values()),
    )
    if ctx.context.accessed is not None:
        for fragment in fragments:
            ctx.context.accessed[(fragment.evidence_id, fragment.locator)] = fragment
    return json.dumps([asdict(f) for f in fragments], default=str, ensure_ascii=False)


class FieldValue(Contract):
    name: Nonempty
    value: str | None


class ProposedObservation(Observation):
    # OpenAI strict schemas cannot express an arbitrary-key dict. A list of exact
    # field/value pairs converts into the domain map only after duplicate checking.
    fields: list[FieldValue]


class ProposedAssessment(Assessment):
    observations: list[ProposedObservation]

    def to_domain(self) -> Assessment:
        raw = self.model_dump()
        for obs in raw["observations"]:
            values = obs["fields"]
            if len({v["name"] for v in values}) != len(values):
                raise AuditError("DUPLICATE_OBSERVATION_FIELD")
            obs["fields"] = {v["name"]: v["value"] for v in values}
        return Assessment.model_validate(raw)


class PolicySupport(Contract):
    system_id: Nonempty
    resource_id: Nonempty
    rule_id: Nonempty
    evidence_id: Nonempty
    locator: Nonempty
    quote: Nonempty


class AuditProposal(Contract):
    assessment: ProposedAssessment
    policy_support: list[PolicySupport]


def task_definitions(model: str, tools: list | None = None) -> tuple[Agent, Agent]:
    if not model.strip():
        raise ValueError("OPENAI_MODEL is required for task setup")
    settings = ModelSettings(
        store=True,
        parallel_tool_calls=False,
        max_tokens=6000,
        timeout=90,
        retry=ModelRetrySettings(max_retries=0),
        extra_body={"service_tier": "default"},
    )
    triage = Agent(
        name="request_triage",
        model=model,
        instructions=TRIAGE,
        output_type=Authorization,
        model_settings=settings.resolve(
            ModelSettings(reasoning=Reasoning(effort=TRIAGE_REASONING_EFFORT), max_tokens=1000)
        ),
    )
    audit = Agent(
        name="deletion_audit",
        model=model,
        instructions=AUDIT,
        output_type=AuditProposal,
        model_settings=settings.resolve(
            ModelSettings(reasoning=Reasoning(effort=AUDIT_REASONING_EFFORT), max_tokens=12000)
        ),
        tools=[search_evidence, read_evidence, lookup_sql_resource] if tools is None else tools,
    )
    # Fail at setup, rather than the first paid request, if a schema is incompatible.
    AgentOutputSchema(Authorization)
    AgentOutputSchema(AuditProposal)
    return triage, audit


async def run_task(
    agent: Agent,
    prompt: str,
    *,
    case_id: str,
    stage: str,
    ledger: UsageLedger,
    context: AuditContext | None = None,
    max_turns: int = 6,
    budget: Budget | None = None,
):
    """Bounded SDK execution; returned audit assessments still require semantic validation.

    No handoffs, sessions or application-level retries. Live calls enable hosted
    traces and Responses storage; fake-model tests never export traces. Caller owns
    spending limits and API configuration; this adapter never chooses a model.
    """
    hooks = UsageHooks(ledger, str(agent.model), case_id, stage)
    client = None
    live = isinstance(agent.model, str)
    if live:
        if budget is None:
            raise ValueError("Live requests require a persistent shared budget")
        if agent.model != "gpt-6.1-sol":
            raise ValueError("Live pricing has only been verified for gpt-6.1-sol")
        client = AsyncOpenAI(max_retries=0, timeout=90, base_url="https://api.openai.com/v1")
        set_tracing_disabled(False)
        set_tracing_export_api_key(os.environ["OPENAI_API_KEY"])
        agent = agent.clone(
            model=BudgetedModel(OpenAIResponsesModel(agent.model, client), budget),
            model_settings=agent.model_settings.resolve(
                ModelSettings(
                    store=True,
                    metadata={"workflow": "ghost_data", "case_id": case_id, "stage": stage},
                )
            ),
        )
    try:
        result = await Runner.run(
            agent,
            prompt,
            context=context,
            max_turns=max_turns,
            hooks=hooks,
            run_config=RunConfig(
                tracing_disabled=not live,
                trace_include_sensitive_data=True,
                workflow_name=f"ghost_data.{stage}",
                group_id=case_id,
                trace_metadata={"case_id": case_id, "stage": stage},
                model_provider=OpenAIProvider(use_responses=True, strict_feature_validation=True),
            ),
        )
        return result.final_output
    finally:
        hooks.record_failure()
        if client:
            await client.close()
            try:
                await asyncio.to_thread(flush_traces)
            except Exception as exc:
                logging.getLogger(__name__).warning("Trace export failed (%s)", type(exc).__name__)
