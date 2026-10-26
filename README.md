# HackerRank Orchestrate - October 2026

## Ghost Data Still Exists

Build an AI agent that audits whether a user's personal data was actually deleted.

A deletion workflow may report **Complete** while data still exists in databases, logs, support attachments, exports, search indexes, archives, or backups. Sync and restore processes may also bring deleted data back.

For each request, the agent must first determine whether deletion was actually requested. It then returns `COMPLETE`, `INCOMPLETE`, or `NOT_APPLICABLE`, reports any remaining data or recreation risk, and produces the ordered remediation and verification steps required to finish an authorized deletion safely.

Read [`problem_statement.md`](./problem_statement.md) for the complete challenge contract.

## Implementation status and tested setup

The first implementation milestone is complete: Python 3.14.5 dependency locking,
typed contracts, the operation registry, deterministic assessment assembly, output
validation/serialization, A01–A03 custom fixtures, evaluation metrics, and offline
OpenAI Agents SDK compatibility. Participant loaders, safe artifact extraction,
exact search, and conservative log readback normalization are also implemented.

**The implementation supports candidate publication; full evidence certification remains
incomplete.** Strict mode requires complete source/condition validation. Candidate mode
separates structural CSV checks from evidence validation, continues through unresolved
cases and writes diagnostics. The preliminary full pass uses bounded request-only model
triage and literal readbacks, with revalidated saved audit proposals where available.
It does not claim that every request received a fresh model evidence audit. See the
measured reports for the output hash, row coverage, acceptance counts and limitations.

Use the existing Python 3.14.5 interpreter with `uv`. In this checkout, preserve
the pre-existing notebook environment by selecting the dedicated project environment:

```bash
export UV_PROJECT_ENVIRONMENT=.venv-ghost
uv sync --locked --python 3.14.5
uv run --locked python code/main.py --preflight
uv run --locked pytest -q
uv run --locked ruff check code tests
uv run --locked python code/evaluation/main.py --custom-output runs/custom-output.csv
```

Run a bounded live pilot with a separate output path:

```bash
uv run --locked python code/main.py --requests dataset/sample_deletion_requests.csv \
  --limit 3 --output runs/pilot-output.csv --run-dir runs/pilot
```

For all public samples, omit `--limit` and keep a separate output/run directory.
The final command is `uv run --locked python code/main.py`, which writes root
`output.csv` only when all 518 cases validate. `--dataset` supports independently
authored evaluation fixtures; the submission default remains the supplied `dataset/`.
The shared persistent `runs/budget.jsonl` must be retained across runs: deleting it
would reset accounting. Failed/unknown requests retain their full reservation.

PowerShell uses `$env:UV_PROJECT_ENVIRONMENT = '.venv-ghost'` before the same `uv`
commands. A fresh clone may use uv's default `.venv` instead. Entry points resolve
dataset/report paths relative to the repository, including when launched elsewhere.
With dependencies installed in the selected interpreter, the direct entry-point
form is `python3 code/main.py --preflight`.

The evaluator writes measured offline custom results directly to
`code/evaluation/evaluation_report.md`. SDK tests use a local fake model and do
not measure language or visual accuracy. To evaluate frozen live predictions later:

```bash
uv run --locked python code/evaluation/main.py \
  --predictions runs/sample-output.csv --expected dataset/sample_output.csv
```

Expected outputs are opened only by evaluation; prediction modules use a fixed
participant-source allowlist. Search returns explicit extraction errors, pagination,
unknown observation times, and visual-review gaps. Empty search results are never
absence proofs. SQL snapshots execute in disposable in-memory SQLite databases
with external attachment and extension loading blocked. PDF rendering is serial.
Visual extraction keeps individual business records separate from neighboring rows.
Explicit query/readback times are parsed from literal text; a model-normalized date
is not accepted on its own. Application-screen captures directly date displayed
state; named business-document captures date observation of that document's own
contents, not the state of other accounts/orders mentioned in it. Embedded
historical snapshot times remain separate. Date-only observations retain an
explicit conservative interval; overlapping contradictory states remain conflicts.
Explicit catalog document-ID aliases can connect a statement/invoice to a logical
resource, with catalog provenance retained. They cannot turn an activity result
claim into state proof or create an ID from a filename/prefix.
ASCII email casing is equivalent, as explicitly approved by the user on 2026-10-25.
Original spellings are preserved; cross-subject case-insensitive collisions fail
identity resolution. This does not enable dot/plus aliases, Unicode mailbox
equivalence, case-insensitive resource IDs, or guessed hash/phone transformations.

