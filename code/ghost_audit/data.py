"""Explicit participant CSV loaders and cutoff-aware exact identity history."""

import csv
from datetime import datetime
from pathlib import Path

from .models import AuditError, Contract, Nonempty, Request

ROOT = Path(__file__).resolve().parents[2]


def email_key(value: str) -> str:
    """User-approved ASCII case equivalence; preserve all original values elsewhere."""
    return value.lower() if value.isascii() else value


def timestamp(value: str) -> datetime:
    return Request.aware(datetime.fromisoformat(value))


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if any(None in row or None in row.values() for row in rows):
            raise AuditError("MALFORMED_CSV")
        return rows


def load_requests(path: Path) -> list[Request]:
    requests = [
        Request.model_validate(
            {
                **row,
                **{
                    field: timestamp(row[field])
                    for field in ("requested_at", "reported_at", "audit_at")
                },
            }
        )
        for row in csv_rows(path)
    ]
    if len({r.case_id for r in requests}) != len(requests):
        raise AuditError("DUPLICATE_REQUEST")
    return requests


class Alias(Contract):
    kind: Nonempty
    value: Nonempty
    evidence_id: Nonempty
    available_at: datetime


class Identity(Contract):
    subject_id: Nonempty
    aliases: list[Alias]


class Dataset:
    """Loads a fixed allowlist. Expected outputs and analysis are never opened."""

    def __init__(self, root: Path = ROOT / "dataset"):
        self.root = root.resolve(strict=True)
        self.identities = csv_rows(self.root / "user_identities.csv")
        self.history = csv_rows(self.root / "user_audit_log.csv")
        self.activity = csv_rows(self.root / "system_activity.csv")
        self.rules = csv_rows(self.root / "deletion_rules.csv")
        self.manifest = csv_rows(self.root / "evidence_files.csv")
        self.files = {row["file_id"]: row for row in self.manifest}
        if len(self.files) != len(self.manifest):
            raise AuditError("DUPLICATE_MANIFEST_ID")

    def aliases_at(self, cutoff: datetime) -> dict[str, list[Alias]]:
        aliases: dict[str, list[Alias]] = {}
        for row in self.identities:
            when = timestamp(row["updated_at"])
            if when > cutoff:
                continue
            values = aliases.setdefault(row["user_id"], [])
            for kind in ("user_id", "name", "email", "phone", "email_hash"):
                if row[kind]:
                    values.append(
                        Alias(
                            kind=kind,
                            value=row[kind],
                            evidence_id="identity:" + row["user_id"],
                            available_at=when,
                        )
                    )
        for row in self.history:
            when = timestamp(row["event_time"])
            if when > cutoff:
                continue
            values = aliases.setdefault(row["user_id"], [])
            values.append(
                Alias(
                    kind="user_id",
                    value=row["user_id"],
                    evidence_id=row["audit_id"],
                    available_at=when,
                )
            )
            for key in ("old_value", "new_value"):
                if row[key]:
                    values.append(
                        Alias(
                            kind=row["field_name"],
                            value=row[key],
                            evidence_id=row["audit_id"],
                            available_at=when,
                        )
                    )
        return aliases

    def resolve_identity(self, email: str, cutoff: datetime) -> Identity:
        aliases = self.aliases_at(cutoff)
        matches = [
            subject
            for subject, values in aliases.items()
            if any(a.kind == "email" and email_key(a.value) == email_key(email) for a in values)
        ]
        if len(matches) != 1:
            # Reassignment/shared historical aliases need further evidence; do not merge.
            raise AuditError("UNRESOLVED_IDENTITY" if not matches else "AMBIGUOUS_IDENTITY")
        subject = matches[0]
        values = set_aliases(aliases[subject])
        matching = next(
            a for a in values if a.kind == "email" and email_key(a.value) == email_key(email)
        )
        if not any(a.kind == "email" and a.value == email for a in values):
            values.append(
                Alias(
                    kind="email",
                    value=email,
                    evidence_id="normalized:" + matching.evidence_id,
                    available_at=matching.available_at,
                )
            )
        return Identity(
            subject_id=subject,
            aliases=sorted(
                values,
                key=lambda a: (a.kind, a.value, a.available_at, a.evidence_id),
            ),
        )


def set_aliases(values: list[Alias]) -> list[Alias]:
    return list({(a.kind, a.value, a.evidence_id, a.available_at): a for a in values}.values())
