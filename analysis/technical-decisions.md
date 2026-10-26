# Technical implementation decisions

Updated 2026-10-25 after the user's scope and stack review. This revision supersedes the earlier Python 3.12, multi-provider, two-database and generic checkpoint/resume proposals. The governing goal is the [challenge-aligned workflow](workflow-design.md), not reusable platform infrastructure. No solver code has been implemented by this documentation change.

## 1. Confirmed stack

| Concern | Decision | Scope |
|---|---|---|
| Runtime | Existing system Python 3.14.5 | uv creates the project environment from this interpreter; do not download/downgrade to 3.12 |
| Dependencies | pyproject.toml, uv.lock, .python-version set to 3.14.5 | Resolve, lock and smoke-test on this exact runtime |
| Model provider | OpenAI | OPENAI_API_KEY from environment; model ID configurable; no provider router |
| Agent execution | OpenAI Agents SDK (openai-agents) | Bounded triage and evidence-tool runs, typed outputs and usage |
| Data contracts | Pydantic v2 | Request/context, observations, assessment and exact output schema |
| CLI | argparse and code/main.py | Run the dataset audit; sample input/output overrides for evaluation |
| Structured data | csv/json/pathlib/datetime/sqlite3 standard libraries | Parse supplied records; execute SQL snapshots in isolated temporary SQLite when appropriate |
| Search/state | In-memory exact indexes and typed case context initially | Optional derived SQLite index only if corpus handling warrants it; no fixed database platform |
| PDF/images | pypdf text; pypdfium2/Pillow rendering when needed; OpenAI vision | Interpret supplied artifacts with source/page/region provenance |
| Evaluation/tests | code/evaluation/main.py, pytest, Ruff | Required metrics, at least three custom cases and focused correctness tests |
| Run artifacts | Simple local result/usage files and optional extraction cache | Support the final 518-case run and reports; no generic resume command or schema migrations |

The host interpreter was verified as Python 3.14.5. Library compatibility is not yet tested: resolve and smoke-test the chosen versions on that interpreter during setup. If a dependency fails, investigate its compatible release or a smaller adapter alternative; do not silently change Python. No API calls, credentials, package installs or dependency changes are needed for this design revision.

## 2. Why use the Agents SDK here

An authorized audit may need several evidence lookups before producing a structured assessment. The SDK can run that tool loop, validate the declared output shape, limit turns, and expose model usage. That removes custom model/tool dispatch code while leaving challenge-specific correctness in ordinary Python.

Use only the following SDK mechanisms:

- Agent instructions and a Pydantic output_type for triage and audit results.
- function_tool wrappers around narrow read-only data/evidence functions.
- Runner.run with explicit model configuration and max_turns.
- Per-run context carrying the case cutoff and permitted dataset/tool state.
- Usage returned by the SDK, including requests/input_tokens/output_tokens and available per-request details.

Triage and audit are two sequential task configurations controlled by Python, not autonomous collaborators. Triage gets no evidence tools; non-deletion requests return immediately. The authorized audit gets grounded identity context and evidence tools; Python checks its assessment and assembles/validates the final steps. Do not use handoffs, subagents, hosted search, generic shell tools, a separate summarizer, persistent chat sessions across subjects, or SDK features unrelated to the challenge.

An SDK context object is local application state, not automatically model evidence. Explicitly pass only relevant facts/instructions and return admissible fragments through tools. No sample-answer data enters either run. Disable remote SDK tracing by default and retain the required local usage/diagnostics; a tracing dashboard is not needed to meet the evaluation contract. Usage recording must still cover exceptions and any separate visual-extraction calls.

