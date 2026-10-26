import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pytest
from ghost_audit.data import ROOT, Dataset, load_requests
from ghost_audit.evidence import EvidenceStore, exact_match
from ghost_audit.models import AuditError

CUTOFF = datetime.fromisoformat("2026-06-10T12:00:00Z")


def csv_file(path, rows, columns):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


@pytest.fixture
def dataset(tmp_path):
    (tmp_path / "evidence").mkdir()
    files = {
        "user_identities": (
            [
                {
                    "user_id": "u",
                    "name": "Fictional",
                    "email": "new@example.invalid",
                    "phone": "",
                    "email_hash": "hash",
                    "updated_at": "2026-06-01T00:00:00Z",
                }
            ],
            ["user_id", "name", "email", "phone", "email_hash", "updated_at"],
        ),
        "user_audit_log": (
            [
                {
                    "audit_id": "a",
                    "user_id": "u",
                    "field_name": "email",
                    "old_value": "old@example.invalid",
                    "new_value": "new@example.invalid",
                    "event_time": "2026-05-01T00:00:00Z",
                }
            ],
            ["audit_id", "user_id", "field_name", "old_value", "new_value", "event_time"],
        ),
        "system_activity": ([], ["activity_id", "event_time", "details"]),
        "deletion_rules": ([], ["rule_id", "data_category", "condition", "required_action"]),
        "evidence_files": ([], ["file_id", "file_path", "origin", "captured_at"]),
    }
    for name, (rows, columns) in files.items():
        csv_file(tmp_path / (name + ".csv"), rows, columns)
    return Dataset(tmp_path)


def add_file(data, name, content, captured="2026-06-10T11:00:00Z"):
    path = data.root / "evidence" / name
    path.write_text(content)
    data.files[name] = {
        "file_path": "evidence/" + name,
        "captured_at": captured,
        "origin": "fictional_store",
    }
    return name


def test_exact_identifier_boundaries():
    assert exact_match("user_48", '{"user":"user_48"}')
    assert not exact_match("user_48", '"user_480"')
    assert not exact_match("a@example.invalid", "xa@example.invalid")
    assert not exact_match("a@example.invalid", "a@example.invalid.extra")
    assert exact_match("A@example.invalid", "a@example.invalid")
    assert not exact_match("USER_48", "user_48")
    assert not exact_match("a@example.invalid", "éa@example.invalid")
    assert not exact_match("i@example.invalid", "ı@example.invalid")
    assert exact_match("user_48", "The catalog linked this resource to user_48.")
    assert exact_match("a@example.invalid", "Email a@example.invalid.")


def test_identity_history_and_ambiguous_ownership(dataset):
    identity = dataset.resolve_identity("old@example.invalid", CUTOFF)
    assert identity.subject_id == "u"
    assert {a.value for a in identity.aliases if a.kind == "email"} == {
        "old@example.invalid",
        "new@example.invalid",
    }
    dataset.identities.append(
        {**dataset.identities[0], "user_id": "other", "email": "old@example.invalid"}
    )
    with pytest.raises(AuditError, match="AMBIGUOUS_IDENTITY"):
        dataset.resolve_identity("old@example.invalid", CUTOFF)


def test_future_identity_cannot_bridge(dataset):
    with pytest.raises(AuditError, match="UNRESOLVED_IDENTITY"):
        dataset.resolve_identity(
            "new@example.invalid", datetime.fromisoformat("2026-04-01T00:00:00Z")
        )


def test_file_and_observation_cutoff_separate_and_cache_scoped(dataset):
    name = add_file(
        dataset,
        "records.json",
        json.dumps(
            {
                "snapshots": [
                    {"captured_at": "2026-06-10T12:00:00Z", "email": "old@example.invalid"},
                    {"captured_at": "2026-06-10T12:00:01Z", "email": "future@example.invalid"},
                ]
            }
        ),
    )
    store = EvidenceStore(dataset)
    assert len(store.read(name, CUTOFF)) == 1
    later = datetime.fromisoformat("2026-06-10T12:00:01Z")
    assert len(store.read(name, later)) == 2
    dataset.files[name]["captured_at"] = "2026-06-11T00:00:00Z"
    with pytest.raises(AuditError, match="POST_CUTOFF_FILE"):
        store.read(name, CUTOFF)


