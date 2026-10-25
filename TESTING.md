# Unit test automation for cachetools (Assignment 3)

Solo submission. Project under test: cachetools (https://github.com/tkem/cachetools).
Setup video: docs/Setup.mp4

## Setup

    python -m venv .venv
    .venv\Scripts\activate
    pip install -e .
    pip install pytest pytest-xdist pytest-order pandas openpyxl

## Run the tests

    pytest                       all tests, in the configured order
    pytest -m lru                group: LRUCache tests
    pytest -m keys               group: cachetools.keys tests
    pytest -m func               group: cachetools.func tests
    pytest -m datadriven         group: tests that read CSV files
    pytest -m boundary           group: boundary value tests
    pytest -m negative           group: tests that expect an error
    pytest -m "keys or func"     two groups together
    pytest -n auto               run in parallel (pytest-xdist)
    pytest -n auto -m datadriven parallel and one group

## Layout

- tests/test_lru_mine.py     LRUCache: __setitem__, __getitem__, popitem, class level
- tests/test_keys_mine.py    keys.py: hashkey, typedkey, module level
- tests/test_func_mine.py    func.py: lru_cache, ttl_cache, module level
- tests/test_csv_mine.py     data-driven tests, data in tests/data/*.csv
- tests/conftest.py          groups (markers) and the execution order
- pytest.ini                 settings and registered markers
- docs/notes_*.md            ECP and BVA notes written before the tests
- docs/testcases.xlsx        test cases sheet (make_excel.py builds it from the CSV files)

## Execution order

Set in tests/conftest.py: LRU, then keys, then func, then CSV data-driven tests.
Inside a file, tests run in the order they are written. Parallel runs (-n auto)
may interleave tests, so use plain pytest when the order matters.

## Techniques

Equivalence class partitioning (ECP) and boundary value analysis (BVA), with
pytest.mark.parametrize for data-driven cases.

## AI assistance

An AI assistant (Claude) was used for guidance and to draft tests and notes.
All tests were run and checked by me.
