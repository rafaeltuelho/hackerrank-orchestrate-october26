import asyncio
import importlib.util
import json
from types import SimpleNamespace

from evaluation.custom_cases import fixtures
from ghost_audit.data import ROOT
from ghost_audit.models import AuditError


def test_candidate_batch_continues_after_semantic_failure(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("entrypoint", ROOT / "code/main.py")
    entrypoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(entrypoint)
    cases = fixtures()
    processed = []

    async def fake_audit(request, *args, **kwargs):
        processed.append(request.case_id)
        if request.case_id == cases[1].request.case_id:
            raise AuditError("UNRESOLVED_POLICY_CONDITION")
        return next(c.expected for c in cases if c.request.case_id == request.case_id)

    monkeypatch.setattr(entrypoint, "audit_request", fake_audit)
    args = SimpleNamespace(
        dataset=ROOT / "dataset",
        run_dir=tmp_path / "run",
        output=tmp_path / "candidate.csv",
        candidate=True,
        batch_triage=False,
        skip_vision=True,
        readbacks_only=False,
        proposal_run=None,
    )
    asyncio.run(entrypoint.run([c.request for c in cases], args))
    assert processed == [c.request.case_id for c in cases]
    summary = json.loads((args.run_dir / "summary.json").read_text())
    assert summary["complete"] and not summary["fully_evidence_validated"]
    assert summary["evidence_validated_cases"] == 2
    diagnostics = json.loads((args.run_dir / "diagnostics.json").read_text())
    assert diagnostics[1]["diagnostics"] == ["UNRESOLVED_POLICY_CONDITION"]
    assert args.output.exists()


def test_usage_restart_retains_prior_measured_calls_without_appending_twice(tmp_path):
    from ghost_audit.usage import UsageEntry, UsageLedger

    path = tmp_path / "usage.jsonl"
    first = UsageLedger(path)
    first.record(UsageEntry("OpenAI", "offline-fixture", "case", "triage", 1, 10, 2, "COMPLETED"))
    second = UsageLedger(path)
    assert second.totals()["requests"] == 1
    assert second.totals()["known_input_tokens"] == 10
    assert len(path.read_text().splitlines()) == 1