def test_unknown_time_and_parse_error_not_absence(dataset):
    add_file(dataset, "notes.txt", "unknown time, user_48")
    add_file(dataset, "broken.json", "{")
    store = EvidenceStore(dataset)
    result = store.search(["user_48"], CUTOFF)
    assert result.status == "PARTIAL"
    assert result.fragments[0].observed_at is None
    assert result.errors == ["broken.json:EXTRACTION_ERROR"]
    empty = store.search(["not-present"], CUTOFF)
    assert empty.fragments == [] and empty.status == "PARTIAL"


def test_path_escape_and_symlink(dataset, tmp_path):
    outside = dataset.root / "outside.txt"
    outside.write_text("private")
    dataset.files["escape"] = {"file_path": "outside.txt", "captured_at": CUTOFF.isoformat()}
    with pytest.raises(AuditError, match="MANIFEST_PATH_ESCAPE"):
        EvidenceStore(dataset).read("escape", CUTOFF)
    (dataset.root / "evidence/link.txt").symlink_to(outside)
    dataset.files["link"] = {"file_path": "evidence/link.txt", "captured_at": CUTOFF.isoformat()}
    with pytest.raises(AuditError, match="MANIFEST_PATH_ESCAPE"):
        EvidenceStore(dataset).read("link", CUTOFF)


def test_sql_safe_snapshot_and_external_operations_blocked(dataset):
    name = add_file(
        dataset,
        "snapshot.sql",
        """-- Captured at: 2026-06-10T11:30:00Z
PRAGMA foreign_keys=ON;
CREATE TABLE profiles (id TEXT PRIMARY KEY, updated_at TEXT);
INSERT INTO profiles VALUES ('user_48','2026-06-10T11:00:00Z');""",
    )
    store = EvidenceStore(dataset)
    rows = store.read(name, CUTOFF)
    assert rows[0].locator == "sql:profiles/row:1"
    assert rows[0].observed_at < CUTOFF
    assert rows[0].observed_at.isoformat() == "2026-06-10T11:30:00+00:00"
    for i, script in enumerate(
        [
            "ATTACH DATABASE '/tmp/should-not-exist' AS other;",
            "SELECT load_extension('untrusted');",
            "PRAGMA temp_store_directory='/tmp';",
        ]
    ):
        blocked = add_file(dataset, f"bad{i}.sql", script)
        with pytest.raises(sqlite3.Error):
            store.read(blocked, CUTOFF)


def test_pagination_and_image_gap(dataset):
    add_file(dataset, "a.txt", "user_48\nuser_48\nuser_48")
    add_file(dataset, "image.png", "unreadable-image")
    store = EvidenceStore(dataset)
    r = store.search(["user_48"], CUTOFF, limit=2)
    assert r.total_matches == 3 and r.next_offset == 2
    assert r.visual_pending == ["image.png"]
    assert len(store.search(["user_48"], CUTOFF, offset=2, limit=2).fragments) == 1


def test_ascii_email_case_equivalence_preserves_originals_and_rejects_collision(dataset):
    identity = dataset.resolve_identity("NEW@EXAMPLE.INVALID", CUTOFF)
    assert identity.subject_id == "u"
    assert {"NEW@EXAMPLE.INVALID", "new@example.invalid"} <= {
        a.value for a in identity.aliases if a.kind == "email"
    }
    dataset.identities.append(
        {**dataset.identities[0], "user_id": "other", "email": "NEW@example.invalid"}
    )
    with pytest.raises(AuditError, match="AMBIGUOUS_IDENTITY"):
        dataset.resolve_identity("new@example.invalid", CUTOFF)


def test_real_participant_inputs_and_all_text_extraction():
    dataset = Dataset()
    assert len(load_requests(ROOT / "dataset/deletion_requests.csv")) == 518
    store = EvidenceStore(dataset)
    r = store.search(
        ["nonexistent-fictional-identifier"], datetime.fromisoformat("2026-10-25T00:00:00Z")
    )
    assert r.errors == []
    assert len(r.visual_pending) == 15
    assert len(store._cache) == 83


def test_prediction_source_does_not_import_evaluation():
    for path in (ROOT / "code/ghost_audit").glob("*.py"):
        text = path.read_text()
        assert "from evaluation" not in text
        assert "sample_output.csv" not in text
        assert "public-samples" not in text


