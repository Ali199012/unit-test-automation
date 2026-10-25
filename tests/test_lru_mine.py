"""Unit tests for cachetools.LRUCache.

Design notes are in docs/notes_lru.md (ECP + BVA).
Sections: __setitem__, __getitem__, popitem, class level.
"""
import pytest
from cachetools import LRUCache


def make_full_cache(maxsize=3):
    """Cache filled to the limit with keys 'a', 'b', 'c', ... (a is oldest)."""
    c = LRUCache(maxsize=maxsize)
    for i in range(maxsize):
        c[chr(ord("a") + i)] = i
    return c


# ---------------------------------------------------------------- __setitem__

@pytest.mark.parametrize("key", ["a", 1, (1, 2), 3.5, None])
def test_setitem_valid_key_types(key):  # ECP: valid hashable keys
    c = LRUCache(maxsize=3)
    c[key] = "v"
    assert c[key] == "v"


def test_setitem_into_empty_cache_sets_size_one():  # BVA: 0 -> 1
    c = LRUCache(maxsize=3)
    c["a"] = 1
    assert c.currsize == 1


def test_setitem_up_to_limit_evicts_nothing():  # BVA: size == maxsize
    c = make_full_cache(3)
    assert c.currsize == 3
    assert set(c) == {"a", "b", "c"}


def test_setitem_past_limit_evicts_oldest():  # BVA: maxsize + 1
    c = make_full_cache(3)
    c["d"] = 99
    assert "a" not in c
    assert set(c) == {"b", "c", "d"}
    assert c.currsize == 3


def test_setitem_overwrite_keeps_size_and_updates_value():  # ECP: existing key
    c = make_full_cache(3)
    c["b"] = "new"
    assert c["b"] == "new"
    assert c.currsize == 3


def test_setitem_overwrite_counts_as_recent_use():
    c = make_full_cache(3)
    c["a"] = "refreshed"  # a was oldest, now newest
    c["d"] = 99           # should evict b, not a
    assert "a" in c
    assert "b" not in c


def test_setitem_unhashable_key_raises_typeerror():  # ECP: invalid key
    c = LRUCache(maxsize=3)
    with pytest.raises(TypeError):
        c[["list"]] = 1


def test_setitem_maxsize_zero_raises_valueerror():  # BVA: maxsize 0
    c = LRUCache(maxsize=0)
    with pytest.raises(ValueError):
        c["a"] = 1


# ---------------------------------------------------------------- __getitem__

def test_getitem_existing_key_returns_value():  # ECP
    c = make_full_cache(3)
    assert c["b"] == 1


@pytest.mark.parametrize("missing", ["zzz", 999, (0, 0)])
def test_getitem_missing_key_raises_keyerror(missing):  # ECP
    c = make_full_cache(3)
    with pytest.raises(KeyError):
        c[missing]


def test_getitem_on_single_item_cache():  # BVA: exactly 1 item
    c = LRUCache(maxsize=1)
    c["only"] = 42
    assert c["only"] == 42


def test_getitem_oldest_and_newest_keys_in_full_cache():  # BVA: both ends
    c = make_full_cache(3)
    assert c["a"] == 0  # oldest
    assert c["c"] == 2  # newest


def test_getitem_marks_key_as_recently_used():
    c = make_full_cache(3)
    c["a"]            # read oldest, so b becomes the oldest
    c["d"] = 99       # evicts b
    assert "a" in c
    assert "b" not in c


def test_getitem_evicted_key_raises_keyerror():
    c = make_full_cache(3)
    c["d"] = 99       # evicts a
    with pytest.raises(KeyError):
        c["a"]


# ------------------------------------------------------------------- popitem

def test_popitem_returns_least_recently_used():  # ECP: non-empty
    c = make_full_cache(3)
    assert c.popitem() == ("a", 0)


def test_popitem_removes_the_item():
    c = make_full_cache(3)
    c.popitem()
    assert "a" not in c
    assert c.currsize == 2


def test_popitem_on_empty_cache_raises_keyerror():  # ECP: empty
    c = LRUCache(maxsize=3)
    with pytest.raises(KeyError):
        c.popitem()


def test_popitem_single_item_empties_cache():  # BVA: exactly 1 item
    c = LRUCache(maxsize=3)
    c["x"] = 7
    assert c.popitem() == ("x", 7)
    assert len(c) == 0


def test_popitem_respects_recent_reads():
    c = make_full_cache(3)
    c["a"]            # a is now newest, b is oldest
    assert c.popitem() == ("b", 1)


def test_popitem_repeated_until_empty_then_raises():  # BVA: drain the cache
    c = make_full_cache(3)
    assert [c.popitem()[0] for _ in range(3)] == ["a", "b", "c"]
    with pytest.raises(KeyError):
        c.popitem()


# --------------------------------------------------------------- class level

@pytest.mark.parametrize("maxsize", [1, 2, 5])
def test_cache_never_exceeds_maxsize(maxsize):  # BVA: maxsize 1, 2, 5
    c = LRUCache(maxsize=maxsize)
    for i in range(maxsize + 3):
        c[i] = i
    assert c.currsize == maxsize
    assert len(c) == maxsize


@pytest.mark.parametrize("maxsize", [1, 2, 5])
def test_cache_keeps_newest_items(maxsize):
    c = LRUCache(maxsize=maxsize)
    total = maxsize + 3
    for i in range(total):
        c[i] = i
    assert set(c) == set(range(total - maxsize, total))


def test_maxsize_property():
    assert LRUCache(maxsize=4).maxsize == 4


def test_currsize_starts_at_zero():
    assert LRUCache(maxsize=4).currsize == 0


def test_len_matches_number_of_items():
    c = LRUCache(maxsize=4)
    c["a"] = 1
    c["b"] = 2
    assert len(c) == 2


def test_contains_true_and_false():
    c = LRUCache(maxsize=4)
    c["a"] = 1
    assert "a" in c
    assert "b" not in c


def test_eviction_order_after_mixed_reads_and_writes():
    c = LRUCache(maxsize=2)
    c["a"] = 1
    c["b"] = 2
    c["a"]            # a newest
    c["c"] = 3        # evicts b
    c["d"] = 4        # evicts a
    assert list(c) == ["c", "d"]


def test_clear_empties_cache():
    c = make_full_cache(3)
    c.clear()
    assert c.currsize == 0
    assert len(c) == 0


def test_pop_removes_specific_key():
    c = make_full_cache(3)
    assert c.pop("b") == 1
    assert "b" not in c


def test_pop_missing_key_raises_keyerror():
    c = make_full_cache(3)
    with pytest.raises(KeyError):
        c.pop("zzz")
