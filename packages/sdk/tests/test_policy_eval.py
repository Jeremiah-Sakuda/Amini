"""Tests for the SDK-side condition evaluator (mirrors backend policy_engine DSL)."""

from amini.policy import evaluate_condition, _resolve_field, _compare


# --- _resolve_field ---

def test_resolve_simple_field():
    assert _resolve_field("name", {"name": "alice"}) == "alice"


def test_resolve_dotted_field():
    ctx = {"kwargs": {"user": {"role": "admin"}}}
    assert _resolve_field("kwargs.user.role", ctx) == "admin"


def test_resolve_missing_field():
    assert _resolve_field("missing.path", {"other": 1}) is None


def test_resolve_non_dict_intermediate():
    assert _resolve_field("a.b", {"a": "string"}) is None


# --- _compare ---

def test_compare_equals():
    assert _compare(5, "equals", 5)
    assert not _compare(5, "equals", 3)


def test_compare_not_equals():
    assert _compare(5, "not_equals", 3)
    assert not _compare(5, "not_equals", 5)


def test_compare_greater_than():
    assert _compare(10, "greater_than", 5)
    assert not _compare(3, "greater_than", 5)


def test_compare_less_than():
    assert _compare(3, "less_than", 5)
    assert not _compare(10, "less_than", 5)


def test_compare_gte():
    assert _compare(5, "greater_than_or_equal", 5)
    assert _compare(6, "greater_than_or_equal", 5)
    assert not _compare(4, "greater_than_or_equal", 5)


def test_compare_lte():
    assert _compare(5, "less_than_or_equal", 5)
    assert _compare(4, "less_than_or_equal", 5)
    assert not _compare(6, "less_than_or_equal", 5)


def test_compare_contains():
    assert _compare("hello world", "contains", "world")
    assert not _compare("hello", "contains", "xyz")


def test_compare_not_contains():
    assert _compare("hello", "not_contains", "xyz")
    assert not _compare("hello world", "not_contains", "world")


def test_compare_matches_regex():
    assert _compare("test@example.com", "matches_regex", r"@example\.com$")
    assert not _compare("test@other.com", "matches_regex", r"@example\.com$")


def test_compare_in_list():
    assert _compare("admin", "in_list", ["admin", "superadmin"])
    assert not _compare("user", "in_list", ["admin", "superadmin"])


def test_compare_not_in_list():
    assert _compare("user", "not_in_list", ["admin", "superadmin"])
    assert not _compare("admin", "not_in_list", ["admin", "superadmin"])


def test_compare_none_returns_false():
    assert not _compare(None, "equals", "anything")


def test_compare_unknown_operator():
    assert not _compare(5, "unknown_op", 5)


# --- evaluate_condition ---

def test_simple_condition():
    cond = {"field": "action", "operator": "equals", "value": "delete"}
    assert evaluate_condition(cond, {"action": "delete"})
    assert not evaluate_condition(cond, {"action": "read"})


def test_and_condition():
    cond = {
        "and": [
            {"field": "role", "operator": "equals", "value": "admin"},
            {"field": "level", "operator": "greater_than", "value": 5},
        ]
    }
    assert evaluate_condition(cond, {"role": "admin", "level": 10})
    assert not evaluate_condition(cond, {"role": "admin", "level": 3})
    assert not evaluate_condition(cond, {"role": "user", "level": 10})


def test_or_condition():
    cond = {
        "or": [
            {"field": "role", "operator": "equals", "value": "admin"},
            {"field": "role", "operator": "equals", "value": "superadmin"},
        ]
    }
    assert evaluate_condition(cond, {"role": "admin"})
    assert evaluate_condition(cond, {"role": "superadmin"})
    assert not evaluate_condition(cond, {"role": "user"})


def test_not_condition():
    cond = {"not": {"field": "approved", "operator": "equals", "value": True}}
    assert not evaluate_condition(cond, {"approved": True})
    assert evaluate_condition(cond, {"approved": False})


def test_nested_and_or():
    cond = {
        "and": [
            {"field": "env", "operator": "equals", "value": "production"},
            {
                "or": [
                    {"field": "action", "operator": "equals", "value": "delete"},
                    {"field": "action", "operator": "equals", "value": "drop"},
                ]
            },
        ]
    }
    assert evaluate_condition(cond, {"env": "production", "action": "delete"})
    assert evaluate_condition(cond, {"env": "production", "action": "drop"})
    assert not evaluate_condition(cond, {"env": "staging", "action": "delete"})
    assert not evaluate_condition(cond, {"env": "production", "action": "read"})


def test_empty_condition_passes():
    assert evaluate_condition({}, {})


def test_dotted_field_in_condition():
    cond = {"field": "kwargs.amount", "operator": "greater_than", "value": 1000}
    assert evaluate_condition(cond, {"kwargs": {"amount": 5000}})
    assert not evaluate_condition(cond, {"kwargs": {"amount": 500}})