The official [OpenAI SDK-backed analyst example](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop#step-2-define-the-agents-sdk-backed-analyst) demonstrates an evidence-based runner with tool policy and validation. The design uses only the relevant runner/tool/output capabilities; it does not adopt that example's sandbox, optimization loop or artifact suite. Current SDK structured-output and usage behavior was also checked through the official SDK documentation exposed by Context7; verify exact signatures against the installed version at implementation.

## 3. Expected source and delivery structure

```text
README.md
pyproject.toml
uv.lock
.python-version                  # 3.14.5
code/
  main.py                        # required runnable entry point
  ghost_audit/
    models.py                    # typed case/evidence/output records
    data.py                      # participant loaders and identity/history index
    evidence.py                  # lookup, artifact extraction and provenance
    agent.py                     # OpenAI SDK task definitions and tool wrappers
    workflow.py                  # request -> triage -> audit -> validated result
    policy.py                    # supplied rule applicability and obligations
    output.py                    # operation registry, ordering, validation, CSV
    usage.py                     # measured calls/tokens and cost aggregation
    prompts.py                   # versioned instructions, visible source
  evaluation/
    main.py                      # public/custom case evaluation
    custom_cases.py              # at least three fictional fixtures/expectations
    evaluation_report.md         # required metrics, failures and improvements
    usage_report.md              # final full-run model/token/cost report
tests/                           # focused offline correctness tests
```

Create modules only as needed; split a file later if its actual complexity warrants it. Keep the existing entry points. Domain functions do not call SDKs directly, and prediction modules do not import evaluation answers. Do not build generic interfaces for unused providers or storage backends.

The default command is `uv run --locked python code/main.py`, reading dataset/ and writing root output.csv. After installing dependencies, `python3 code/main.py` remains the entry-point form documented by the starter. Use optional request/output arguments for sample runs so they cannot overwrite the final submission accidentally. Resolve paths relative to the repository root. Evaluation runs through code/evaluation/main.py against frozen predictions and separate public expected answers.

## 4. Data, state and output implementation

User-approved clarification on 2026-10-25: treat ASCII email casing differences as
equivalent for identity and evidence matching, preserve original spellings, and
reject ambiguous cross-subject normalized matches. This does not authorize
provider-specific dot/plus aliases, Unicode mailbox equivalence, or other guessed
identifier transformations. All availability/cutoff rules remain applicable.

Use exact typed identifiers, explicit CSV parsing and timezone-aware comparisons. Record original values alongside any justified normalization. Preserve source IDs and line/page/JSON-pointer/SQL-table locations. Observation time, file capture time and subject links remain separate. Filter by audit_at inside evidence access before returning context to the model.

Keep per-case state in memory. Parse common evidence once and reuse its indexed facts across cases, with case-specific cutoff filtering. A small content/version-keyed extraction cache can avoid repeated PDF/image work. Save completed case results and measured usage locally so a long run can be inspected; implement simple reuse only if needed, never a generic checkpoint service.

For supplied SQL, load a snapshot into a disposable SQLite database with external attachment/extension loading disabled, then query relevant tables. The agent receives narrow lookup tools rather than unrestricted SQL or shell access. Preserve primary/replica distinctions. For PDFs, pypdf extracts text but does not OCR images; use rendered pages/image input where needed. PDFium calls must be serial or isolated by process, not concurrent in threads within one process.

Start serially. Add a small bounded concurrency limit for independent cases or tool reads only after sample runs establish correct results and usage. Completion order must not affect final ordering. Bounded retries, model-turn limits, source errors and missing evidence remain explicit; they never produce fabricated facts.

Pydantic rejects extra fields and invalid types at output boundaries. A fixed operation registry enforces exact phase/operation/state combinations. Deterministic code assigns step numbers, canonical order and citation rules, and checks policy obligations/dependencies. A valid JSON schema is not evidence support. Verify subject-resource links and cutoff-admissible sources before accepting an assessment.

The final CSV must contain every evaluation case exactly once, sorted, with no additional columns/statuses. If a required case fails, preserve diagnostics and fix/retry it rather than silently skip it or claim the final run succeeded. A temporary file and final replace prevent publishing a truncated output. This failure handling is not an extra abstention mode or an alternative to completing the challenge.

## 5. Evaluation is part of the implementation

The repository's Evaluation instructions are a required deliverable, not deferred optional documentation. Build the evaluator alongside the solution and write results directly in code/evaluation/evaluation_report.md:

1. Case-level deletion-status accuracy across the labeled public/custom cases.
2. Step-level accuracy, with precision/recall and exact matching rules documented.
3. Field-level accuracy with stated alignment/denominators; missing/extra steps count as errors.
4. Sequence accuracy comparing ordered parsed arrays, ignoring object-key order and whitespace only.
5. At least three authored cases and their expected/actual results, exercising non-deletion, incomplete remediation and complete verification/retention.
6. Failures found and improvements made, including honest source-evidence gaps or unresolved predictions.

All 32 public samples are a development/regression set already inspected during design; do not describe them as an untouched holdout. Hidden evaluation truth is unavailable. Keep expected answers separate from prediction inputs. The broader acceptance catalog is a reference for targeted tests, not a requirement to implement every hypothetical scenario or a new operation vocabulary.

Write code/evaluation/usage_report.md from the final run that produces output.csv. Include OpenAI model names, call counts, input/output tokens, totals and averages per request, estimated total/per-request costs, and per-model plus overall totals. Count triage/audit/visual calls and reported retries; distinguish local tool calls from model requests. Do not double-count SDK aggregate totals and their per-request breakdowns. Report unknown usage and price/cache assumptions explicitly. Raw local usage files support the report but do not replace its Markdown contents.

## 6. Packaging and report-path reconciliation

README explicitly requires reports in code/evaluation/. AGENTS.md and the problem statement additionally name evaluation/ paths in code.zip. Maintain one source report pair in code/evaluation/. During packaging, copy that same pair into archive-root evaluation/ as well, checking the copies are identical. This small packaging rule satisfies both documented paths; there is no second reporting subsystem or manually maintained duplicate.

The archive contains runnable source, prompts/configuration, README, dependency metadata/lockfile and the required reports. Exclude dataset/, environments, caches, nested archives, credentials and real personal data. Root output.csv and log.txt remain separate submission artifacts. Update setup/run and archive instructions only when corresponding commands actually work.

## 7. First implementation milestone

- Create the uv environment using the existing Python 3.14.5 interpreter; declare/lock compatible dependencies.
- Implement typed contracts, operation registry, output validation and serialization.
- Add at least the three complete custom cases A01–A03 and tests for their expected rows plus malformed counterparts.
- Establish the OpenAI SDK dependency and confirm imports/structured task setup without API calls. The model and OPENAI_API_KEY are only needed for live runs.
- Add the evaluation entry point as soon as fixture predictions exist; do not write fabricated accuracy or usage numbers into reports.

Offline stubs validate orchestration/contracts only, not language understanding or visual accuracy. Actual live tests follow with a configured OpenAI model. Subsequent work is limited to the supplied data adapters, audit workflow, sample evaluation/improvements, and the complete 518-case run.

Pending configuration: concrete OpenAI model ID (with needed image support), spending limits for pilot/full run, and recorded price assumptions. Provider and Python version are settled. These settings do not justify a provider abstraction or block implementing the deterministic foundation.

## User-approved candidate publication amendment (2026-10-25)

The failure gate prevents unsupported evidence certification, rather than halting
implementation or batch processing. Structural output validation and semantic
source/policy/coverage validation are separate. Candidate mode processes every
request, retains independently grounded treatments, and records unresolved
conditions in internal diagnostics and the evaluation report. Unknown retention
periods and exclusive ownership are never supplied by default or inferred solely
from a subject match. Unsupported cases receive explicitly documented candidate
limitations; INCOMPLETE with no steps is an uncertified fallback, not a finding.
Only cases passing the complete existing semantic checks are evidence-validated.
The three-status CSV contract has no uncertainty value, so diagnostic counts and
output hashes must accompany any candidate file. Do not describe candidate row
coverage as full evidence validation or accuracy. Strict certification remains
available without --candidate.
