"""Tests for the improved _safe_repr structured serialization."""

import dataclasses
from unittest.mock import MagicMock

from amini.client import _safe_repr


def test_primitives():
    assert _safe_repr(None) is None
    assert _safe_repr("hello") == "hello"
    assert _safe_repr(42) == 42
    assert _safe_repr(3.14) == 3.14
    assert _safe_repr(True) is True


def test_dict():
    assert _safe_repr({"a": 1, "b": [2, 3]}) == {"a": 1, "b": [2, 3]}


def test_list_and_tuple():
    assert _safe_repr([1, "two", 3]) == [1, "two", 3]
    assert _safe_repr((1, 2)) == [1, 2]  # tuples become lists


def test_dataclass():
    @dataclasses.dataclass
    class Point:
        x: int
        y: int

    result = _safe_repr(Point(x=1, y=2))
    assert result == {"x": 1, "y": 2}


def test_pydantic_v2_model():
    try:
        from pydantic import BaseModel
    except ImportError:
        return  # skip if pydantic not installed

    class User(BaseModel):
        name: str
        age: int

    result = _safe_repr(User(name="alice", age=30))
    assert result == {"name": "alice", "age": 30}


def test_object_with_dict():
    class Custom:
        def __init__(self):
            self.value = 42
            self.label = "test"

    result = _safe_repr(Custom())
    assert result == {"value": 42, "label": "test"}


def test_nested_complex_objects():
    @dataclasses.dataclass
    class Inner:
        val: int

    @dataclasses.dataclass
    class Outer:
        inner: Inner
        name: str

    result = _safe_repr(Outer(inner=Inner(val=99), name="top"))
    assert result == {"inner": {"val": 99}, "name": "top"}


def test_fallback_to_str():
    """Objects that don't support any structured serialization fall back to str()."""
    obj = MagicMock()
    obj.__class__.__name__ = "MockObj"
    # MagicMock has __dict__ so it should use that, but let's test the str fallback
    # by creating something truly opaque
    class Opaque:
        __slots__ = ()
        def __str__(self):
            return "opaque-value"
    # Opaque has no __dict__ because of __slots__, no model_dump, no dict, not a dataclass
    result = _safe_repr(Opaque())
    assert result == "opaque-value"
