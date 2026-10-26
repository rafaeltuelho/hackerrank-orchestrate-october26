"""Serial, persistent request reservations for the authorized shared spending ceiling.

Prices verified 2026-10-25: Standard Sol input/output $2/$10 per million;
cache writes up to $5 short/$10 long. Reservations conservatively allow those
write rates and a 10% regional premium. No discount is assumed for enforcement.
Unknown/failed calls retain the entire reservation; restarting never resets it.
"""

import json
import os
from contextlib import contextmanager
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from agents import Model

from .models import AuditError

MILLION = Decimal(1000000)


def upper_cost(input_tokens: int, output_tokens: int) -> Decimal:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("negative usage")
    input_rate, output_rate = (5, 10) if input_tokens <= 272000 else (10, 15)
    return (
        Decimal(input_tokens * input_rate + output_tokens * output_rate) / MILLION * Decimal("1.10")
    )


class Budget:
    def __init__(self, path: Path, ceiling: Decimal):
        if not ceiling.is_finite() or not Decimal(0) < ceiling <= Decimal(50):
            raise ValueError("budget must be positive and <= USD 50")
        self.path, self.ceiling = path, ceiling
        self.pending: dict[str, Decimal] = {}
        self.charges: dict[str, Decimal] = {}
        self._reload()

    def _reload(self):
        self.pending.clear()
        self.charges.clear()
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                self._apply(json.loads(line))

    @contextmanager
    def _locked(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_suffix(".lock").open("a+b") as handle:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                handle.write(b"0")
                handle.flush()
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                self._reload()
                yield
            finally:
                if os.name == "nt":
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle, fcntl.LOCK_UN)

    def _apply(self, event: dict) -> None:
        call_id, amount = event["call_id"], Decimal(event["usd"])
        if event["event"] == "reserve":
            if call_id in self.pending or call_id in self.charges:
                raise AuditError("DUPLICATE_BUDGET_RESERVATION")
            self.pending[call_id] = amount
        elif event["event"] == "settle":
            if call_id not in self.pending or amount > self.pending[call_id]:
                raise AuditError("INVALID_BUDGET_SETTLEMENT")
            del self.pending[call_id]
            self.charges[call_id] = amount
        else:
            raise AuditError("UNKNOWN_BUDGET_EVENT")

    @property
    def committed(self) -> Decimal:
        return sum(self.pending.values(), Decimal(0)) + sum(self.charges.values(), Decimal(0))

    def _append(self, event: dict) -> None:
        self._apply(event)  # Validate before appending; bad settlements never corrupt the ledger.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"at": datetime.now(UTC).isoformat(), **event}) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def reserve(self, input_bound: int, output_bound: int) -> str:
        amount = upper_cost(input_bound, output_bound)
        with self._locked():
            if self.committed + amount > self.ceiling:
                raise AuditError("BUDGET_EXHAUSTED")
            call_id = str(uuid4())
            self._append({"event": "reserve", "call_id": call_id, "usd": str(amount)})
        return call_id

    def settle(self, call_id: str, input_tokens: int, output_tokens: int) -> None:
        with self._locked():
            self._append(
                {
                    "event": "settle",
                    "call_id": call_id,
                    "usd": str(upper_cost(input_tokens, output_tokens)),
                }
            )


class BudgetedModel(Model):
    """All live Responses requests pass through this wrapper, including tool continuations."""

    def __init__(self, delegate: Model, budget: Budget):
        self.delegate, self.budget = delegate, budget

    async def get_response(
        self,
        system_instructions,
        input,
        model_settings,
        tools,
        output_schema,
        handoffs,
        tracing,
        **kwargs,
    ):
        if handoffs or any(not hasattr(t, "params_json_schema") for t in tools):
            raise AuditError("UNPRICED_HOSTED_TOOL")
        if model_settings.max_tokens is None or model_settings.max_tokens > 128000:
            raise AuditError("OUTPUT_LIMIT_REQUIRED")
        payload = {
            "instructions": system_instructions,
            "input": input,
            "tools": [
                {"name": t.name, "description": t.description, "parameters": t.params_json_schema}
                for t in tools
            ],
            "schema": output_schema.json_schema() if output_schema else None,
        }
        wire = json.dumps(payload, ensure_ascii=False, default=str)
        if '"input_image"' in wire or '"input_file"' in wire:
            # Multimodal tokens depend on image shape/detail: reserve the model's
            # full input limit, settle from actual provider usage afterwards.
            input_bound = 922000
        else:
            # UTF-8 bytes upper-bound text tokens; margin covers protocol/schema framing.
            input_bound = len(wire.encode("utf-8")) + 16384
            if input_bound > 256000:
                raise AuditError("TEXT_CONTEXT_LIMIT")
        call_id = self.budget.reserve(input_bound, model_settings.max_tokens)
        response = await self.delegate.get_response(
            system_instructions,
            input,
            model_settings,
            tools,
            output_schema,
            handoffs,
            tracing,
            **kwargs,
        )
        usage = response.usage
        if usage.requests != 1 or usage.input_tokens < 0 or usage.output_tokens < 0:
            raise AuditError("PROVIDER_USAGE_UNAVAILABLE")
        self.budget.settle(call_id, usage.input_tokens, usage.output_tokens)
        return response

    async def stream_response(self, *args, **kwargs):
        raise AuditError("STREAMING_NOT_SUPPORTED")
        yield