The user-selected model is `gpt-6.1-sol`, configured as the default. Triage uses
low reasoning effort; audit and visual interpretation use medium
as specified in `analysis/model-recommendation.md`. SDK task runs explicitly use
the Responses API for tool calling. Luna/Astra remain optional future comparisons;
the baseline has no automatic model escalation. Visual transcription is integrated and cached.
An explicit `OPENAI_MODEL` environment variable overrides that default. Model selection does
not establish API access. The CLI loads the repository-root `.env` automatically;
existing process environment variables take precedence. Set your key in the blank
`OPENAI_API_KEY` entry there. The file also contains `OPENAI_MODEL=gpt-6.1-sol` and
`GHOST_BUDGET_USD=50.00`. `.env` is ignored by Git and must be excluded from packaging.
The budget setting may lower the approved ceiling but cannot raise it above $50.
Before live runs, verify model price assumptions. The approved budget is **USD 50.00
total across the pilot and full run**; pilot, retry, and visual-call costs all count
toward that same ceiling. Every live model request reserves a conservative allowance
before sending and settles from reported usage; separate processes lock the same
ledger. HTTP and SDK automatic retries are disabled, and explicit audit repairs are
limited to one. Unknown usage retains its reservation. Live requests are restricted
to the priced Sol baseline, Standard service tier and local function tools.
Do not put credentials in source, logs, reports, or command arguments.
Offline preflight/tests/custom fixtures need no API key. Live solver commands require
OPENAI_API_KEY. Measured development and candidate usage are recorded in the reports.

For packaging after completion, use `uv run --locked python code/package_submission.py`.
It checks the exact 518-case output and requires both measured reports to name that
output's SHA-256. It includes dependency metadata, README and source, and copies the
authoritative `code/evaluation/` report pair identically into archive-root
`evaluation/`. It excludes dataset, credentials, local run files, output.csv, log.txt,
environments and nested archives. Use `--candidate` when packaging an explicitly labeled candidate; both report hashes
must match the exact output file.

---

## Quick Start

Clone the repository and move into the project directory:

```bash
git clone https://github.com/interviewstreet/hackerrank-orchestrate-october26.git
cd hackerrank-orchestrate-october26
```

Start your AI coding tool from the **repository root** so it automatically reads [`AGENTS.md`](./AGENTS.md) and logs your session turns to `log.txt` in the root directory.

Build your solution in `code/main.py`, or use another language and document its setup and run command clearly in your README.

Your solution must:

- Read the input files from `dataset/`
- Generate one prediction row for every request in `dataset/deletion_requests.csv`
- Write the final predictions to `output.csv` in the repository root

Run the starter Python entry point with:

```bash
python3 code/main.py
```

The blank template at `dataset/output.csv` is provided as a reference. Your final generated file for submission must be the root-level `output.csv`.


## Dataset

All participant-facing files are in `dataset/`:

| File | Contents |
| --- | --- |
| `deletion_requests.csv` | 518 requests |
| `sample_deletion_requests.csv` | 32 sample requests |
| `sample_output.csv` | Correct sample answers |
| `user_identities.csv` | Current user identities |
| `user_audit_log.csv` | Historical identity changes |
| `system_activity.csv` | Activity across services and data processes |
| `deletion_rules.csv` | Required treatment for each data category |
| `evidence_files.csv` | Manifest of supplied evidence files |
| `output.csv` | Blank output template |

Evidence is stored under `dataset/evidence/` and may include PDFs, images, logs, JSON, plain text, or SQL snapshot exports. SQL captures may contain a primary database, regional replicas, a reporting replica, or a failover replica so replication drift can be investigated directly. The `.sql` files are readable as text and executable with SQLite.

Only `deletion_requests.csv` requires answers. The other files provide evidence and context.

---

## Output

Create `output.csv` with these columns in this exact order:

```text
case_id,deletion_status,steps_json
```

