"""Sequential request triage, evidence investigation, grounded validation and assembly."""

import json
from dataclasses import asdict
from pathlib import Path

from .agent import AuditContext, run_task, task_definitions
from .budget import Budget
from .data import Dataset, Identity
from .evidence import EvidenceStore
from .grounding import literal_fields, validate_proposal
from .identity import resolve_identity
from .models import AuditError, Authorization, Request
from .prompts import VERSION
from .resource_links import resource_aliases
from .triage_batch import triage_key
from .usage import UsageEntry, UsageLedger
from .workflow import assemble


def discover(store: EvidenceStore, identity: Identity, request: Request) -> tuple[dict, list, list]:
    """Search aliases, then exact trace/resource links; no ownership inference here."""
    # Exact names are discovery candidates, never sufficient ownership proof on their own.
    identifiers = {a.value for a in identity.aliases}
    sources, errors, visual = {}, set(), set()
    frontier = identifiers
    for _ in range(4):
        if not frontier:
            break
        if len(frontier) > 256:
            errors.add("DISCOVERY_IDENTIFIER_LIMIT")
            break
        offset = 0
        discovered = set()
        while True:
            result = store.search(sorted(frontier), request.audit_at, offset, 100)
            errors.update(result.errors)
            visual.update(result.visual_pending)
            for f in result.fragments:
                sources[(f.evidence_id, f.locator)] = f
                fields = literal_fields(f)
                discovered.update(
                    v
                    for k, v in fields.items()
                    if k in {"resource_id", "parent_resource_id", "trace_id"} and v
                )
            if result.next_offset is None:
                break
            offset = result.next_offset
        frontier = discovered - identifiers
        identifiers.update(discovered)
    else:
        if frontier:
            errors.add("DISCOVERY_DEPTH_LIMIT")
    return sources, sorted(errors), sorted(visual)


