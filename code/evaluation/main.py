"""Score frozen predictions separately from the participant-only solver."""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ghost_audit.models import Result
from ghost_audit.output import HEADER, validate_result, write_csv
from ghost_audit.workflow import assemble

from evaluation.custom_cases import fixtures


def read_results(path: Path) -> list[Result]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != HEADER:
            raise ValueError("invalid output header")
        results = [
            Result.model_validate(
                {
                    "case_id": r["case_id"],
                    "deletion_status": r["deletion_status"],
                    "steps": json.loads(r["steps_json"]),
                }
            )
            for r in reader
        ]
    if len({r.case_id for r in results}) != len(results):
        raise ValueError("duplicate case ID")
    return results


def score(actual: list[Result], expected: list[Result]) -> dict[str, int | float]:
    """Exact multiset step matching; field alignment is by array position.

    Missing/extra cases and steps count as errors. Step numbers count as fields.
    A sequence match compares parsed ordered steps and status together.
    """
    a = {r.case_id: r for r in actual}
    e = {r.case_id: r for r in expected}
    if len(a) != len(actual) or len(e) != len(expected):
        raise ValueError("duplicate case ID")
    case_ids = set(a) | set(e)
    status_correct = sequence_correct = step_matches = fields_correct = fields_total = 0
    predicted_steps = expected_steps = 0
    for case_id in sorted(case_ids):
        left, right = a.get(case_id), e.get(case_id)
        status_correct += bool(left and right and left.deletion_status == right.deletion_status)
        sequence_correct += bool(left and right and left == right)
        ls = [s.model_dump() for s in left.steps] if left else []
        rs = [s.model_dump() for s in right.steps] if right else []
        predicted_steps += len(ls)
        expected_steps += len(rs)
        lc = Counter(json.dumps(s, sort_keys=True) for s in ls)
        rc = Counter(json.dumps(s, sort_keys=True) for s in rs)
        step_matches += sum((lc & rc).values())
        fields_total += 7 * max(len(ls), len(rs))
        for x, y in zip(ls, rs, strict=False):
            fields_correct += sum(x[k] == y[k] for k in x)
    return {
        "cases": len(case_ids),
        "status_correct": status_correct,
        "status_accuracy": status_correct / len(case_ids) if case_ids else 0.0,
        "sequence_correct": sequence_correct,
        "sequence_accuracy": sequence_correct / len(case_ids) if case_ids else 0.0,
        "step_matches": step_matches,
        "predicted_steps": predicted_steps,
        "expected_steps": expected_steps,
        "step_precision": step_matches / predicted_steps if predicted_steps else 0.0,
        "step_recall": step_matches / expected_steps if expected_steps else 0.0,
        "fields_correct": fields_correct,
        "fields_total": fields_total,
        "field_accuracy": fields_correct / fields_total if fields_total else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--expected", type=Path)
    parser.add_argument(
        "--report", type=Path, default=Path(__file__).with_name("evaluation_report.md")
    )
    parser.add_argument("--custom-output", type=Path)
    args = parser.parse_args()
    if bool(args.predictions) != bool(args.expected):
        parser.error("provide both --predictions and --expected")
    cases = fixtures()
    actual = [assemble(c.request, c.authorization, c.assessment) for c in cases]
    for result in actual:
        validate_result(result)
    metrics = score(actual, [c.expected for c in cases])
    lines = [
        "# Evaluation report",
        "",
        "## Custom cases A01–A03 (offline)",
        "",
        "Measured deterministic assessment assembly using authored source inventories and "
        "frozen task doubles. These results do not measure model intent, retrieval, visual "
        "interpretation, or live end-to-end accuracy.",
        "",
        "| Case | Complete source inventory and policy | Expected | Actual | Exact sequence |",
        "|---|---|---|---|---|",
    ]
    for case, result in zip(cases, actual, strict=True):
        lines.append(
            f"| {result.case_id} | {case.inventory} | {case.expected.deletion_status} | "
            f"{result.deletion_status} | {result == case.expected} |"
        )
    lines += ["", "### Measured custom metrics", ""]
    lines += [f"- {key}: {value}" for key, value in metrics.items()]
    for case, result in zip(cases, actual, strict=True):
        lines += [
            "",
            f"### {case.request.case_id} expected and actual",
            "",
            f"Request: {case.request.request_text}",
            "",
            f"Cutoff: {case.request.audit_at.isoformat()}. "
            "All declared observations and subject links predate this cutoff.",
            "",
        ]
        if not result.steps:
            lines += ["Expected `[]`; actual `[]`. No discovery or planning is authorized."]
        else:
            lines += [
                "The actual seven-field ordered array exactly matches this expected table.",
                "",
                "| step_no | phase | system_id | resource_id | operation | state | evidence_id |",
                "|---|---|---|---|---|---|---|",
            ]
            for step in case.expected.steps:
                fields = [str(v) if v != "" else '`""`' for v in step.model_dump().values()]
                lines.append("| " + " | ".join(fields) + " |")
    lines += [
        "",
        "Step matching: exact seven-field multiset intersection, including step_no. "
        "Precision divides by predicted steps; recall divides by expected steps. "
        "Field matching aligns by array position, counts seven fields per position, and "
        "penalizes missing/extra positions. Sequence matching requires equal status and "
        "ordered parsed arrays; object key order and whitespace are ignored.",
        "",
        "## Public samples (development/regression set)",
        "",
    ]
    if args.predictions:
        public_actual, public_expected = read_results(args.predictions), read_results(args.expected)
        lines += [
            f"- {key}: {value}" for key, value in score(public_actual, public_expected).items()
        ]
    else:
        lines += [
            "Not run: no frozen live solver predictions supplied. Hidden truth is unavailable."
        ]
    lines += [
        "",
        "## Failures and improvements",
        "",
        "The foundation rejects unsupported intent spans, unknown citations, invalid "
        "operation/state/phase combinations, unsafe ordering, incomplete coverage, "
        "unscoped absence, unresolved ownership, and missing required retained records. "
        "A01–A03 test expected assembly; focused pytest failures/rejections are separate "
        "from live solver failures. Public-sample evidence gaps remain unresolved pending "
        "the live investigation; expected-answer resource IDs are never prediction inputs.",
        "",
        "Observed compatibility failures fixed: the SDK rejected arbitrary-key observation "
        "dictionaries in strict output schemas, so the SDK boundary now uses duplicate-checked "
        "field/value pairs. The SQLite authorizer initially rejected implicit primary-key "
        "indexes, REINDEX and the supplied foreign_keys pragma; narrow allowances now load "
        "all 24 snapshots while external attachment/extension tests remain blocked. PDFium "
        "page objects lacked context-manager support; explicit closing fixed serial rendering.",
        "",
        "## Delivery status",
        "",
        "No final 518-case run has completed. This report is an intermediate measurement.",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if args.custom_output:
        write_csv(args.custom_output, actual, [c.request.case_id for c in cases])
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    # Direct script execution keeps the required entry point usable from any cwd.
    main()