Produce exactly one row per request. `deletion_status` is `COMPLETE`, `INCOMPLETE`, or `NOT_APPLICABLE`. `steps_json` is an ordered JSON array containing findings, remediation actions, and verification checks. Use an empty array (`[]`) for `NOT_APPLICABLE`. Evidence references may be a `file_id`, `activity_id`, or `audit_id`. Determine the resource state at `audit_at` from the available evidence; reported workflow statuses and operation results are claims. Use `dataset/sample_output.csv` as the format reference.

The final file must contain 518 data rows sorted by `case_id` (plus the header row). The grader parses `steps_json` as JSON, so object-key order and whitespace do not matter; array order does. Order findings, remediation, and verification in that phase order. Within a phase, follow the operation order in the problem statement, then sort by `system_id` and `resource_id`.

---

## Evaluation

`output.csv` will be compared with hidden canonical answers. Scoring considers:

- deletion assessment accuracy;
- current and historical identity resolution;
- discovery of remaining data and recreation risks;
- correct policy application and evidence references; and
- completeness and ordering of remediation and verification steps.

Your `code.zip` must include:

```text
code/evaluation/evaluation_report.md
code/evaluation/usage_report.md
```

- `evaluation_report.md` must cover case, row, field, and sequence accuracy, at least three additional evaluation cases created by you, failures found, and improvements made.
- `usage_report.md` must cover the final full-dataset run, including model providers and names, model calls, input and output tokens, total and average tokens per request, and estimated total and per-request cost. Include per-model and overall totals when using multiple models.

**Important:** Place `evaluation_report.md` and `usage_report.md` inside `code/evaluation/` (matching `code/evaluation/main.py` in this starter layout), write your complete evaluation metrics, custom evaluation test cases, and token/cost breakdowns directly inside those Markdown files, and keep prompts in source code or Markdown files. Automated code evaluation ignores raw data files (`.csv`, `.tsv`, `.json`, `.jsonl`, `.sql`, `.log`), so content stored only in those formats will not be visible to the code judge or AI interviewer.

---

## Chat Transcript

This repository includes [`AGENTS.md`](./AGENTS.md), which instructs compatible AI coding tools to append conversation summaries to `log.txt` in the repository root:

| Platform | Path |
| --- | --- |
| macOS / Linux | `<repo root>/log.txt` |
| Windows | `<repo root>\log.txt` |

- Always launch your AI coding agent from the repository root (or explicitly ask it to read `./AGENTS.md` first) so every turn is logged to `log.txt` with the required `User Prompt`, `Agent Response Summary`, `Actions`, and `Context` sections.
- Upload `log.txt` directly as your `chat_transcript` submission on HackerRank.
- Do not include API keys, tokens, credentials, or secrets in prompts, code, configuration, or `log.txt`.

---

## Packaging `code.zip` and Submission

| Item | Description |
| --- | --- |
| `code.zip` | Runnable solution, prompts, configuration, `README.md`, and `evaluation/` reports |
| `output.csv` | One answer row for each of the 518 requests in `dataset/deletion_requests.csv` |
| `chat_transcript` | The root `log.txt` file generated by your coding agent |
| AI interview | Live explanation of your architecture, approach, and evaluation |

You may use any programming language, model, framework, or retrieval approach. Include clear setup and execution instructions in `README.md` inside `code.zip`.

After the full run and matching measured reports are complete, package from the repository root:

```bash
UV_PROJECT_ENVIRONMENT=.venv-ghost uv run --locked python code/package_submission.py
```

The packaging command validates all 518 output rows and the report output hashes. It includes
the locked environment metadata, source and reports, with required reports also at the archive
root under `evaluation/`. Its allowlist excludes dataset files, credentials, virtual environments,
caches, run artifacts and nested archives. Supply `OPENAI_API_KEY` through the environment when
running the extracted submission; the local `.env` is excluded.

Before submitting, confirm that:

- `output.csv` has the exact header `case_id,deletion_status,steps_json` and contains all 518 data rows sorted by `case_id`;
- every `steps_json` value is a valid JSON array with consecutive step numbers starting at `1`;
- findings cite valid evidence IDs, and `COMPLETE` verification steps cite evidence proving the current state;
- proposed remediation and future verification steps use an empty `evidence_id` (`""`);
- `code.zip` includes your runnable code, `README.md`, `code/evaluation/evaluation_report.md`, and `code/evaluation/usage_report.md`;
- `log.txt` follows the `AGENTS.md` turn format and is uploaded to the `chat_transcript` slot; and
- no API keys, credentials, real personal data, or sensitive configuration values are included.