async def audit_request(
    request: Request,
    dataset: Dataset,
    store: EvidenceStore,
    model: str,
    budget: Budget,
    ledger: UsageLedger,
    run_dir: Path,
    *,
    candidate: bool = False,
    readbacks_only: bool = False,
    proposal_run: Path | None = None,
):
    triage, audit = task_definitions(model)
    key = triage_key(request, model)
    cache = run_dir.parent / "triage-cache" / (key + ".json")
    if cache.exists():
        authorization = Authorization.model_validate_json(cache.read_text())
        ledger.record(
            UsageEntry("OpenAI", model, request.case_id, "triage_cache", 0, 0, 0, "CACHE_HIT")
        )
    else:
        authorization = await run_task(
            triage,
            request.request_text,
            case_id=request.case_id,
            stage="triage",
            budget=budget,
            ledger=ledger,
            max_turns=1,
        )
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(authorization.model_dump_json(), encoding="utf-8")
    if not authorization.request_spans or any(
        span not in request.request_text for span in authorization.request_spans
    ):
        raise AuditError("UNSUPPORTED_INTENT_SPAN")
    if authorization.intent == "NON_DELETION":
        return assemble(request, authorization)
    if authorization.intent == "UNRESOLVED":
        raise AuditError("UNRESOLVED_INTENT")
    identity = resolve_identity(dataset, store, request)
    sources, errors, visuals = discover(store, identity, request)
    aliases = resource_aliases(dataset, request, identity)
    related_ids = {
        v
        for f in sources.values()
        for k, v in literal_fields(f).items()
        if k in {"resource_id", "parent_resource_id"} and v
    }
    relevant_aliases = {key: values for key, values in aliases.items() if key in related_ids}
    for values in relevant_aliases.values():
        for alias in values:
            offset = 0
            while True:
                found = store.search([alias["value"]], request.audit_at, offset, 100)
                for f in found.fragments:
                    sources[f.evidence_id, f.locator] = f
                if found.next_offset is None:
                    break
                offset = found.next_offset
    for file_id in {f.evidence_id for f in list(sources.values()) if f.locator.startswith("sql:")}:
        for f in store.read(file_id, request.audit_at):
            if f.locator.endswith("/scope"):
                sources[(f.evidence_id, f.locator)] = f
    allowed = {a.value for a in identity.aliases}
    allowed.update(
        v
        for f in sources.values()
        for k, v in literal_fields(f).items()
        if k in {"resource_id", "parent_resource_id", "trace_id"} and v
    )
    allowed.update(a["value"] for values in relevant_aliases.values() for a in values)
    context = AuditContext(store, request.audit_at, sources, allowed)
    payload = {
        "request": request.model_dump(mode="json"),
        "identity": identity.model_dump(mode="json"),
        "rules": dataset.rules,
        "resource_aliases": relevant_aliases,
        "discovery_errors": errors,
        "visual_pending": visuals,
        "discovery_scope": "Every admissible participant artifact and activity row was searched "
        "for all supplied identity aliases, followed by exact discovered resource/trace IDs. "
        "Search pagination was exhausted. Only explicit linked new identifiers warrant expansion.",
        "seed_fragments": [
            {**asdict(f), "extracted_fields": literal_fields(f)} for f in sources.values()
        ],
    }
    prompt = json.dumps(payload, default=str, ensure_ascii=False)
    run_dir.mkdir(parents=True, exist_ok=True)
    if (errors or visuals) and not candidate:
        raise AuditError("UNRESOLVED_SOURCE_COVERAGE")
    if readbacks_only:
        from .agent import AuditProposal
        from .candidate import candidate_from_proposal
        from .readback_candidate import propose_readbacks

        proposal = propose_readbacks(identity, sources, dataset.rules)
        origin = "literal_readbacks"
        result, diagnostic = candidate_from_proposal(
            proposal, request, authorization, identity, dataset, sources
        )
        if proposal_run:
            paths = sorted(proposal_run.glob(f"{request.case_id}-proposal-*.json"))
            if paths:
                saved = json.loads(paths[-1].read_text())
                raw = saved["proposal"]
                # Rebind source receipts to the same currently retrieved fragments.
                # Values/states/conditions are still independently validated below.
                for field in ("links", "observations", "dependencies"):
                    for item in raw["assessment"][field]:
                        ref = item["source"]
                        fragment = sources.get((ref["evidence_id"], ref["locator"]))
                        if fragment is not None and fragment.observed_at is not None:
                            ref.update(
                                captured_at=fragment.captured_at.isoformat(),
                                observed_at=fragment.observed_at.isoformat(),
                                time_precision="EXACT",
                            )
                proposal = AuditProposal.model_validate_json(json.dumps(raw))
                replay, replay_diagnostic = candidate_from_proposal(
                    proposal, request, authorization, identity, dataset, sources
                )
                if replay_diagnostic["evidence_validated"] or len(replay.steps) > len(result.steps):
                    result, diagnostic = replay, replay_diagnostic
                    origin = "revalidated_saved_model_proposal"
                else:
                    diagnostic["diagnostics"].extend(replay_diagnostic["diagnostics"])
        diagnostic["proposal_origin"] = origin
        diagnostic["diagnostics"].extend(errors + ["VISUAL_PENDING:" + v for v in visuals])
        if errors or visuals:
            diagnostic["evidence_validated"] = False
            if result.deletion_status == "COMPLETE":
                from .candidate import unsupported_candidate

                result, _ = unsupported_candidate(request.case_id, "UNRESOLVED_SOURCE_COVERAGE")
        return result, diagnostic
    for attempt in range(1 if candidate else 2):
        proposal = await run_task(
            audit,
            prompt,
            case_id=request.case_id,
            stage="audit" if attempt == 0 else "audit_repair",
            budget=budget,
            ledger=ledger,
            context=context,
            max_turns=8,
        )
        (run_dir / f"{request.case_id}-proposal-{attempt}.json").write_text(
            json.dumps(
                {
                    "prompt_version": VERSION,
                    "authorization": authorization.model_dump(mode="json"),
                    "proposal": proposal.model_dump(mode="json"),
                    "accessed": [[a, b] for a, b in sorted(sources)],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        if candidate:
            from .candidate import candidate_from_proposal

            result, diagnostic = candidate_from_proposal(
                proposal, request, authorization, identity, dataset, sources
            )
            if errors or visuals:
                diagnostic["evidence_validated"] = False
                diagnostic["diagnostics"].extend(errors + ["VISUAL_PENDING:" + v for v in visuals])
                if result.deletion_status == "COMPLETE":
                    from .candidate import unsupported_candidate

                    result, fallback = unsupported_candidate(
                        request.case_id, "UNRESOLVED_SOURCE_COVERAGE"
                    )
                    diagnostic["fallback"] = fallback["fallback"]
            return result, diagnostic
        try:
            assessment = validate_proposal(proposal, request, identity, dataset, sources)
            return assemble(request, authorization, assessment)
        except AuditError as exc:
            # Evidence/coverage gaps cannot be fixed by asking for a more convenient answer.
            if attempt or str(exc) in {
                "INCOMPLETE_EVIDENCE_COVERAGE",
                "UNRESOLVED_IDENTITY",
                "UNKNOWN_OBSERVATION_TIME",
                "UNREPRESENTABLE_OBLIGATION",
                "ORDER_CONFLICT",
            }:
                raise
            prompt = json.dumps(
                {
                    "original_context": payload,
                    "previous_proposal": proposal.model_dump(mode="json"),
                    "validation_error": str(exc),
                    "instruction": "Correct only with retrieved evidence. If no "
                    "supported correction exists, mark coverage incomplete with a gap. "
                    "Do not invent fields, identifiers, times, categories or sources.",
                },
                default=str,
                ensure_ascii=False,
            )