def test_real_visual_artifacts_render_serially():
    import io

    from PIL import Image

    store = EvidenceStore(Dataset())
    cutoff = datetime.fromisoformat("2026-10-25T00:00:00Z")
    rendered = 0
    for file_id, row in store.dataset.files.items():
        if Path(row["file_path"]).suffix in {".pdf", ".png"}:
            content = store.read_page_image(file_id, cutoff)
            with Image.open(io.BytesIO(content)) as image:
                assert image.width > 0 and image.height > 0
            rendered += 1
    assert rendered == 15


def test_identity_recovery_requires_explicit_bridge_and_no_future_snapshot(dataset):
    from evaluation.custom_cases import request
    from ghost_audit.identity import resolve_identity

    dataset.identities[0]["updated_at"] = "2026-06-11T00:00:00Z"
    req = request(4, "Delete my account.").model_copy(update={"email": "orphan@example.invalid"})
    add_file(
        dataset,
        "bridge.log",
        "2026-06-10T11:00:00Z service=account_service "
        "customer_reference=u email=orphan@example.invalid",
    )
    identity = resolve_identity(dataset, EvidenceStore(dataset), req)
    assert identity.subject_id == "u"
    assert any(a.kind == "email" and a.value == req.email for a in identity.aliases)
    assert not any(a.kind in {"name", "email_hash"} for a in identity.aliases)


def test_identity_recovery_rejects_cross_file_trace_collision(dataset):
    from evaluation.custom_cases import request
    from ghost_audit.identity import resolve_identity

    req = request(4, "Delete my account.").model_copy(update={"email": "orphan@example.invalid"})
    add_file(
        dataset,
        "lookup.log",
        "2026-06-10T11:00:00Z service=account_service "
        "trace_id=collision event=lookup lookup_key=orphan@example.invalid",
    )
    add_file(
        dataset,
        "other.log",
        "2026-06-10T11:00:00Z service=account_service trace_id=collision customer_reference=u",
    )
    with pytest.raises(AuditError, match="UNRESOLVED_IDENTITY"):
        resolve_identity(dataset, EvidenceStore(dataset), req)


def test_sql_lookup_requires_grounded_schema_and_complete_admissible_rows(dataset):
    schema = "CREATE TABLE records(resource_id TEXT, origin_system TEXT, updated_at TEXT);"
    old = add_file(
        dataset,
        "old.sql",
        "-- Captured at: 2026-06-09T10:00:00Z\n"
        + schema
        + "INSERT INTO records VALUES ('record_1','example_service','2026-06-01T00:00:00Z');",
    )
    new = add_file(dataset, "new.sql", "-- Captured at: 2026-06-10T10:00:00Z\n" + schema)
    store = EvidenceStore(dataset)
    references = store.read(old, CUTOFF)
    receipt = store.lookup_sql(new, "records", "record_1", CUTOFF, references)[0]
    assert receipt.extracted_fields["rows"] == "0"
    assert receipt.extracted_fields["service"] == "example_service"
    assert receipt.observed_at.isoformat() == "2026-06-10T10:00:00+00:00"
    with pytest.raises(AuditError, match="SAME_SCHEMA"):
        store.lookup_sql(new, "records", "unseen", CUTOFF, references)
    with pytest.raises(AuditError, match="SAME_SCHEMA"):
        store.lookup_sql(new, "records", "record_1", CUTOFF, [])
    future = add_file(
        dataset,
        "future.sql",
        "-- Captured at: 2026-06-10T10:00:00Z\n"
        + schema
        + "INSERT INTO records VALUES ('record_1','example_service','2026-06-11T00:00:00Z');",
    )
    assert len(store.read(future, CUTOFF)) == 1  # scope only; future row inadmissible
    with pytest.raises(AuditError, match="INADMISSIBLE_ROWS"):
        store.lookup_sql(future, "records", "record_1", CUTOFF, references)


def test_sql_lookup_preserves_positive_rows_and_requires_explicit_snapshot(dataset):
    schema = "CREATE TABLE records(resource_id TEXT, origin_system TEXT);"
    name = add_file(
        dataset,
        "positive.sql",
        "-- Captured at: 2026-06-10T10:00:00Z\n"
        + schema
        + "INSERT INTO records VALUES ('record_1','example_service');",
    )
    store = EvidenceStore(dataset)
    refs = store.read(name, CUTOFF)
    assert store.lookup_sql(name, "records", "record_1", CUTOFF, refs) == refs[:1]
    undated = add_file(dataset, "undated.sql", schema)
    with pytest.raises(AuditError, match="SNAPSHOT_TIME_UNKNOWN"):
        store.lookup_sql(undated, "records", "record_1", CUTOFF, refs)