## Candidate output and evidence certification

Run `UV_PROJECT_ENVIRONMENT=.venv-ghost uv run --locked python code/main.py --candidate`
to process all requests and write a structurally checked candidate `output.csv`.
Run without `--candidate` to require complete semantic evidence validation before
publication. Both modes use the same source, cutoff, identity and policy checks.

Candidate mode retains independently supported treatments when whole-case coverage
is unresolved. It never supplies an unknown retention duration or assumes exclusive
attachment ownership from a subject match. Cases without a supported plan use
`INCOMPLETE` with an empty array as an **uncertified placeholder**, not as a claim
that a policy violation was proved. Inspect `runs/current/diagnostics.json` and the
measured evaluation report before interpreting any candidate result. Exactly 518
rows establish structural coverage; they do not establish evidence completeness or
accuracy. The run summary counts evidence-validated cases separately. If the shared
budget stops paid calls, remaining cases still receive diagnostics and placeholders;
these cases are not described as model-audited. Operational failure messages contain
error codes rather than credential-bearing HTTP response bodies.

For a preliminary candidate pass over all cases with bounded request-only triage
and literal readback extraction, use:

```bash
UV_PROJECT_ENVIRONMENT=.venv-ghost uv run --locked python code/main.py \
  --candidate --readbacks-only --batch-triage --run-dir runs/preliminary
```

This mode does **not** run the model evidence investigator for every case. It
returns partial evidence inventories and records that limitation, rather than
certifying completeness from a subset of source formats. `--proposal-run PATH`
can revalidate previously saved model proposals against the current subject,
cutoff, corpus and policy checks; it never reads expected outputs. Request-only
triage batches contain at most 32 independent texts, require the exact case set
and exact item-specific supporting spans, and run sequentially. The default
candidate mode still performs individual model evidence audits.

To package the current candidate, regenerate the report for the exact output and
use the explicit candidate packaging mode:

```bash
UV_PROJECT_ENVIRONMENT=.venv-ghost uv run --locked python code/evaluation/live_report.py
UV_PROJECT_ENVIRONMENT=.venv-ghost uv run --locked python code/evaluation/candidate_report.py \
  --run-dir runs/full-candidate-v2
UV_PROJECT_ENVIRONMENT=.venv-ghost uv run --locked python code/package_submission.py --candidate
```

The output file is a preliminary candidate. Consult the evaluation report for the
counts of supported plans, unresolved placeholders and evidence-validated cases.
A full model investigation of every case and stronger step/sequence accuracy remain
future implementation/evaluation work. The general policy clarification draft is
in `analysis/participant-clarification.md`; it has not been sent externally.

## OpenAI console logs and SDK traces

All future live model calls explicitly set Responses `store=True`, including
request triage, batched triage, evidence audits, repair calls, visual extraction and
tool continuations. Responses carry `workflow=ghost_data`, `case_id` and `stage`
metadata to make them easier to identify in [OpenAI Logs](https://platform.openai.com/logs).
Use the organization/project associated with `OPENAI_API_KEY` in the console.

Hosted Agents SDK tracing is also enabled, with workflow names `ghost_data.<stage>`
and case IDs as trace group IDs. Prompt/response and tool content capture is enabled
for this fictional challenge dataset. The exporter authenticates with the same key
as the model client; that key is not added to metadata or prompts. Buffered traces
are flushed after each completed or failed SDK run. Inspect SDK workflow spans in
[OpenAI Traces](https://platform.openai.com/traces).

These settings apply to new live calls. Local cache hits and deterministic evidence
processing make no API request, and prior calls made with storage/tracing disabled
are not backfilled. Hosted visibility depends on successful ingestion and the
project's account/data controls. Offline fake-model tests do not export traces.
Existing measured reports describe their historical runs, whose tracing was disabled;
no predictions or paid full-dataset runs were repeated for this configuration change.
A one-call live smoke confirmed that the response was stored and retrievable, with
`case_id=tracing_smoke` and `stage=tracing_smoke`. The console UI itself was not inspected.
