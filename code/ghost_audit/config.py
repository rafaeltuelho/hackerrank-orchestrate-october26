"""Non-secret model selection; credentials remain environment-only."""

import os
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_MODEL = "gpt-6.1-sol"
TRIAGE_REASONING_EFFORT = "low"
AUDIT_REASONING_EFFORT = "medium"
VISION_REASONING_EFFORT = "medium"
# User-authorized total across pilot and full run, including retries/visual calls.
# Every live call uses the shared persistent reservation guard.
APPROVED_BUDGET_USD = Decimal("50.00")


def load_environment() -> None:
    load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False, interpolate=False)


def budget_limit_usd() -> Decimal:
    value = Decimal(os.environ.get("GHOST_BUDGET_USD", str(APPROVED_BUDGET_USD)))
    if not value.is_finite() or not Decimal("0") < value <= APPROVED_BUDGET_USD:
        raise ValueError("GHOST_BUDGET_USD must be positive and at most 50.00")
    return value


def model_id() -> str:
    value = os.environ.get("OPENAI_MODEL", DEFAULT_MODEL).strip()
    if not value:
        raise ValueError("OPENAI_MODEL must not be blank")
    return value
