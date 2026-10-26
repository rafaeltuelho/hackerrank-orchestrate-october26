import hashlib
import zipfile

import pytest
from evaluation.custom_input import write_csv as fixture_csv
from ghost_audit.models import Result
from ghost_audit.output import write_csv
from package_submission import package


@pytest.mark.parametrize("candidate", [False, True])
def test_archive_contents_and_report_identity(tmp_path, candidate):
    root = tmp_path / "project"
    (root / "dataset").mkdir(parents=True)
    (root / "code/evaluation").mkdir(parents=True)
    requests = [
        {
            "case_id": f"fixture_{i:03}",
            "email": "fixture@example.invalid",
            "requested_at": "2026-06-10T10:00:00Z",
            "reported_status": "COMPLETE",
            "reported_at": "2026-06-10T11:00:00Z",
            "audit_at": "2026-06-10T12:00:00Z",
            "request_text": "Do not delete.",
        }
        for i in range(518)
    ]
    fixture_csv(root / "dataset/deletion_requests.csv", requests, list(requests[0]))
    ids = [r["case_id"] for r in requests]
    write_csv(
        root / "output.csv",
        [
            Result(
                case_id=i, deletion_status="INCOMPLETE" if candidate else "NOT_APPLICABLE", steps=[]
            )
            for i in ids
        ],
        ids,
        semantic=not candidate,
    )
    digest = hashlib.sha256((root / "output.csv").read_bytes()).hexdigest()
    for name in ("evaluation_report.md", "usage_report.md"):
        (root / "code/evaluation" / name).write_text(
            f"Run output SHA-256: {digest}\n" + ("Output kind: candidate\n" if candidate else "")
        )
    for name in ("README.md", "pyproject.toml", "uv.lock", ".python-version"):
        (root / name).write_text("fixture")
    (root / ".env").write_text("NOT_A_REAL_SECRET=excluded")
    (root / "code/main.py").write_text("print('fixture')")
    (root / "code/nested.zip").write_text("excluded")
    (root / "log.txt").write_text("separate")
    destination = tmp_path / "code.zip"
    package(root, destination, candidate=candidate)
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
        assert ".env" not in names and "log.txt" not in names and "output.csv" not in names
        assert not any(name.startswith("dataset/") or name.endswith(".zip") for name in names)
        for name in ("evaluation_report.md", "usage_report.md"):
            assert archive.read("evaluation/" + name) == archive.read("code/evaluation/" + name)
    (root / "code/evaluation/usage_report.md").write_text("Not yet measured")
    before = destination.read_bytes()
    with pytest.raises(ValueError, match="exact completed final-run|explicit report labeling"):
        package(root, destination, candidate=candidate)
    assert before == destination.read_bytes()
