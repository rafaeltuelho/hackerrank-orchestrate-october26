"""Report real local development usage separately from the pending final run."""

import json
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ghost_audit.budget import Budget
from ghost_audit.config import APPROVED_BUDGET_USD
from ghost_audit.data import ROOT


def development_usage(root: Path) -> list[dict]:
    paths = list((root / "runs").glob("**/usage.jsonl"))
    paths += list((root / "runs").glob("pilot-usage.jsonl"))
    records = []
    for path in sorted(set(paths)):
        records.extend(json.loads(line) for line in path.read_text().splitlines() if line)
    return records


def write_report(root: Path = ROOT) -> None:
    records = development_usage(root)
    grouped = defaultdict(lambda: {"requests": 0, "input": 0, "output": 0, "unknown": 0})
    for record in records:
        row = grouped[(record["model"], record["stage"])]
        row["requests"] += record["requests"]
        row["input"] += record["input_tokens"] or 0
        row["output"] += record["output_tokens"] or 0
        row["unknown"] += record["requests"] if record["input_tokens"] is None else 0
    budget = Budget(root / "runs/budget.jsonl", APPROVED_BUDGET_USD)
    lines = [
        "# Usage report",
        "",
        "## Final full-dataset run",
        "",
        "Not completed. No final 518-row output.csv exists. The development measurements "
        "below are not a substitute for final-run usage/cost.",
        "",
        "## Measured development pilots",
        "",
        "Provider: OpenAI. Model: gpt-6.1-sol. Reasoning: triage low; audit and visual "
        "interpretation medium. Standard Responses API; remote tracing disabled. "
        "SDK and HTTP automatic retries disabled. Any audit-repair calls are explicit "
        "and included below. Offline fake-model tests are excluded.",
        "",
        "| Model | Stage | Requests | Known input tokens | Known output tokens | "
        "Unknown-usage requests |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for (model, stage), row in sorted(grouped.items()):
        lines.append(
            f"| {model} | {stage} | {row['requests']} | {row['input']} | "
            f"{row['output']} | {row['unknown']} |"
        )
    totals = {
        key: sum(r[key] for r in grouped.values())
        for key in ("requests", "input", "output", "unknown")
    }
    lines += [
        f"| Overall | All development | {totals['requests']} | {totals['input']} | "
        f"{totals['output']} | {totals['unknown']} |",
        "",
    ]
    estimate = (Decimal(totals["input"]) * 2 + Decimal(totals["output"]) * 10) / Decimal(1000000)
    lines += [
        f"Known total tokens: {totals['input'] + totals['output']}.",
        "",
        f"Known-token Standard uncached baseline estimate: USD {estimate:.6f}. "
        "This estimate excludes cache discounts/write premiums, regional premiums and "
        "unreported tokens; it is not an invoice or complete cost.",
        "",
        f"Conservative settled cost allowance: USD {sum(budget.charges.values()):.6f}.",
        f"Outstanding/unknown request reservations: USD {sum(budget.pending.values()):.6f}.",
        f"Total budget committed (including reservations): USD {budget.committed:.6f} "
        f"of USD {budget.ceiling:.2f}.",
        "",
        "Budget prices allow short-context input/cache writes up to $5/M and output "
        "$10/M; long-context input/cache writes up to $10/M and output $15/M, plus "
        "a conservative 10% regional premium. Official Standard base rates are $2/M "
        "input and $10/M output. Prices verified 2026-10-25 at "
        "[OpenAI pricing](https://developers.openai.com/api/docs/pricing). "
        "Requests reserve before sending; failures/crashes keep their full reservation. "
        "The single persistent budget is shared by all pilot, vision, audit and final calls.",
        "",
        "Visual extraction is cached by source image/model/prompt hash. Cache hits "
        "make no model call. Development shared-extraction calls appear under vision; "
        "the final report must state reuse and any allocated shared preparation costs. "
        "Local evidence tools are not model requests. SDK aggregate usage is not added "
        "again. Unknown usage stays unknown, not zero.",
        "",
        "Final averages per evaluation request, per-model totals and total/per-request "
        "final cost remain unavailable until the successful 518-case run. Credentials "
        "and sensitive configuration are never included in this report.",
    ]
    (root / "code/evaluation/usage_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_report()
