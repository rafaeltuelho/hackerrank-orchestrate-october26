"""Ghost Data Still Exists command line entry point."""

import argparse
import asyncio
import json
import os
from pathlib import Path

from ghost_audit.agent import task_definitions
from ghost_audit.budget import Budget
from ghost_audit.candidate import unsupported_candidate
from ghost_audit.config import (
    AUDIT_REASONING_EFFORT,
    TRIAGE_REASONING_EFFORT,
    VISION_REASONING_EFFORT,
    budget_limit_usd,
    load_environment,
    model_id,
)
from ghost_audit.data import ROOT, Dataset, load_requests
from ghost_audit.evidence import EvidenceStore
from ghost_audit.models import AuditError
from ghost_audit.output import write_csv
from ghost_audit.pipeline import audit_request
from ghost_audit.usage import UsageLedger
from ghost_audit.vision import prepare_visuals


def main() -> None:
    load_environment()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="validate participant inputs and SDK schemas without API calls",
    )
    parser.add_argument("--requests", type=Path, default=ROOT / "dataset/deletion_requests.csv")
    parser.add_argument("--dataset", type=Path, default=ROOT / "dataset")
    parser.add_argument("--output", type=Path, default=ROOT / "output.csv")
    parser.add_argument("--limit", type=int, help="bounded pilot; requires an explicit output path")
    parser.add_argument("--run-dir", type=Path, default=ROOT / "runs/current")
    parser.add_argument(
        "--skip-vision", action="store_true", help="debug only; visual gaps block rows"
    )
    parser.add_argument(
        "--candidate",
        action="store_true",
        help="publish structurally valid candidates with separate evidence diagnostics",
    )
    parser.add_argument(
        "--readbacks-only",
        action="store_true",
        help="candidate partial inventory; no new model audit calls",
    )
    parser.add_argument(
        "--batch-triage",
        action="store_true",
        help="cache request-only triage in sequential batches of at most 32",
    )
    parser.add_argument(
        "--proposal-run",
        type=Path,
        help="revalidate saved model proposals as candidates against current evidence",
    )
    args = parser.parse_args()
    if (args.readbacks_only or args.proposal_run) and not args.candidate:
        parser.error("partial/replayed proposals require --candidate")
    if args.preflight:
        data = Dataset()
        requests = load_requests(ROOT / "dataset/deletion_requests.csv")
        selected_model = model_id()
        task_definitions(selected_model)
        print(
            f"Python/SDK schemas OK; {len(requests)} requests; "
            f"{len(data.manifest)} evidence files; {len(data.rules)} policy rules."
        )
        print("OPENAI_API_KEY: " + ("set" if os.getenv("OPENAI_API_KEY") else "missing"))
        print("Model: " + selected_model)
        print(
            f"Reasoning: triage={TRIAGE_REASONING_EFFORT}; "
            f"audit={AUDIT_REASONING_EFFORT}; vision={VISION_REASONING_EFFORT}"
        )
        print(f"Configured combined pilot/full-run ceiling: USD {budget_limit_usd():.2f}")
        print("No API calls or output.csv writes performed.")
        return
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("OPENAI_API_KEY is missing from environment/.env")
    if args.limit is not None and (args.limit < 1 or args.output.resolve() == ROOT / "output.csv"):
        parser.error("--limit must be positive and use a separate --output pilot path")
    requests = load_requests(args.requests)
    if args.limit:
        requests = requests[: args.limit]
    if args.output.resolve() == ROOT / "output.csv":
        canonical = load_requests(ROOT / "dataset/deletion_requests.csv")
        if sorted(r.case_id for r in requests) != sorted(r.case_id for r in canonical):
            parser.error("root output.csv requires the exact full 518-case evaluation set")
    asyncio.run(run(requests, args))


async def run(requests, args):
    dataset, ledger = Dataset(args.dataset), UsageLedger(args.run_dir / "usage.jsonl")
    store = EvidenceStore(dataset)
    budget = Budget(ROOT / "runs/budget.jsonl", budget_limit_usd())
    preparation_errors = []
    if args.batch_triage:
        from ghost_audit.triage_batch import prepare_triage

        try:
            await prepare_triage(
                requests, model_id(), budget, ledger, args.run_dir.parent / "triage-cache"
            )
        except Exception as exc:
            if not args.candidate:
                raise
            preparation_errors.append("TRIAGE_PREPARATION:" + type(exc).__name__)
    if not args.skip_vision:
        try:
            await prepare_visuals(
                store,
                max(r.audit_at for r in requests),
                model_id(),
                budget,
                ledger,
                ROOT / "runs/visual-cache",
            )
        except Exception as exc:
            if not args.candidate:
                raise
            preparation_errors.append("VISUAL_PREPARATION:" + type(exc).__name__)
    results, failures, diagnostics = [], [], []
    budget_stopped = False
    args.run_dir.mkdir(parents=True, exist_ok=True)
    for request in requests:
        try:
            result = await audit_request(
                request,
                dataset,
                store,
                model_id(),
                budget,
                ledger,
                args.run_dir,
                candidate=args.candidate,
                readbacks_only=args.readbacks_only or budget_stopped,
                proposal_run=args.proposal_run,
            )
            if isinstance(result, tuple):
                result, diagnostic = result
            else:
                diagnostic = {
                    "case_id": request.case_id,
                    "structurally_valid": True,
                    "evidence_validated": True,
                    "diagnostics": [],
                }
            diagnostics.append(diagnostic)
            results.append(result)
            print(f"{request.case_id}: {result.deletion_status}", flush=True)
            with (args.run_dir / "results.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(result.model_dump_json() + "\n")
        except Exception as exc:
            code = str(exc) if isinstance(exc, AuditError) else type(exc).__name__
            failures.append({"case_id": request.case_id, "code": code})
            with (args.run_dir / "failures.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(failures[-1]) + "\n")
            print(f"{request.case_id}: unresolved ({code})", flush=True)
            if args.candidate:
                result, diagnostic = unsupported_candidate(request.case_id, code)
                results.append(result)
                diagnostics.append(diagnostic)
                with (args.run_dir / "results.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(result.model_dump_json() + "\n")
            if code in {"BUDGET_EXHAUSTED", "AuthenticationError", "PermissionDeniedError"}:
                if not args.candidate:
                    break
                budget_stopped = True
    (args.run_dir / "diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8"
    )
    (args.run_dir / "failures.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")
    (args.run_dir / "summary.json").write_text(
        json.dumps(
            {
                "requested_ids": [r.case_id for r in requests],
                "successful_ids": [r.case_id for r in results],
                "failures": failures,
                "usage": ledger.totals(),
                "model": model_id(),
                "complete": len(results) == len(requests),
                "candidate_mode": args.candidate,
                "preparation_errors": preparation_errors,
                "readbacks_only": args.readbacks_only,
                "proposal_run": str(args.proposal_run) if args.proposal_run else None,
                "evidence_validated_cases": sum(d["evidence_validated"] for d in diagnostics),
                "fully_evidence_validated": not failures
                and all(d["evidence_validated"] for d in diagnostics),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "successful_cases": len(results),
                "failed_cases": len(failures),
                "usage": ledger.totals(),
                "budget_committed_upper_usd": str(budget.committed),
            }
        )
    )
    if (failures and not args.candidate) or len(results) != len(requests):
        raise SystemExit("Requested case set is incomplete; output CSV was not replaced.")
    write_csv(args.output, results, [r.case_id for r in requests], semantic=not args.candidate)


if __name__ == "__main__":
    main()
