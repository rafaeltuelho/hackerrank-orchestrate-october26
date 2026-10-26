"""Materialize independent fictional A01–A03 source facts for live evaluation."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.custom_cases import fixtures


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def create(root: Path):
    root.mkdir(parents=True, exist_ok=False)
    (root / "evidence").mkdir()
    cases = fixtures()
    requests = [c.request.model_dump(mode="json") for c in cases]
    write_csv(root / "deletion_requests.csv", requests, list(requests[0]))
    identities = [
        {
            "user_id": f"custom_user_{n:02}",
            "name": f"Fictional Fixture {n}",
            "email": f"sample{n:02}@example.invalid",
            "phone": "",
            "email_hash": "",
            "updated_at": "2026-06-10T10:00:00Z",
        }
        for n in (2, 3)
    ]
    write_csv(root / "user_identities.csv", identities, list(identities[0]))
    write_csv(
        root / "user_audit_log.csv",
        [],
        ["audit_id", "user_id", "event_time", "field_name", "old_value", "new_value"],
    )
    write_csv(
        root / "system_activity.csv",
        [],
        [
            "activity_id",
            "event_time",
            "event_type",
            "source_system",
            "target_system",
            "resource_id",
            "reported_result",
            "details",
        ],
    )
    rules = [
        {
            "rule_id": "rule_01",
            "data_category": "USER_PROFILE",
            "condition": "Always",
            "required_action": "DELETE",
        },
        {
            "rule_id": "rule_03",
            "data_category": "SEARCH_INDEX_ENTRY",
            "condition": "Always",
            "required_action": "DELETE",
        },
        {
            "rule_id": "rule_12",
            "data_category": "SECURITY_AUDIT_LOG",
            "condition": "Record is within the supplied retention period",
            "required_action": "RETAIN",
        },
        {
            "rule_id": "rule_15",
            "data_category": "ACCOUNT_TOMBSTONE",
            "condition": "Account is deleted and only a stable internal user_id is needed to "
            "preserve references to retained records",
            "required_action": "REDACT",
        },
    ]
    write_csv(root / "deletion_rules.csv", rules, list(rules[0]))
    content = {
        "custom_e02": "\n".join(
            [
                "2026-06-10T11:45:00Z service=search_service event=index_query_completed "
                "resource_id=search_custom02 result=hit total_hits=1 "
                "email=sample02@example.invalid "
                "customer_reference=custom_user_02",
                "2026-06-10T11:46:00Z service=integration_service "
                "event=connector_config_read_completed "
                "resource_id=flow_custom02 enabled=true customer_reference=custom_user_02",
            ]
        ),
        "custom_e03": "\n".join(
            [
                "2026-06-10T11:45:00Z service=account_service event=profile_lookup_completed "
                "resource_id=account_custom03 rows=0 http_status=404 "
                "lookup_key=sample03@example.invalid",
                "2026-06-10T11:46:00Z service=identity_service event=tombstone_read_completed "
                "resource_id=tombstone_custom03 account_status=DELETED "
                "subject_reference=custom_user_03 "
                "name=null email=null phone=null email_hash=null "
                "retained_record_refs=audit_custom03 "
                "reference_purpose=retained_records_only",
                "2026-06-10T11:47:00Z service=security_service event=audit_record_read_completed "
                "resource_id=audit_custom03 rows=1 subject_reference=custom_user_03 "
                "retention_until=2030-12-31T23:59:59Z",
            ]
        ),
    }
    manifest = []
    for evidence_id, text in content.items():
        path = "evidence/" + evidence_id + ".log"
        (root / path).write_text(text + "\n", encoding="utf-8")
        manifest.append(
            {
                "file_id": evidence_id,
                "file_path": path,
                "origin": "authored_fixture",
                "captured_at": "2026-06-10T11:50:00Z"
                if evidence_id.endswith("02")
                else "2026-06-10T11:55:00Z",
            }
        )
    write_csv(root / "evidence_files.csv", manifest, list(manifest[0]))


if __name__ == "__main__":
    create(Path(sys.argv[1]))
