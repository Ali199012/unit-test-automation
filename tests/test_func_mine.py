import pytest
from cachetools import func
from cachetools.func import lru_cache, ttl_cache


def make_lru(maxsize=2, typed=False):
    calls = []

    @lru_cache(maxsize=maxsize, typed=typed)
    def double(x):
        calls.append(x)
        return x * 2

    return double, calls


class Clock:
    # A fake clock, so TTL tests do not have to wait.
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


def make_ttl(ttl=10, maxsize=2):
    clock = Clock()
    calls = []

    @ttl_cache(maxsize=maxsize, ttl=ttl, timer=clock)
    def ident(x):
        calls.append(x)
        return x

    return ident, clock, calls


# ---------------------------------------------------------------- lru_cache

def test_lru_cache_repeat_call_is_a_hit():
    f, calls = make_lru()
    f(1)
    f(1)
    assert calls == [1]


def test_lru_cache_info_counts_hits_and_misses():
    f, calls = make_lru(maxsize=2)
    for x in (1, 1, 2, 3, 1):
        f(x)
    info = f.cache_info()
    assert (info.hits, info.misses, info.maxsize, info.currsize) == (1, 4, 2, 2)


def test_lru_cache_evicted_value_is_recomputed():
    f, calls = make_lru(maxsize=2)
    for x in (1, 2, 3, 1):
        f(x)
    assert calls == [1, 2, 3, 1]


def test_lru_cache_clear_resets_counters():
    f, calls = make_lru()
    f(1)
    f(1)
    f.cache_clear()
    info = f.cache_info()
    assert (info.hits, info.misses, info.currsize) == (0, 0, 0)


def test_lru_cache_maxsize_zero_never_caches():
    f, calls = make_lru(maxsize=0)
    f(1)
    f(1)
    assert calls == [1, 1]
    assert f.cache_info().currsize == 0


def test_lru_cache_maxsize_none_is_unbounded():
    f, calls = make_lru(maxsize=None)
    for x in range(5):
        f(x)
    assert f.cache_info().currsize == 5


def test_lru_cache_untyped_treats_1_and_1_0_as_same():
    f, calls = make_lru(typed=False)
    f(1)
    f(1.0)
    assert len(calls) == 1


def test_lru_cache_typed_separates_1_and_1_0():
    f, calls = make_lru(maxsize=4, typed=True)
    f(1)
    f(1.0)
    assert len(calls) == 2


def test_lru_cache_unhashable_arg_raises_typeerror():
    f, calls = make_lru()
    with pytest.raises(TypeError):
        f([1])


def test_lru_cache_negative_maxsize_raises_valueerror():
    with pytest.raises(ValueError):
        lru_cache(maxsize=-1)(lambda x: x)


# ---------------------------------------------------------------- ttl_cache

def test_ttl_cache_first_call_is_a_miss():
    f, clock, calls = make_ttl()
    f(1)
    info = f.cache_info()
    assert (info.hits, info.misses) == (0, 1)


def test_ttl_cache_hit_before_expiry():
    f, clock, calls = make_ttl(ttl=10)
    f(1)
    clock.now = 9
    f(1)
    assert calls == [1]


def test_ttl_cache_expires_exactly_at_ttl():
    f, clock, calls = make_ttl(ttl=10)
    f(1)
    clock.now = 10
    f(1)
    assert calls == [1, 1]


def test_ttl_cache_hit_again_after_recompute():
    f, clock, calls = make_ttl(ttl=10)
    f(1)
    clock.now = 10
    f(1)
    clock.now = 11
    f(1)
    assert calls == [1, 1]


def test_ttl_cache_info_counts_over_time():
    f, clock, calls = make_ttl(ttl=10)
    for t in (0, 0, 9, 10, 11):
        clock.now = t
        f(1)
    info = f.cache_info()
    assert (info.hits, info.misses) == (3, 2)


def test_ttl_cache_clear_forces_recompute():
    f, clock, calls = make_ttl()
    f(1)
    f.cache_clear()
    f(1)
    assert calls == [1, 1]


# ------------------------------------------------------------- module level

def test_func_wrapper_keeps_function_name():
    f, calls = make_lru()
    assert f.__name__ == "double"


def test_func_wrapper_exposes_wrapped_function():
    f, calls = make_lru()
    assert hasattr(f, "__wrapped__")


def test_func_bare_decorator_defaults_to_maxsize_128():
    assert lru_cache(lambda x: x).cache_info().maxsize == 128


def test_func_cache_parameters_reports_settings():
    f, calls = make_lru(maxsize=2)
    params = f.cache_parameters()
    assert params["maxsize"] == 2
    assert params["typed"] is False


@pytest.mark.parametrize("name", ["lru_cache", "ttl_cache", "fifo_cache", "lfu_cache", "rr_cache"])
def test_func_module_exports_decorator(name):
    assert hasattr(func, name)
