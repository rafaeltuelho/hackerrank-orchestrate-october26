from datetime import datetime
from types import SimpleNamespace

from evaluation.custom_cases import request
from ghost_audit.data import Alias, Identity
from ghost_audit.evidence import Fragment
from ghost_audit.resource_links import matches_resource, resource_aliases


def test_catalog_document_alias_is_subject_scoped_cutoff_scoped_and_not_state_proof():
    req = request(2, "Delete my records.")
    identity = Identity(
        subject_id="u",
        aliases=[
            Alias(
                kind="user_id",
                value="u",
                evidence_id="a",
                available_at=datetime.fromisoformat("2026-06-01T00:00:00Z"),
            )
        ],
    )
    row = {
        "event_type": "LINK_RESOURCE_IDENTITY",
        "event_time": "2026-06-10T11:00:00Z",
        "resource_id": "logical_record",
        "details": "Linked logical_record (DOC-77) to u.",
        "activity_id": "activity_1",
        "target_system": "service",
    }
    aliases = resource_aliases(SimpleNamespace(activity=[row]), req, identity)
    fragment = Fragment("e", "page:1", req.requested_at, None, "Statement: DOC-77")
    assert matches_resource("logical_record", fragment, aliases)
    assert aliases["logical_record"][0]["activity_id"] == "activity_1"
    future = {**row, "event_time": "2026-06-11T00:00:00Z"}
    assert resource_aliases(SimpleNamespace(activity=[future]), req, identity) == {}
    other = {**row, "details": "Linked logical_record (DOC-77) to unrelated_user."}
    assert resource_aliases(SimpleNamespace(activity=[other]), req, identity) == {}
    collision = {
        **row,
        "resource_id": "second_record",
        "details": "Linked second_record (DOC-77) to u.",
    }
    ambiguous = resource_aliases(SimpleNamespace(activity=[row, collision]), req, identity)
    assert not matches_resource("logical_record", fragment, ambiguous)
