"""Measured candidate-run coverage, semantic limitations and attributable usage."""

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ghost_audit.data import ROOT
from ghost_audit.models import Result
from ghost_audit.output import HEADER, validate_result


def write_candidate_report(run_dir: Path, root: Path = ROOT):
    run_dir = run_dir.resolve()
    summary = json.loads((run_dir / "summary.json").read_text())
    diagnostics = json.loads((run_dir / "diagnostics.json").read_text())
    output = root / "output.csv"
    with output.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != HEADER:
            raise ValueError("Invalid candidate CSV header")
        rows = list(reader)
    results = [
        Result.model_validate(
            dict(
                case_id=r["case_id"],
                deletion_status=r["deletion_status"],
                steps=json.loads(r["steps_json"]),
            )
        )
        for r in rows
    ]
    if [r.case_id for r in results] != sorted(summary["requested_ids"]):
        raise ValueError("Candidate does not match measured run")
    if len({d["case_id"] for d in diagnostics}) != len(results):
        raise ValueError("Missing or duplicate case diagnostics")
    for result in results:
        validate_result(result, semantic=False)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    certified = sum(d["evidence_validated"] for d in diagnostics)
    empty = sum(r.deletion_status == "INCOMPLETE" and not r.steps for r in results)
    statuses = Counter(r.deletion_status for r in results)
    diag_by_id = {d["case_id"]: d for d in diagnostics}
    run_name = run_dir.relative_to(root).as_posix()
    lines = [
        "## Full candidate output measurement",
        "",
        "Output kind: candidate",
        f"Run output SHA-256: {digest}",
        "",
        f"Measured run: `{run_name}`.",
        f"Structurally valid sorted output rows: {len(results)}.",
        f"Cases passing complete semantic evidence checks: {certified}/{len(results)}.",
        f"Uncertified INCOMPLETE rows with no steps: {empty}.",
        f"Status distribution: {dict(sorted(statuses.items()))}.",
        "",
        "This is a best-supported preliminary candidate, not a fully evidence-validated solution. "
        "No hidden expected outputs are available for these requests, so deletion-status, "
        "step-level, field-level and sequence accuracy on this file are unavailable. "
        "Row coverage and semantic acceptance are not accuracy metrics. The public and "
        "authored measured evaluations above remain separately labeled.",
        "",
        "INCOMPLETE with an empty step array is an uncertified placeholder imposed by the "
        "three-status serialization vocabulary. It does not assert that a remaining record "
        "or policy violation was proved. Partial plans contain independently validated "
        "treatments; unresolved records are omitted from treatment rather than deleted by "
        "default. Unknown retention windows and exclusive ownership remain unknown.",
        "",
        "This run used request-only model triage in sequential bounded batches plus cached "
        "individual authorizations. The evidence pass used literal readbacks and revalidated "
        "saved model proposals where available. It did not perform a fresh model evidence "
        "audit for every case. Literal inventory cannot certify that unclassified visual, "
        "document, dependency and conditional-policy evidence is exhausted.",
        "",
        "The earlier serial model pass was interrupted after four completed cases to "
        "implement the full preliminary pass. Its interrupted-call reservation remains "
        "charged conservatively. No unknown usage was converted to zero.",
        "",
        "General participant-facing clarification remains needed for missing retention "
        "periods, exclusive attachment ownership, and the intended answer when a rule "
        "condition is unestablished. The clarification draft has not been sent externally.",
        "",
        "| Case | Candidate status | Steps | Evidence validated | Limitations |",
        "|---|---|---:|---|---|",
    ]
    for result in results:
        diagnostic = diag_by_id[result.case_id]
        details = "; ".join(diagnostic["diagnostics"])
        details = re.sub(r"[^\s;|]+@[^\s;|]+", "[email omitted]", details)
        details = details.replace("|", "/").replace("\n", " ")
        if len(details) > 220:
            details = details[:217] + "..."
        lines.append(
            f"| {result.case_id} | {result.deletion_status} | {len(result.steps)} | "
            f"{'yes' if diagnostic['evidence_validated'] else 'no'} | {details} |"
        )
    report = root / "code/evaluation/evaluation_report.md"
    original = report.read_text().split("## Full candidate output measurement")[0].rstrip()
    report.write_text(original + "\n\n" + "\n".join(lines) + "\n")
    records = [json.loads(line) for line in (run_dir / "usage.jsonl").read_text().splitlines()]
    grouped = defaultdict(lambda: [0, 0, 0, 0])
    for record in records:
        values = grouped[record["model"], record["stage"]]
        values[0] += record["requests"]
        values[1] += record["input_tokens"] or 0
        values[2] += record["output_tokens"] or 0
        values[3] += record["requests"] if record["input_tokens"] is None else 0
    totals = [sum(v[i] for v in grouped.values()) for i in range(4)]
    estimate = (Decimal(totals[1]) * 2 + Decimal(totals[2]) * 10) / Decimal(1000000)
    usage = [
        "## Measured full candidate pass",
        "",
        "Output kind: candidate",
        f"Run output SHA-256: {digest}",
        "",
        f"Run: `{run_name}`; requests: {len(results)}.",
        "Provider: OpenAI; model: gpt-6.1-sol. Request-only triage effort: low. "
        "Reused audit/vision preparation used medium effort.",
        "",
        "| Model | Stage | Model calls | Known input | Known output | Unknown calls |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for (model, stage), values in sorted(grouped.items()):
        usage.append("| " + " | ".join([model, stage] + list(map(str, values))) + " |")
    usage += [
        "| Overall | All stages | " + " | ".join(map(str, totals)) + " |",
        "",
        f"Known total tokens: {totals[1] + totals[2]}; average per request: "
        f"{(totals[1] + totals[2]) / len(results):.3f}.",
        f"Known-token uncached baseline estimate for new calls in this pass: "
        f"USD {estimate:.6f}; per request: USD {estimate / len(results):.8f}.",
        "",
        "This estimate excludes cache rate changes and unreported usage; it is not an "
        "invoice. Cache hits have zero new calls/tokens, not zero historical cost. "
        "The development totals above include the historical visual extraction, "
        "cached individual authorizations and saved audit proposals reused by this "
        "pass, plus failed and superseded work. No fraction of that shared preparation "
        "is silently relabeled as a new call or assigned a fabricated exact per-case "
        "cost. Thus the new-call estimate is incremental, not total end-to-end cost. "
        "The all-development committed ceiling is the conservative cost bound covering "
        "all preparation and this run. Local readback processing makes no model call.",
        "",
        "A final fully evidence-validated run is still unavailable. These candidate "
        "measurements replace neither the semantic limitations nor the unknown hidden "
        "accuracy. Credentials are excluded.",
    ]
    from ghost_audit.budget import Budget
    from ghost_audit.config import APPROVED_BUDGET_USD

    from evaluation.live_report import development_usage

    all_records = development_usage(root)
    all_input = sum(r["input_tokens"] or 0 for r in all_records)
    all_output = sum(r["output_tokens"] or 0 for r in all_records)
    all_calls = sum(r["requests"] for r in all_records)
    all_unknown = sum(r["requests"] for r in all_records if r["input_tokens"] is None)
    all_estimate = (Decimal(all_input) * 2 + Decimal(all_output) * 10) / Decimal(1000000)
    budget = Budget(root / "runs/budget.jsonl", APPROVED_BUDGET_USD)
    usage += [
        "",
        "### Conservative inclusive preparation allocation",
        "",
        "For an inclusive bound, allocate all recorded development preparation, "
        "superseded attempts and evaluation overhead to this candidate. This "
        "deliberately overallocates shared preparation; it is not exact marginal "
        "cache attribution or an invoice. The preceding stage table reports the "
        "measured candidate pass separately, without double counting.",
        "",
        f"Allocated overall OpenAI/gpt-6.1-sol calls: {all_calls}; "
        f"unknown-usage calls: {all_unknown}.",
        f"Allocated known input/output/total tokens: {all_input}/{all_output}/"
        f"{all_input + all_output}; mean total per candidate request: "
        f"{(all_input + all_output) / len(results):.3f}.",
        f"Allocated known-token uncached baseline estimate: USD {all_estimate:.6f}; "
        f"per candidate request: USD {all_estimate / len(results):.8f}.",
        f"Inclusive committed budget allowance (including unknown reservations): "
        f"USD {budget.committed:.6f}; per candidate request: "
        f"USD {budget.committed / len(results):.8f}.",
    ]
    report = root / "code/evaluation/usage_report.md"
    original = report.read_text().split("## Measured full candidate pass")[0].rstrip()
    original = original.replace(
        "Not completed. No final 518-row output.csv exists.",
        "No fully evidence-validated final run is complete. A 518-row candidate exists.",
    )
    report.write_text(original + "\n\n" + "\n".join(usage) + "\n")
    print(
        json.dumps(
            dict(
                rows=len(results),
                evidence_validated=certified,
                unresolved_empty=empty,
                output_sha256=digest,
            )
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    write_candidate_report(parser.parse_args().run_dir)
