"""Read-only participant artifact extraction, exact retrieval and provenance.

Extraction returns candidates, never absence/state conclusions. Undated content stays
undated. A successful empty search is distinct from extraction failure and visual gaps.
"""

import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from .data import Dataset, timestamp
from .models import AuditError

OBSERVATION_KEYS = {
    "captured_at",
    "observed_at",
    "snapshot_at",
    "event_time",
    "updated_at",
    "timestamp",
}


@dataclass(frozen=True)
class Fragment:
    evidence_id: str
    locator: str
    captured_at: datetime
    observed_at: datetime | None
    text: str
    extracted_fields: dict[str, str | None] | None = None
    effective_at: datetime | None = None


def pipe_values(text: str) -> dict[str, str]:
    parts = text.removeprefix("- ").split(" | ")
    if len(parts) != 6 or not re.fullmatch(r"\d{4}-\d\d-\d\dT\S+", parts[0]):
        return {}
    return dict(
        zip(
            (
                "observed_at",
                "service",
                "resource_id",
                "data_category",
                "handover_state",
                "lookup_key",
            ),
            parts,
            strict=True,
        )
    )


@dataclass
class SearchResult:
    status: str
    fragments: list[Fragment]
    errors: list[str]
    visual_pending: list[str]
    next_offset: int | None
    total_matches: int


def exact_match(value: str, content: str) -> bool:
    # Preserve literal punctuation/case. Full email and identifier token boundaries
    # prevent user_48/user_480 and someone@example.invalid/xsomeone@example.invalid.
    if not value:
        raise ValueError("empty search identifier")
    # Most corpus/identifier pairs are negative. Avoid compiling/escaping a regex
    # for those pairs, especially in broad but bounded graph expansion.
    if "@" in value and value.isascii():
        if value.lower() not in content.lower():
            return False
    elif value not in content:
        return False
    literal = re.escape(value)
    if "@" in value and value.isascii():
        literal = "(?ai:" + literal + ")"
        return bool(re.search(r"(?<![\w@.+-])" + literal + r"(?![\w@+-]|\.\w)", content))
    # A sentence-ending period is punctuation, not an extension of a stable ID/hash.
    return bool(re.search(r"(?<![\w@+-])" + literal + r"(?![\w@+-])", content))


