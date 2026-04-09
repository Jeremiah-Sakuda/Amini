"""Amini Demo Agent — Multi-Scenario Showcase.

Exercises every major SDK feature and populates the dashboard with
realistic data when run against a live backend.

Usage:
    make demo          (from repo root)
    poetry run python -m scripts.demo_agent   (from packages/sdk)
"""

from __future__ import annotations

import time

from amini import Amini, PolicyRule, PolicyTier, PolicyEnforcement, PolicySeverity, PolicyViolationError

# ---------------------------------------------------------------------------
# Client setup
# ---------------------------------------------------------------------------
amini = Amini(
    api_key="dev-key",
    agent_id="demo-support-agent",
    environment="development",
    regulations=["eu-ai-act", "soc2"],
)

SEPARATOR = "\n" + "=" * 50


def _header(scenario: int, total: int, title: str) -> None:
    print(f"\n[Scenario {scenario}/{total}] {title}")


# ---------------------------------------------------------------------------
# Scenario 1 — Happy path: customer lookup & resolution
# ---------------------------------------------------------------------------

@amini.trace
def lookup_customer(customer_id: str) -> dict:
    """Simulate a CRM lookup."""
    return {
        "customer_id": customer_id,
        "name": "Alice Johnson",
        "tier": "premium",
        "account_status": "active",
    }


def scenario_happy_path() -> None:
    _header(1, 4, "Happy Path: Customer Lookup & Resolution")

    print("  Starting session...")
    amini.start_session(user_context={"user_id": "u-1001", "channel": "chat"})

    print("  Looking up customer C-1001...")
    customer = lookup_customer(customer_id="C-1001")

    print("  Resolving ticket T-4521...")
    with amini.decision("resolve-ticket") as ctx:
        ctx.log_input({"ticket_id": "T-4521", "issue": "billing discrepancy"})
        ctx.log_reasoning({"strategy": "check_recent_invoices", "confidence": 0.92})
        ctx.log_action("database_query", {"table": "invoices", "filter": "last_30_days"})
        ctx.log_output({
            "resolution": "credited $12.50",
            "status": "resolved",
            "customer": customer["name"],
        })

    amini.end_session(status="completed")
    print("  Session completed.")


# ---------------------------------------------------------------------------
# Scenario 2 — Policy warning: refund amount threshold
# ---------------------------------------------------------------------------

def scenario_policy_warning() -> None:
    _header(2, 4, "Policy Warning: High-Value Refund")

    print("  Registering max-refund-amount policy (WARN)...")
    amini.register_policy(PolicyRule(
        name="max-refund-amount",
        tier=PolicyTier.DETERMINISTIC,
        enforcement=PolicyEnforcement.WARN,
        severity=PolicySeverity.HIGH,
        conditions={"field": "kwargs.amount", "operator": "greater_than", "value": 500},
    ))

    @amini.enforce("max-refund-amount")
    def process_refund(amount: float, reason: str) -> dict:
        return {"amount": amount, "reason": reason, "status": "processed"}

    print("  Starting session...")
    amini.start_session(user_context={"user_id": "u-2045", "channel": "phone"})

    print("  Processing $750.00 refund...")
    result = process_refund(amount=750.00, reason="duplicate charge")
    print("  [!] Policy warning: max-refund-amount triggered (amount > $500)")
    print("  Refund processed (with warning logged).")

    amini.end_session(status="completed")
    print("  Session completed.")


# ---------------------------------------------------------------------------
# Scenario 3 — Blocked action: PII in external call
# ---------------------------------------------------------------------------

def scenario_pii_block() -> None:
    _header(3, 4, "Blocked Action: PII Protection")

    print("  Registering pii-external-block policy (BLOCK)...")
    amini.register_policy(PolicyRule(
        name="pii-external-block",
        tier=PolicyTier.DETERMINISTIC,
        enforcement=PolicyEnforcement.BLOCK,
        severity=PolicySeverity.CRITICAL,
        regulation="eu-ai-act",
        conditions={
            "and": [
                {"field": "kwargs.action_type", "operator": "equals", "value": "external_api_call"},
                {"field": "kwargs.payload", "operator": "matches_regex", "value": r"\b\d{3}-\d{2}-\d{4}\b"},
            ]
        },
    ))

    @amini.enforce("pii-external-block")
    def send_to_external(action_type: str, payload: str) -> dict:
        return {"sent": True, "payload_length": len(payload)}

    print("  Starting session...")
    amini.start_session(user_context={"user_id": "u-3100", "channel": "api"})

    print("  Attempting external API call with PII data...")
    try:
        send_to_external(
            action_type="external_api_call",
            payload="Customer SSN: 123-45-6789, account balance: $4,200",
        )
    except PolicyViolationError:
        print("  [X] BLOCKED: pii-external-block -- cannot send SSN to external service")

    amini.end_session(status="completed")
    print("  Session completed.")


# ---------------------------------------------------------------------------
# Scenario 4 — Error handling: service failure
# ---------------------------------------------------------------------------

@amini.trace
def analyze_sentiment(text: str) -> dict:
    """Simulate calling an NLP service that is down."""
    raise RuntimeError("NLP service unavailable")


def scenario_error_handling() -> None:
    _header(4, 4, "Error Handling: Service Failure")

    print("  Starting session...")
    amini.start_session(user_context={"user_id": "u-4200", "channel": "chat"})

    print("  Analyzing sentiment...")
    try:
        analyze_sentiment(text="I'm very frustrated with my last bill")
    except RuntimeError as exc:
        print(f"  [X] Error captured: {exc}")

    amini.end_session(status="error", reason="Unhandled exception in agent")
    print("  Session ended with error status.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(SEPARATOR)
    print("  Amini Demo Agent -- Multi-Scenario Showcase")
    print("=" * 50)

    scenario_happy_path()
    time.sleep(1)

    scenario_policy_warning()
    time.sleep(1)

    scenario_pii_block()
    time.sleep(1)

    scenario_error_handling()

    # Cleanup
    amini.flush()
    time.sleep(2)
    amini.shutdown()

    print(SEPARATOR)
    print("  Demo complete! 4 sessions created.")
    print("  View results: http://localhost:5173/sessions")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
