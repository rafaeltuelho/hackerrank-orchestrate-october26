import asyncio
from decimal import Decimal

import pytest
from agents import ModelSettings
from ghost_audit.budget import Budget, BudgetedModel, upper_cost
from ghost_audit.models import AuditError
from test_sdk import OfflineModel


def test_persistent_reservation_and_unknown_failure(tmp_path):
    path = tmp_path / "budget.jsonl"
    b = Budget(path, Decimal("1"))
    call = b.reserve(100, 20)
    reserved = b.committed
    assert Budget(path, Decimal("1")).committed == reserved
    b.settle(call, 10, 5)
    assert b.committed == upper_cost(10, 5) < reserved
    assert Budget(path, Decimal("1")).committed == b.committed
    with pytest.raises(AuditError, match="BUDGET_EXHAUSTED"):
        b.reserve(922000, 6000)


def test_live_wrapper_reserves_before_call_and_settles(tmp_path):
    budget = Budget(tmp_path / "budget.jsonl", Decimal("1"))
    model = BudgetedModel(OfflineModel("{}"), budget)
    asyncio.run(
        model.get_response("test", "test", ModelSettings(max_tokens=100), [], None, [], None)
    )
    assert budget.committed == upper_cost(11, 7)
    assert not budget.pending


def test_live_wrapper_failure_keeps_reservation(tmp_path):
    budget = Budget(tmp_path / "budget.jsonl", Decimal("1"))
    model = BudgetedModel(OfflineModel(failure=True), budget)
    with pytest.raises(RuntimeError):
        asyncio.run(
            model.get_response("test", "test", ModelSettings(max_tokens=100), [], None, [], None)
        )
    assert budget.pending and budget.committed > 0


def test_no_request_when_unaffordable(tmp_path):
    budget = Budget(tmp_path / "budget.jsonl", Decimal("0.001"))
    model = BudgetedModel(OfflineModel(failure=True), budget)
    with pytest.raises(AuditError, match="BUDGET_EXHAUSTED"):
        asyncio.run(
            model.get_response("test", "test", ModelSettings(max_tokens=100), [], None, [], None)
        )
    assert not budget.pending


def test_independent_instances_share_ceiling_and_bad_settlement_cannot_corrupt(tmp_path):
    path = tmp_path / "budget.jsonl"
    first = Budget(path, Decimal("0.01"))
    second = Budget(path, Decimal("0.01"))
    call = first.reserve(1000, 100)
    with pytest.raises(AuditError, match="BUDGET_EXHAUSTED"):
        second.reserve(1000, 100)
    before = path.read_bytes()
    with pytest.raises(AuditError, match="INVALID_BUDGET_SETTLEMENT"):
        first.settle(call, 100000, 100000)
    assert path.read_bytes() == before
    assert Budget(path, Decimal("0.01")).committed == first.committed
