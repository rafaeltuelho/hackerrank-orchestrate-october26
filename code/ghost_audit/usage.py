"""Append-only local SDK usage; exceptions never masquerade as zero tokens."""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from agents import RunHooks


@dataclass
class UsageEntry:
    provider: str
    model: str
    case_id: str
    stage: str
    requests: int
    input_tokens: int | None
    output_tokens: int | None
    status: str


class UsageLedger:
    def __init__(self, path: Path | None = None):
        self.path = path
        self.entries: list[UsageEntry] = []
        if path and path.exists():
            # A restarted evidence pass keeps the same measured run ledger.
            names = UsageEntry.__dataclass_fields__
            self.entries = [
                UsageEntry(**{k: value[k] for k in names})
                for line in path.read_text(encoding="utf-8").splitlines()
                if line
                for value in [json.loads(line)]
            ]

    def record(self, entry: UsageEntry) -> None:
        self.entries.append(entry)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"at": datetime.now(UTC).isoformat(), **asdict(entry)}) + "\n")

    def totals(self) -> dict:
        return {
            "requests": sum(e.requests for e in self.entries),
            "known_input_tokens": sum(e.input_tokens or 0 for e in self.entries),
            "known_output_tokens": sum(e.output_tokens or 0 for e in self.entries),
            "unknown_usage_requests": sum(
                e.requests
                for e in self.entries
                if e.input_tokens is None or e.output_tokens is None
            ),
        }


class UsageHooks(RunHooks):
    """Per-response hooks retain completed usage even if the subsequent turn fails."""

    def __init__(self, ledger: UsageLedger, model: str, case_id: str, stage: str):
        self.ledger, self.model, self.case_id, self.stage = ledger, model, case_id, stage
        self.pending = 0

    async def on_llm_start(self, context, agent, system_prompt, input_items):
        self.pending += 1

    async def on_llm_end(self, context, agent, response):
        usage = response.usage
        self.ledger.record(
            UsageEntry(
                "OpenAI",
                self.model,
                self.case_id,
                self.stage,
                usage.requests,
                usage.input_tokens,
                usage.output_tokens,
                "COMPLETED",
            )
        )
        self.pending -= 1

    def record_failure(self) -> None:
        if self.pending:
            self.ledger.record(
                UsageEntry(
                    "OpenAI",
                    self.model,
                    self.case_id,
                    self.stage,
                    self.pending,
                    None,
                    None,
                    "FAILED_USAGE_UNAVAILABLE",
                )
            )
            self.pending = 0
