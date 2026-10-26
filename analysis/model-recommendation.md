# OpenAI model recommendation for the deletion-audit workflow

Recommendation recorded on 2026-10-25 for the implementation agent. This is a configuration recommendation based on current official documentation and the reviewed workflow, not a measured benchmark or confirmation of account access.

Read alongside the [workflow specification](workflow-design.md), [technical decisions](technical-decisions.md), [acceptance cases](workflow-acceptance-cases.md), and [implementation handoff](implementation-handoff.md). Preserve their challenge-only scope, Python 3.14.5 runtime, OpenAI provider, and sequential triage/audit execution through the OpenAI Agents SDK.

## Initial baseline

Use **gpt-6.1-sol** for all model-dependent stages initially, varying reasoning effort by task. This provides a consistent baseline before introducing model-specific cost optimizations.

| Task | Model | Reasoning effort | Purpose |
|---|---|---|---|
| Deletion-intent triage | gpt-6.1-sol | low | Interpret multilingual requests, negation, and requests to verify or finish a prior deletion |
| Unstructured evidence interpretation | gpt-6.1-sol | medium | Extract grounded observations and interpret business-record categories and conditions |
| Screenshot/complex PDF-page interpretation | gpt-6.1-sol | medium | Read image input with source/page/region provenance |
| Evidence reconciliation and audit assessment | gpt-6.1-sol | medium | Interpret conflicts, policy conditions, remaining records, recreation risks, and proposed remediation |

These are logical tasks, not a requirement for four agents or four calls per case. Combine interpretation with the existing audit run where practical. Use separate visual calls only where needed, and include them in usage reporting.

Suggested application configuration (illustrative names, not SDK arguments):

```toml
[models.triage]
name = "gpt-6.1-sol"
reasoning_effort = "low"

[models.audit]
name = "gpt-6.1-sol"
reasoning_effort = "medium"

[models.vision]
name = "gpt-6.1-sol"
reasoning_effort = "medium"
```

Map these settings to the installed Agents SDK's supported configuration. Use the **Responses API for tool calling**. Sol supports text/image input, structured outputs, and function calling, and supports low/medium/high/xhigh/max reasoning; none and minimal are unsupported. Verify the installed SDK signatures and actual model access before live execution. [GPT-6.1 Sol documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol)

## Cost optimization after baseline evaluation

Evaluate **gpt-6-luna with low reasoning** for intent triage. Luna is positioned for focused, high-volume work and supports structured outputs and image input. It is a candidate, not an already validated replacement. [GPT-6 Luna documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)

The 32 public samples contain no NOT_APPLICABLE examples. Therefore, triage evaluation must also include participant-authored cases for:

- Access, export, correction, and marketing-only requests.
- Explicit negation, including multilingual variants.
- Hypothetical or conditional deletion language.
- Requests to verify or finish a previously authorized deletion.
- Ambiguous wording that must not silently become NOT_APPLICABLE.

Compare Luna with the Sol baseline using identical inputs and expected decisions. Inspect false NOT_APPLICABLE decisions particularly carefully: they suppress the entire audit. Adopt Luna only if the evaluation supports the change, and document the measured tradeoff in the evaluation report.

The resulting candidate configuration is:

```text
Triage:          gpt-6-luna  / low
Evidence/audit:  gpt-6.1-sol / medium
Visual reading: gpt-6.1-sol / medium
```

This changes configuration within the existing workflow; it does not add a router, handoffs, worker agents, or a new orchestration layer.

## Difficult-case comparison

During evaluation, compare **Sol at high reasoning** with **gpt-6-astra at medium reasoning** on difficult cases where the necessary evidence exists but interpretation or reasoning remains unreliable. Keep inputs and expected outcomes fixed. Compare supported findings, policy correctness, step/field/sequence accuracy, latency, and actual usage/cost.

Astra is documented as the most capable model for demanding work, but no benchmark yet shows that using it throughout this submission is worth the additional cost. Do not implement automatic escalation as part of the baseline. [GPT-6 Astra documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)

A stronger model cannot supply missing evidence, create a subject-resource link, or make post-cutoff evidence admissible. Distinguish reasoning failures from the source-evidence gaps identified in the [public sample audit](public-samples/report.md).

## Tasks that remain deterministic

Use Python for exact identifier matching, history joins, timestamp filtering, public source-ID validation, rule lookup, operation/state validation, dependency checks, canonical ordering, step numbering, JSON/CSV serialization, and evaluation scoring.

Models interpret ambiguous language and business evidence and propose assessments. Python enforces the contract. Passing a structured-output schema does not prove evidence sufficiency or correct policy interpretation.

## Pricing reference and usage accounting

Official Standard API rates checked on 2026-10-25, in USD per million tokens for requests with at most 272K input tokens:

| Model | Input | Output |
|---|---:|---:|
| gpt-6-luna | $0.10 | $0.50 |
| gpt-6.1-sol | $2.00 | $10.00 |
| gpt-6-astra | $10.00 | $50.00 |

These rates are a dated reference, not a cost guarantee or complete billing formula. Cache reads/writes, long-context requests, service tiers, and regional processing can have different rates. Recheck the applicable prices before the final run and record the assumptions. [OpenAI pricing](https://developers.openai.com/api/docs/pricing)

Measure every model call in triage, audit, visual interpretation, and retries where usage is reported. Count tool-loop continuations; do not count local tool invocations as separate model calls or double-count SDK aggregate and per-call usage. Include shared extraction/cache attribution where applicable. Unknown usage remains unavailable, not zero.

The final code/evaluation/usage_report.md must describe the full-dataset run that actually produced output.csv, including per-model and overall calls/tokens/cost and averages per request. No actual run cost or model accuracy has been measured during this recommendation.

## Implementation handoff instruction

> Start with gpt-6.1-sol: low reasoning for triage and medium for evidence/audit and visual interpretation. Establish the baseline on the public samples and custom cases. Evaluate gpt-6-luna for triage as a subsequent cost optimization. Do not add automatic model escalation. Keep deterministic evidence/policy/output checks outside the model and preserve the original challenge scope.

OpenAI project access, credentials and spending limits still require configuration before live execution. Read OPENAI_API_KEY from the environment without displaying it. This recommendation does not authorize an unlimited paid run or guarantee that the named models are enabled for the participant's account.

Official selection guidance recommends comparing models on the same workload and retaining the lightest setting that meets the quality requirement. The task-to-model mapping above is our workflow-specific judgment and must be validated by those experiments. [OpenAI model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection)
