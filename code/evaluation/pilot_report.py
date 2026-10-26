"""Append measured live pilot results after freezing local results/diagnostics."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ghost_audit.data import ROOT
from ghost_audit.models import Result

from evaluation.custom_cases import fixtures
from evaluation.main import read_results, score


def accepted(run_dir: Path) -> list[Result]:
    path = run_dir / "results.jsonl"
    if not path.exists():
        return []
    results = [Result.model_validate_json(line) for line in path.read_text().splitlines() if line]
    if len({r.case_id for r in results}) != len(results):
        raise ValueError("run directory contains repeated case results; select a clean frozen run")
    return results


def update(public_run: Path | None, custom_run: Path | None, report: Path):
    lines = [
        "",
        "## Live pilot measurements",
        "",
        "Predictions were generated without expected outputs. Expected answers are opened "
        "only by this evaluator after the run. Public samples are a development/regression "
        "set, not a holdout. Unsupported or failed cases have no fabricated submission row.",
    ]
    if custom_run:
        results = accepted(custom_run)
        expected = [c.expected for c in fixtures()]
        metrics = score(results, expected)
        lines += ["", "### Live authored A01–A03", "", f"Frozen run: `{custom_run}`.", ""]
        lines += [f"- {k}: {v}" for k, v in metrics.items()]
        by_id = {r.case_id: r for r in results}
        lines += ["", "| Case | Expected | Actual | Exact ordered array |", "|---|---|---|---|"]
        for e in expected:
            actual = by_id.get(e.case_id)
            lines.append(
                f"| {e.case_id} | {e.deletion_status} | "
                f"{actual.deletion_status if actual else 'FAILED/UNRESOLVED'} | "
                f"{actual == e} |"
            )
        lines += [
            "",
            "These live cases use independent fictional source logs and the supplied "
            "policy subset, through real SDK triage/audit runs and deterministic validation. "
            "They exercise non-deletion stopping, active-flow control before deletion, "
            "stable tombstone redaction, and retention. The exact expected arrays and "
            "fixture rationale appear in the custom-case tables above.",
        ]
    if public_run:
        summary_path = public_run / "summary.json"
        if not summary_path.exists():
            raise ValueError("public run has not finished; do not score a moving run")
        summary = json.loads(summary_path.read_text())
        ids = set(summary["requested_ids"])
        results = accepted(public_run)
        expected = [r for r in read_results(ROOT / "dataset/sample_output.csv") if r.case_id in ids]
        metrics = score(results, expected)
        lines += [
            "",
            "### Public-sample pilot",
            "",
            f"Frozen run: `{public_run}`.",
            "",
            "Missing/unresolved cases count as incorrect in the status/sequence denominators "
            "and contribute their missing expected steps/fields as errors. These are "
            "whole-pilot scores; scoring only the accepted subset would overstate success.",
            "",
        ]
        lines += [f"- {k}: {v}" for k, v in metrics.items()]
        by_id = {r.case_id: r for r in results}
        failures = {r["case_id"]: r["code"] for r in summary["failures"]}
        lines += [
            "",
            "| Case | Expected | Actual | Exact sequence | Diagnostic |",
            "|---|---|---|---|---|",
        ]
        for e in expected:
            actual = by_id.get(e.case_id)
            lines.append(
                f"| {e.case_id} | {e.deletion_status} | "
                f"{actual.deletion_status if actual else 'UNRESOLVED'} | "
                f"{actual == e} | {failures.get(e.case_id, '')} |"
            )
        lines += [
            "",
            "### Observed failures and improvements",
            "",
            "Development runs found unsupported resource/alias links, mistaken logical "
            "service versus physical-replica names, unrecognized table-location category "
            "evidence, shell-quote parse errors in ordinary log lines, and exhausted tool "
            "budgets. Fixes add exact source receipts, table-scope metadata, narrow "
            "identifier-only tools, bounded evidence-backed repair, and explicit challenge "
            "flow/restore rules. Deliberately abbreviated file-integrity checksums remain "
            "literal and cannot become identity hashes. Genuine capture-cutoff, anonymous "
            "ownership and missing retention-condition gaps remain unresolved; no expected "
            "resource mapping or post-cutoff source was inserted into prediction logic.",
        ]
    original = report.read_text(encoding="utf-8").split("\n## Live pilot measurements", 1)[0]
    report.write_text(original.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-run", type=Path)
    parser.add_argument("--custom-run", type=Path)
    parser.add_argument(
        "--report", type=Path, default=Path(__file__).with_name("evaluation_report.md")
    )
    args = parser.parse_args()
    update(args.public_run, args.custom_run, args.report)
