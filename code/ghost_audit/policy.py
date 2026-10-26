"""Supplied policy lookup. Unknown/false conditions do not invent fallback actions."""

from .models import AuditError, Obligation


def validate_obligation(
    obligation: Obligation, rules: list[dict[str, str]], supported_conditions: set[str]
) -> None:
    if obligation.action in {"DISABLE", "BLOCK"}:
        required = "active_flow" if obligation.action == "DISABLE" else "restore_risk"
        if obligation.rule_id != required or required not in supported_conditions:
            raise AuditError("UNSUPPORTED_RISK_CONDITION")
        return
    matches = [
        r
        for r in rules
        if r["rule_id"] == obligation.rule_id
        and r["data_category"] == obligation.category
        and r["required_action"] == obligation.action
    ]
    if len(matches) != 1:
        raise AuditError("POLICY_RULE_MISMATCH")
    rule = matches[0]
    if rule["condition"] != "Always" and rule["rule_id"] not in supported_conditions:
        raise AuditError("UNRESOLVED_POLICY_CONDITION")
