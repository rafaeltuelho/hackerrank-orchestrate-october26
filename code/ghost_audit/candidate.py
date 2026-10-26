"""Best-supported candidates with an explicit, separate certification ledger.

Unknown conditions never select a treatment. An INCOMPLETE empty row is an
uncertified fallback required by the three-status output contract, not evidence
that a policy violation exists. Diagnostics preserve this distinction.
"""

import json

from .agent import AuditProposal
from .grounding import validate_proposal
from .models import AuditError, Result
from .output import canonical_steps, validate_result
from .workflow import assemble


def unsupported_candidate(case_id: str, code: str) -> tuple[Result, dict]:
    return Result(case_id=case_id, deletion_status="INCOMPLETE", steps=[]), {
        "case_id": case_id,
        "structurally_valid": True,
        "evidence_validated": False,
        "diagnostics": [code],
        "fallback": "INCOMPLETE with no asserted findings or invented remediation",
    }


def candidate_from_proposal(proposal, request, authorization, identity, dataset, sources):
    diagnostics = list(proposal.assessment.gaps)
    try:
        assessment = validate_proposal(proposal, request, identity, dataset, sources)
        result = assemble(request, authorization, assessment)
        return result, {
            "case_id": request.case_id,
            "structurally_valid": True,
            "evidence_validated": True,
            "diagnostics": [],
        }
    except AuditError as exc:
        diagnostics.append(str(exc))
    # Validate each treatment independently, preserving every ordinary evidence,
    # ownership, category, condition and time check. Only whole-case coverage is
    # deferred. This cannot certify the whole case or bypass an unknown condition.
    steps = []
    retained = set()
    for obligation in proposal.assessment.obligations:
        key = (obligation.system_id, obligation.resource_id)
        raw = proposal.model_dump(mode="json")
        a = raw["assessment"]
        a["obligations"] = [obligation.model_dump(mode="json")]
        for field in ("links", "observations"):
            a[field] = [v for v in a[field] if (v["system_id"], v["resource_id"]) == key]
        a["coverage_complete"], a["gaps"] = True, []
        raw["policy_support"] = [
            v
            for v in raw["policy_support"]
            if (v["system_id"], v["resource_id"], v["rule_id"]) == (*key, obligation.rule_id)
        ]
        try:
            piece = AuditProposal.model_validate_json(json.dumps(raw))
            assessment = validate_proposal(
                piece, request, identity, dataset, sources, require_coverage=False
            )
            result = assemble(request, authorization, assessment)
            steps.extend(result.steps)
            retained.add(key)
        except (AuditError, ValueError) as exc:
            diagnostics.append(f"{key[0]}/{key[1]}/{obligation.rule_id}: {exc}")
    # A dependency involving retained steps is still material. Do not publish a
    # potentially unsafe partial plan if dependency validation failed globally.
    if any("DEPENDENCY" in d or "ORDER_CONFLICT" in d for d in diagnostics):
        steps = []
    if not any(s.phase == "FINDING" for s in steps):
        steps = []  # no unsupported COMPLETE claim or invented violation
    unique = {(s.operation, s.system_id, s.resource_id): s for s in steps}
    steps = canonical_steps(
        [
            s.model_copy(update={"evidence_id": ""}) if s.phase == "VERIFICATION" else s
            for s in unique.values()
        ]
    )
    positions = {(s.system_id, s.resource_id): s.step_no for s in steps if s.phase == "REMEDIATION"}
    for dependency in proposal.assessment.dependencies:
        before = positions.get((dependency.before_system, dependency.before_resource))
        after = positions.get((dependency.after_system, dependency.after_resource))
        if before is not None and after is not None and before >= after:
            diagnostics.append("ORDER_CONFLICT")
            steps = []
            break
    result = Result(case_id=request.case_id, deletion_status="INCOMPLETE", steps=steps)
    validate_result(result, semantic=False)
    return result, {
        "case_id": request.case_id,
        "structurally_valid": True,
        "evidence_validated": False,
        "diagnostics": sorted(set(diagnostics)),
        "supported_resources": [list(k) for k in sorted(retained)],
        "fallback": None
        if steps
        else "INCOMPLETE with no asserted findings or invented remediation",
    }
