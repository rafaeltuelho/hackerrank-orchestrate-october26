# Fresh-session implementation handoff

Start a new chat in this repository's existing local checkout. The design/report files and log.txt are currently untracked; verify they exist before using another checkout or worktree. No implementation has been completed by the planning session. Recheck current files and Git status rather than assuming this snapshot is still current.

Paste the following prompt into the new session:

```text
Implement the approved Ghost Data Still Exists deletion-audit solution.

Repository:
/Users/rsoares/dev/github/rafaeltuelho/hackerrank-orchestrate-october26

This is a fresh implementation session. The design has been reviewed and its latest scope-limited version accepted. Proceed with implementation, not another architecture exercise.

First read AGENTS.md in full and follow its session/per-turn logging rules. Obtain your own exact harness/model identifiers from authoritative runtime metadata. Preserve existing untracked files and append to the existing root log.txt. Follow the referenced RTK instructions and graph-first code discovery guidance.

Then read these files relative to the repository root, in order:
1. problem_statement.md
2. README.md, especially code structure, Evaluation, and packaging
3. analysis/workflow-design.md
4. analysis/technical-decisions.md
5. analysis/model-recommendation.md
6. analysis/workflow-acceptance-cases.md
7. analysis/public-samples/report.md

Consult analysis/public-samples/case_exercises.md and case_matrix.csv selectively when investigating individual samples. You do not need the previous conversation history. Follow the latest documents; older proposals in log.txt may have been superseded.

Settled decisions:
- Use the existing system Python 3.14.5 and uv. Do not downgrade Python.
- OpenAI is the model provider. Use the OpenAI Agents SDK for bounded sequential triage/audit runs with narrow read-only tools, structured outputs, and measured usage.
- Python controls the workflow and validates evidence, policy, ordering, and serialization. No handoffs, worker-agent organization, provider router, generic workflow platform, or live deletion execution.
- Preserve code/main.py and code/evaluation/main.py as entry points. Required report sources belong in code/evaluation/. Follow the documented packaging reconciliation for archive-root evaluation/ copies.

Implement only the challenge: authorize deletion, reconstruct current/historical identity, inspect global activity/evidence at audit_at, apply supplied policy, preserve retained records/tombstones, and produce the required COMPLETE/INCOMPLETE/NOT_APPLICABLE output. Reported statuses are claims. Use participant-facing data only; expected answers are evaluation targets, never prediction inputs. Do not hardcode sample IDs, resource mappings, or case families. The sample audit documents evidence gaps; do not hide them with invented links or extra output operations.

Work in tested increments. Begin with Python/dependency setup and offline SDK compatibility, typed contracts, operation registry, output validation/serialization, and custom cases A01-A03. Then implement evidence tools, SDK integration, policy/planning, sample evaluation, and the full-dataset run as described in the plan. Add further catalog tests only where needed by the contract or observed failures.

Build evaluation alongside the solver: status, step, field and sequence accuracy; at least three custom cases; failures and improvements. Measure actual model calls/tokens/cost for the final run. Do not substitute mocked results or fabricated metrics for live evaluation.

Inspect existing model configuration without displaying credentials. The recommended baseline model/settings are recorded in analysis/model-recommendation.md; actual project access and spending limits remain unverified. If required configuration is missing, request it while continuing independent offline implementation; do not invent access or launch an unbounded paid run. Read secrets from environment variables only.

The end goal is a runnable solution, exactly 518 valid sorted rows in root output.csv, the required measured Markdown reports, and compliant submission artifacts. Do not claim completion while cases remain failed or evidence is unsupported. Report implemented behavior, tests actually run, measured results, and remaining blockers. Keep setup instructions consistent with commands that work. Do not modify the supplied dataset or expand scope.

Start by checking the working tree and implementing the first milestone.
```
