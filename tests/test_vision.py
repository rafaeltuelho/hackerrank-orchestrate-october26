from ghost_audit.vision import VisualPage, complete_for_audit


def test_deliberate_file_checksum_abbreviation_is_not_missing_identity():
    page = VisualPage(
        complete=False,
        uncertainty=[
            'The panel displays checksum only as "e71b6d..."; the full checksum is not visible.'
        ],
        regions=[],
        records=[],
        is_application_screen=True,
    )
    assert complete_for_audit(page)
    identity_gap = page.model_copy(update={"uncertainty": ["email hash checksum is truncated..."]})
    assert not complete_for_audit(identity_gap)
    owner_gap = page.model_copy(update={"uncertainty": ["Owner email is illegible"]})
    assert not complete_for_audit(owner_gap)


def test_literal_readback_timestamp_normalization_and_no_index_time_substitution():
    from datetime import datetime

    from ghost_audit.vision import explicit_readback_time

    assert explicit_readback_time("Executed: 01 Sep 2026 06:00:14 UTC") == datetime.fromisoformat(
        "2026-09-01T06:00:14Z"
    )
    assert explicit_readback_time("indexed_at: 2026-09-01T05:58:21Z") is None
    assert explicit_readback_time("Created: 01 Sep 2026 06:00:14 UTC") is None
    assert explicit_readback_time("Executed: 2026-09-01T06:00:14Z") == datetime.fromisoformat(
        "2026-09-01T06:00:14Z"
    )


def test_own_document_identifier_does_not_promote_a_referenced_account():
    from ghost_audit.vision import VisualField, VisualRecord, is_own_business_document

    record = VisualRecord(
        resource_id="DOC-77",
        location="header",
        text="Statement DOC-77",
        observed_at=None,
        fields=[VisualField(name="statement", label="Statement", value="DOC-77")],
    )
    assert is_own_business_document(record)
    account = record.model_copy(update={"resource_id": "account_77"})
    assert not is_own_business_document(account)