class EvidenceStore:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset
        self._cache: dict[str, tuple[int, int, list[Fragment]]] = {}
        self.visual_fragments: dict[str, list[Fragment]] = {}

    def path(self, file_id: str, cutoff: datetime) -> tuple[Path, datetime]:
        row = self.dataset.files.get(file_id)
        if row is None:
            raise AuditError("UNKNOWN_FILE_ID")
        captured = timestamp(row["captured_at"])
        if captured > cutoff:
            raise AuditError("POST_CUTOFF_FILE")
        path = (self.dataset.root / row["file_path"]).resolve(strict=True)
        if not path.is_relative_to(self.dataset.root / "evidence"):
            raise AuditError("MANIFEST_PATH_ESCAPE")
        return path, captured

    def read(self, file_id: str, cutoff: datetime) -> list[Fragment]:
        if file_id.startswith(("activity_", "audit_")):
            rows = (
                self.dataset.activity if file_id.startswith("activity_") else self.dataset.history
            )
            key = "activity_id" if file_id.startswith("activity_") else "audit_id"
            matching = [r for r in rows if r[key] == file_id]
            if len(matching) != 1:
                raise AuditError("UNKNOWN_ROW_ID")
            row = matching[0]
            when = timestamp(row["event_time"])
            if when > cutoff:
                raise AuditError("POST_CUTOFF_ROW")
            return [
                Fragment(
                    file_id,
                    "csv:system_activity" if key == "activity_id" else "csv:user_audit_log",
                    when,
                    when,
                    json.dumps(row, ensure_ascii=False, sort_keys=True),
                )
            ]
        path, captured = self.path(file_id, cutoff)
        stat = path.stat()
        cached = self._cache.get(file_id)
        if cached and cached[:2] == (stat.st_mtime_ns, stat.st_size):
            fragments = cached[2]
        else:
            fragments = self._extract(file_id, path, captured)
            self._cache[file_id] = (stat.st_mtime_ns, stat.st_size, fragments)
        return [
            f
            for f in fragments
            if (f.observed_at is None or f.observed_at <= cutoff)
            and (f.effective_at is None or f.effective_at <= cutoff)
        ]

    def _extract(self, file_id: str, path: Path, captured: datetime) -> list[Fragment]:
        suffix = path.suffix.lower()
        if suffix == ".png":
            if file_id in self.visual_fragments:
                return self.visual_fragments[file_id]
            raise AuditError("VISUAL_INTERPRETATION_REQUIRED")
        if suffix == ".pdf":
            from pypdf import PdfReader

            return [
                Fragment(file_id, f"page:{i}", captured, None, page.extract_text() or "")
                for i, page in enumerate(PdfReader(path).pages, 1)
            ] + self.visual_fragments.get(file_id, [])
        text = path.read_text(encoding="utf-8")
        if suffix == ".json":
            return self._json_fragments(file_id, json.loads(text), captured)
        if suffix == ".sql":
            return self._sql_fragments(file_id, text, captured)
        if suffix not in {".log", ".txt"}:
            raise AuditError("UNSUPPORTED_ARTIFACT")
        fragments = []
        for n, line in enumerate(text.splitlines(), 1):
            match = re.match(r"(?:- )?(\d{4}-\d{2}-\d{2}T\S+)", line)
            observed = timestamp(match[1]) if match else None
            fragments.append(
                Fragment(file_id, f"line:{n}", captured, observed, line, pipe_values(line) or None)
            )
        return fragments

    def _json_fragments(
        self,
        file_id: str,
        node,
        captured: datetime,
        pointer: str = "",
        inherited: datetime | None = None,
        context: dict | None = None,
    ) -> list[Fragment]:
        output = []
        if isinstance(node, dict):
            times = [
                timestamp(v)
                for k, v in node.items()
                if k in OBSERVATION_KEYS and isinstance(v, str)
            ]
            observed = max([*times, *([inherited] if inherited else [])], default=None)
            # Carry source-system/collection metadata, never neighboring row identities.
            metadata = {
                **(context or {}),
                **{
                    k: v
                    for k, v in node.items()
                    if k in {"data_store", "collection", "source", "origin_system"}
                    and not isinstance(v, (dict, list))
                },
            }
            if isinstance(node.get("resource_id"), str):
                metadata["parent_resource_id"] = node["resource_id"]
            # Each object gets its scalar fields; nested child objects get independent locators.
            scalars = {k: v for k, v in node.items() if not isinstance(v, (dict, list))}
            if scalars:
                output.append(
                    Fragment(
                        file_id,
                        "json:" + (pointer or "/"),
                        captured,
                        observed,
                        json.dumps(
                            {"context": metadata, "fields": scalars},
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                    )
                )
            for key, child in node.items():
                if isinstance(child, (dict, list)):
                    escaped = key.replace("~", "~0").replace("/", "~1")
                    output.extend(
                        self._json_fragments(
                            file_id, child, captured, f"{pointer}/{escaped}", observed, metadata
                        )
                    )
        elif isinstance(node, list):
            for i, child in enumerate(node):
                if isinstance(child, (dict, list)):
                    output.extend(
                        self._json_fragments(
                            file_id, child, captured, f"{pointer}/{i}", inherited, context
                        )
                    )
                else:
                    output.append(
                        Fragment(
                            file_id,
                            f"json:{pointer}/{i}",
                            captured,
                            inherited,
                            json.dumps(child, ensure_ascii=False),
                        )
                    )
        return output

    @staticmethod
    def _sql_fragments(file_id: str, script: str, captured: datetime) -> list[Fragment]:
        allowed = {
            sqlite3.SQLITE_CREATE_INDEX,
            sqlite3.SQLITE_REINDEX,
            sqlite3.SQLITE_CREATE_TABLE,
            sqlite3.SQLITE_INSERT,
            sqlite3.SQLITE_SELECT,
            sqlite3.SQLITE_READ,
            sqlite3.SQLITE_UPDATE,
            sqlite3.SQLITE_TRANSACTION,
            sqlite3.SQLITE_FUNCTION,
        }
        conn = sqlite3.connect(":memory:")
        conn.enable_load_extension(False)
        steps = 0

        def authorize(action, arg1, arg2, database, trigger):
            if action == sqlite3.SQLITE_PRAGMA:
                return (
                    sqlite3.SQLITE_OK
                    if arg1 == "foreign_keys" and arg2 in {"ON", "1"}
                    else sqlite3.SQLITE_DENY
                )
            if action == sqlite3.SQLITE_FUNCTION and (arg2 or "").lower() == "load_extension":
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_UPDATE and arg1 != "sqlite_master":
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

        def bounded():
            nonlocal steps
            steps += 1
            return steps > 100000

        conn.set_authorizer(authorize)
        conn.set_progress_handler(bounded, 1000)
        try:
            conn.executescript(script)
            # No agent-provided SQL is accepted; enumerate and quote table names locally.
            tables = [
                r[0]
                for r in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
            ]
            snapshot_time = None
            header = re.search(r"--\s*Captured at:\s*(\S+)", script)
            if header:
                snapshot_time = timestamp(header[1])
            elif "snapshot_scope" in tables:
                scopes = {
                    timestamp(r[0]) for r in conn.execute("SELECT captured_at FROM snapshot_scope")
                }
                if len(scopes) == 1:
                    snapshot_time = next(iter(scopes))
            output = []
            for table in tables:
                quoted = '"' + table.replace('"', '""') + '"'
                cursor = conn.execute(f"SELECT * FROM {quoted}")
                columns = [c[0] for c in cursor.description]
                row_count = 0
                for index, values in enumerate(cursor, 1):
                    row_count += 1
                    row = dict(zip(columns, values, strict=True))
                    times = [
                        timestamp(v)
                        for k, v in row.items()
                        if k in OBSERVATION_KEYS and isinstance(v, str)
                    ]
                    output.append(
                        Fragment(
                            file_id,
                            f"sql:{table}/row:{index}",
                            captured,
                            snapshot_time,
                            json.dumps(row, ensure_ascii=False, sort_keys=True),
                            None,
                            max(times) if times else None,
                        )
                    )
                output.append(
                    Fragment(
                        file_id,
                        f"sql:{table}/scope",
                        captured,
                        snapshot_time,
                        json.dumps(
                            {
                                "table": table,
                                "row_count": row_count,
                                "columns": columns,
                                "scope": "complete supplied SQL table export; "
                                "no assertion about unexported databases",
                            }
                        ),
                    )
                )
            return output
        finally:
            conn.close()

    def lookup_sql(
        self,
        file_id: str,
        table: str,
        resource_id: str,
        cutoff: datetime,
        references: list[Fragment],
    ) -> list[Fragment]:
        """Exact ID lookup in a complete exported table of a previously observed schema."""
        if file_id not in self.dataset.files:
            raise AuditError("UNKNOWN_FILE_ID")
        if not self.dataset.files[file_id]["file_path"].endswith(".sql"):
            raise AuditError("SQL_ARTIFACT_REQUIRED")
        fragments = self.read(file_id, cutoff)
        scope = next((f for f in fragments if f.locator == f"sql:{table}/scope"), None)
        if scope is None or scope.observed_at is None:
            raise AuditError("SQL_SCOPE_OR_SNAPSHOT_TIME_UNKNOWN")
        columns = json.loads(scope.text)["columns"]
        rows = [f for f in fragments if f.locator.startswith(f"sql:{table}/row:")]
        if len(rows) != json.loads(scope.text)["row_count"]:
            raise AuditError("SQL_SCOPE_HAS_INADMISSIBLE_ROWS")
        if "resource_id" not in columns:
            raise AuditError("SQL_RESOURCE_COLUMN_REQUIRED")
        reference = None
        service = None
        for f in references:
            origin = self.dataset.files[file_id].get("origin")
            reference_origin = self.dataset.files.get(f.evidence_id, {}).get("origin")
            if not origin or reference_origin != origin:
                continue
            if not f.locator.startswith("sql:") or "/row:" not in f.locator:
                continue
            if f.locator.split("/row:")[0] != f"sql:{table}":
                continue
            row = json.loads(f.text)
            if row.get("resource_id") != resource_id or sorted(row) != sorted(columns):
                continue
            service = row.get("origin_system")
            if service:
                reference = f
                break
        if reference is None:
            raise AuditError("SQL_LOOKUP_REQUIRES_SAME_SCHEMA_RESOURCE_REFERENCE")
        hits = [
            f
            for f in fragments
            if f.locator.startswith(f"sql:{table}/row:")
            and json.loads(f.text).get("resource_id") == resource_id
        ]
        if hits:
            return hits
        fields = {
            "service": service,
            "resource_id": resource_id,
            "event": "scoped_sql_lookup_completed",
            "rows": "0",
            "scope_complete": "true",
        }
        return [
            Fragment(
                file_id,
                f"sql:{table}/lookup:{resource_id}",
                scope.captured_at,
                scope.observed_at,
                json.dumps(fields),
                fields,
            )
        ]

    def search(
        self, identifiers: list[str], cutoff: datetime, offset: int = 0, limit: int = 40
    ) -> SearchResult:
        if (
            not identifiers
            or any(not v for v in identifiers)
            or offset < 0
            or not 1 <= limit <= 100
        ):
            raise ValueError("invalid search bounds")
        matches, errors, visual_pending = [], [], []
        for file_id, row in sorted(self.dataset.files.items()):
            if timestamp(row["captured_at"]) > cutoff:
                continue
            try:
                fragments = self.read(file_id, cutoff)
                matches.extend(
                    f for f in fragments if any(exact_match(v, f.text) for v in identifiers)
                )
                if row["file_path"].endswith(".pdf") and file_id not in self.visual_fragments:
                    # Text search does not establish absence in visual content.
                    visual_pending.append(file_id)
            except AuditError as exc:
                if str(exc) == "VISUAL_INTERPRETATION_REQUIRED":
                    visual_pending.append(file_id)
                else:
                    errors.append(f"{file_id}:{type(exc).__name__}")
            except OSError, ValueError, sqlite3.Error:
                errors.append(f"{file_id}:EXTRACTION_ERROR")
        for row in self.dataset.activity:
            when = timestamp(row["event_time"])
            text = json.dumps(row, ensure_ascii=False, sort_keys=True)
            if when <= cutoff and any(exact_match(v, text) for v in identifiers):
                matches.append(
                    Fragment(row["activity_id"], "csv:system_activity", when, when, text)
                )
        next_offset = offset + limit if offset + limit < len(matches) else None
        return SearchResult(
            "PARTIAL" if errors or visual_pending else "OK",
            matches[offset : offset + limit],
            errors,
            visual_pending,
            next_offset,
            len(matches),
        )

    def read_page_image(self, file_id: str, cutoff: datetime, page: int = 1) -> bytes:
        """Serial rendering only; callers must record any separate vision model usage."""
        import io

        from PIL import Image

        path, _ = self.path(file_id, cutoff)
        if page < 1:
            raise ValueError("page is one-based")
        if path.suffix.lower() == ".png" and page == 1:
            with Image.open(path) as im:
                output = io.BytesIO()
                im.save(output, format="PNG")
                return output.getvalue()
        if path.suffix.lower() != ".pdf":
            raise ValueError("image or PDF required")
        import pypdfium2 as pdfium

        with pdfium.PdfDocument(path) as doc:
            pdf_page = doc[page - 1]
            try:
                bitmap = pdf_page.render(scale=2)
                try:
                    output = io.BytesIO()
                    bitmap.to_pil().save(output, format="PNG")
                    return output.getvalue()
                finally:
                    bitmap.close()
            finally:
                pdf_page.close()


def search_payload(result: SearchResult) -> str:
    return json.dumps(asdict(result), default=lambda v: v.isoformat(), ensure_ascii=False)
