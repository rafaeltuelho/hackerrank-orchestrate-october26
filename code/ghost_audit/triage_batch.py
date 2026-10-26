"""Sequential bounded batches of independent request-only authorizations."""

import hashlib
import json

from agents import ModelSettings

from .agent import run_task, task_definitions
from .models import Authorization, Contract, Nonempty
from .prompts import TRIAGE


class Item(Contract):
    case_id: Nonempty
    authorization: Authorization


class Batch(Contract):
    items: list[Item]


def triage_key(request, model):
    return hashlib.sha256(
        json.dumps(
            {
                "request": request.model_dump(mode="json"),
                "model": model,
                "instructions": TRIAGE,
                "effort": "low",
                "schema": Authorization.model_json_schema(),
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()


async def prepare_triage(requests, model, budget, ledger, cache_dir):
    cache_dir.mkdir(parents=True, exist_ok=True)
    missing = [r for r in requests if not (cache_dir / (triage_key(r, model) + ".json")).exists()]
    triage, _ = task_definitions(model)
    triage = triage.clone(
        name="request_triage_batch",
        output_type=Batch,
        instructions=TRIAGE + "\nInput is a list of independent case_id/request_text pairs. "
        "Apply the authorization rules separately to each text. Return exactly one item per ID, "
        "with exact supporting spans from that item's text. Never share context between items.",
        model_settings=triage.model_settings.resolve(ModelSettings(max_tokens=12000)),
    )
    for offset in range(0, len(missing), 32):
        chunk = missing[offset : offset + 32]
        result = await run_task(
            triage,
            json.dumps(
                [{"case_id": r.case_id, "request_text": r.request_text} for r in chunk],
                ensure_ascii=False,
            ),
            case_id="batch:" + str(offset),
            stage="triage_batch",
            ledger=ledger,
            budget=budget,
            max_turns=1,
        )
        validate_batch(result, chunk)
        by_id = {i.case_id: i.authorization for i in result.items}
        for request in chunk:
            (cache_dir / (triage_key(request, model) + ".json")).write_text(
                by_id[request.case_id].model_dump_json(), encoding="utf-8"
            )
        print(
            f"Request-only triage cached: {min(offset + 32, len(missing))}/{len(missing)}",
            flush=True,
        )


def validate_batch(result, requests):
    if sorted(i.case_id for i in result.items) != sorted(r.case_id for r in requests):
        raise ValueError("TRIAGE_BATCH_CASE_SET_MISMATCH")
    texts = {r.case_id: r.request_text for r in requests}
    for item in result.items:
        if not item.authorization.request_spans or any(
            span not in texts[item.case_id] for span in item.authorization.request_spans
        ):
            raise ValueError("UNSUPPORTED_INTENT_SPAN")
