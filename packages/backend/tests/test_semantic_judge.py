"""Tests for semantic policy evaluation with the judge hook."""

import pytest
from unittest.mock import MagicMock

from amini_server.models.policy import PolicyTier, PolicyVersion
from amini_server.services.policy_engine import (
    EvaluationResult,
    evaluate_session,
    register_semantic_judge,
    _semantic_judge,
)


def _make_session(status="active", environment="test"):
    session = MagicMock()
    session.status = status
    session.environment = environment
    session.agent_id = "test-agent"
    return session


def _make_semantic_policy(**kwargs):
    defaults = dict(
        id="pv-semantic-1",
        tier=PolicyTier.SEMANTIC,
        enforcement="warn",
        severity="medium",
        message="Semantic check",
        is_active=True,
        scope=None,
        parsed_rule={"prompt": "Is this output safe?"},
    )
    defaults.update(kwargs)
    pv = MagicMock(**defaults)
    pv.tier = defaults["tier"]
    pv.is_active = defaults["is_active"]
    return pv


def test_semantic_without_judge_returns_deferred():
    """When no judge is registered, semantic policies return deferred=True."""
    import amini_server.services.policy_engine as pe
    original = pe._semantic_judge
    pe._semantic_judge = None
    try:
        session = _make_session()
        pv = _make_semantic_policy()
        results = evaluate_session(session, [], [pv])
        assert len(results) == 1
        assert results[0].deferred is True
        assert results[0].violated is False
        assert "No semantic judge registered" in results[0].message
    finally:
        pe._semantic_judge = original


def test_semantic_with_judge_calls_it():
    """When a judge is registered, it is called for semantic policies."""
    import amini_server.services.policy_engine as pe
    original = pe._semantic_judge

    expected_result = EvaluationResult(
        violated=True,
        policy_version_id="pv-semantic-1",
        severity="high",
        message="LLM judge found a violation",
        evidence={"reason": "unsafe output detected"},
    )

    def mock_judge(pv, context):
        return expected_result

    pe._semantic_judge = mock_judge
    try:
        session = _make_session()
        pv = _make_semantic_policy()
        results = evaluate_session(session, [], [pv])
        assert len(results) == 1
        assert results[0].violated is True
        assert results[0].message == "LLM judge found a violation"
    finally:
        pe._semantic_judge = original


def test_semantic_judge_error_defers():
    """If the judge raises an exception, result is deferred gracefully."""
    import amini_server.services.policy_engine as pe
    original = pe._semantic_judge

    def broken_judge(pv, context):
        raise RuntimeError("LLM API timeout")

    pe._semantic_judge = broken_judge
    try:
        session = _make_session()
        pv = _make_semantic_policy()
        results = evaluate_session(session, [], [pv])
        assert len(results) == 1
        assert results[0].deferred is True
        assert results[0].violated is False
        assert "error" in results[0].message.lower() or "deferred" in results[0].message.lower()
    finally:
        pe._semantic_judge = original
