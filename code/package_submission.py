"""Package a verified final output's runnable source and identical report copies."""

import argparse
import csv
import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path

from ghost_audit.data import ROOT, load_requests
from ghost_audit.models import Result
from ghost_audit.output import HEADER, validate_result


def package(root: Path, destination: Path, *, candidate: bool = False) -> None:
    output = root / "output.csv"
    with output.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != HEADER:
            raise ValueError("invalid output header")
        results = [
            Result.model_validate(
                {
                    "case_id": row["case_id"],
                    "deletion_status": row["deletion_status"],
                    "steps": json.loads(row["steps_json"]),
                }
            )
            for row in reader
        ]
    requests = load_requests(root / "dataset/deletion_requests.csv")
    ids = [r.case_id for r in results]
    if len(ids) != 518 or ids != sorted(r.case_id for r in requests) or len(set(ids)) != 518:
        raise ValueError("output must contain exactly the 518 requested cases in sorted order")
    for result in results:
        validate_result(result, semantic=not candidate)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    reports = [
        root / "code/evaluation" / name for name in ("evaluation_report.md", "usage_report.md")
    ]
    for report in reports:
        if candidate and "Output kind: candidate" not in report.read_text(encoding="utf-8"):
            raise ValueError("candidate packaging requires explicit report labeling")
        if f"Run output SHA-256: {digest}" not in report.read_text(encoding="utf-8"):
            raise ValueError("reports must identify the exact completed final-run output hash")
    sources = [
        root / name for name in ("README.md", "pyproject.toml", "uv.lock", ".python-version")
    ]
    sources += [
        p
        for p in (root / "code").rglob("*")
        if p.is_file() and p.suffix in {".py", ".md"} and "__pycache__" not in p.parts
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=destination.parent, suffix=".zip")
    os.close(fd)
    try:
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(sources):
                archive.write(source, source.relative_to(root).as_posix())
            for report in reports:
                archive.writestr("evaluation/" + report.name, report.read_bytes())
        with zipfile.ZipFile(temp) as archive:
            for report in reports:
                assert archive.read("evaluation/" + report.name) == archive.read(
                    "code/evaluation/" + report.name
                )
        os.replace(temp, destination)
    finally:
        Path(temp).unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "code.zip")
    parser.add_argument(
        "--candidate", action="store_true", help="package explicitly labeled candidates"
    )
    args = parser.parse_args()
    package(ROOT, args.output, candidate=args.candidate)
