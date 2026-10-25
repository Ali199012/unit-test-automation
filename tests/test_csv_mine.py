import ast
import csv
from pathlib import Path

import pytest
from cachetools import LRUCache
from cachetools.func import lru_cache, ttl_cache
from cachetools.keys import hashkey, typedkey

DATA = Path(__file__).parent / "data"


def read_rows(filename):
    with open(DATA / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def row_id(row):
    return row["id"]


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


@pytest.mark.parametrize("row", read_rows("lru_cases.csv"), ids=row_id)
def test_lru_inserts_from_csv(row):
    c = LRUCache(maxsize=int(row["maxsize"]))
    for key in row["inserts"].split():
        c[key] = 1
    assert sorted(c) == sorted(row["expected_keys"].split())
    assert c.currsize == int(row["expected_size"])


@pytest.mark.parametrize("row", read_rows("keys_cases.csv"), ids=row_id)
def test_key_equality_from_csv(row):
    make_key = {"hashkey": hashkey, "typedkey": typedkey}[row["func"]]
    args1 = ast.literal_eval(row["args1"])
    args2 = ast.literal_eval(row["args2"])
    assert (make_key(*args1) == make_key(*args2)) == (row["expected_equal"] == "True")


@pytest.mark.parametrize("row", read_rows("func_cases.csv"), ids=row_id)
def test_lru_cache_counts_from_csv(row):
    wrapped = lru_cache(maxsize=int(row["maxsize"]))(lambda x: x)
    for x in row["calls"].split():
        wrapped(int(x))
    info = wrapped.cache_info()
    assert info.hits == int(row["expected_hits"])
    assert info.misses == int(row["expected_misses"])
    assert info.currsize == int(row["expected_currsize"])


@pytest.mark.parametrize("row", read_rows("ttl_cases.csv"), ids=row_id)
def test_ttl_expiry_from_csv(row):
    clock = Clock()
    cached = ttl_cache(maxsize=2, ttl=int(row["ttl"]), timer=clock)(lambda x: x)
    for t in row["times"].split():
        clock.now = int(t)
        cached(1)
    info = cached.cache_info()
    assert info.hits == int(row["expected_hits"])
    assert info.misses == int(row["expected_misses"])
