"""Tests for capsize_commons.sentinel."""

from capsize_commons.sentinel import UNSET, is_unset


def test_unset_is_falsy_and_distinct_from_none() -> None:
    assert not UNSET
    assert UNSET is not None
    assert repr(UNSET) == "UNSET"


def test_is_unset_only_matches_the_sentinel() -> None:
    assert is_unset(UNSET)
    assert not is_unset(None)
    assert not is_unset(0)
    assert not is_unset(False)
